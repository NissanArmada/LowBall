from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from models.schemas import SupervisorSynthesis, NegotiationState, Message
from agents import unified
from core.dependencies import get_store, get_limiter
from services.store import SessionStore
from services.limiter import RateLimiter
from core.config import settings
import json
import asyncio
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/{session_id}")
async def chat_negotiation(
    websocket: WebSocket, 
    session_id: str,
    store: SessionStore = Depends(get_store),
    limiter: RateLimiter = Depends(get_limiter)
):
    # 1. Security Check
    token = websocket.headers.get("x-api-token")
    if not token:
        token = websocket.headers.get("X-API-Token")
        
    if token != settings.API_SECRET_TOKEN:
        logger.warning(f"Unauthorized access attempt with token: {token}")
        await websocket.accept()
        await websocket.send_text(json.dumps({"error": "Unauthorized"}))
        await websocket.close(code=1008)
        return

    await websocket.accept()
    
    try:
        while True:
            # 2. Rate Limit Check
            try:
                await limiter.check_rate_limit(token)
            except HTTPException as e:
                await websocket.send_text(json.dumps({"error": e.detail}))
                continue

            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON"}))
                continue

            user_text = message_data.get("user_message", "")

            # 3. Reload state from DB (picking up background updates)
            state = await store.load_state(session_id)
            if not state:
                 await websocket.send_text(json.dumps({"error": "Session expired or not found."}))
                 break

            state.history.append(Message(role="user", content=user_text))

            # 4. Unified Negotiation Agent (Single Call with Council-of-Thought)
            # This follows the optimized Unified Agent architecture.
            response: SupervisorSynthesis = await unified.get_negotiation_response(state)

            # 5. Update & Persist State
            state.history.append(Message(role="ai", content=response.final_response))
            state.current_lowball_price = response.suggested_next_price
            await store.save_state(state)

            # 6. Respond to Client
            await websocket.send_text(response.model_dump_json())

    except WebSocketDisconnect:
        logger.info(f"Client disconnected from session {session_id}")
    except Exception:
        logger.exception(f"Error in chat session {session_id}")
        if websocket.client_state.name != "DISCONNECTED":
            await websocket.close(code=1011)
