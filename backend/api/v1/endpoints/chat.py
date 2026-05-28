from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from models.schemas import SupervisorSynthesis, ChatResponse, Message
from agents import unified
from core.dependencies import get_store, get_limiter
from services.store import SessionStore
from services.limiter import RateLimiter
from core.config import settings
from typing import Optional
import json
import asyncio
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/{session_id}")
async def chat_negotiation(
    websocket: WebSocket, 
    session_id: str,
    token: Optional[str] = Query(None),
    store: SessionStore = Depends(get_store),
    limiter: RateLimiter = Depends(get_limiter)
):
    # 1. Security Check
    auth_token = token
    if not auth_token:
        auth_token = websocket.headers.get("x-api-token") or websocket.headers.get("X-API-Token")
        
    if auth_token != settings.API_SECRET_TOKEN:
        logger.warning(f"Unauthorized WebSocket access attempt. Session: {session_id}")
        await websocket.accept()
        await websocket.send_text(json.dumps({"error": "Unauthorized"}))
        await websocket.close(code=1008)
        return

    await websocket.accept()
    logger.info(f"WebSocket Connected: Session {session_id}")
    
    try:
        # --- INITIALIZATION PHASE ---
        # The greeting and research are handled by the background task in listing.py.
        # This socket simply watches the database and pushes updates.

        # --- DB WATCHER TASK ---
        # Watches for background updates (Greeting and Research Completion)
        async def watch_db():
            last_pushed_count = 0
            while True:
                s = await store.load_state(session_id)
                if not s:
                    break
                
                # Push new messages (like the greeting) if they appear in the DB
                if len(s.history) > last_pushed_count:
                    # Find the last AI message
                    ai_msgs = [m for m in s.history if m.role == "ai"]
                    if ai_msgs:
                        last_ai = ai_msgs[-1]
                        # Mock a synthesis to satisfy the schema the frontend expects
                        # In a real app, we might save the full synthesis to the DB too.
                        dummy_synth = SupervisorSynthesis(
                            aggressive_thought="Push", sympathetic_thought="Push", analytical_thought="Push",
                            final_response=last_ai.content, rationale="Synchronized from state store.", 
                            suggested_next_price=s.current_lowball_price
                        )
                        await websocket.send_text(ChatResponse(synthesis=dummy_synth, analytical_data=s.analytical_data).model_dump_json())
                        last_pushed_count = len(s.history)

                # Stop watching once research is done and we have at least one message
                if s.analytical_data.is_researched and last_pushed_count > 0:
                    break
                await asyncio.sleep(2)

        watcher_task = asyncio.create_task(watch_db())

        # --- MAIN CHAT LOOP ---
        while True:
            # 2. Rate Limit Check
            try:
                await limiter.check_rate_limit(auth_token)
            except HTTPException as e:
                await websocket.send_text(json.dumps({"error": e.detail}))
                continue

            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON format."}))
                continue

            user_text = message_data.get("user_message", "")
            if not user_text:
                continue

            # 3. Process the turn with internal error handling
            try:
                # Reload state from DB
                state = await store.load_state(session_id)
                if not state:
                    await websocket.send_text(json.dumps({"error": "Session not found."}))
                    break

                state.history.append(Message(role="user", content=user_text))

                # 4. Unified Negotiation Agent Call
                response: SupervisorSynthesis = await unified.get_negotiation_response(state)

                # 5. Update & Persist State
                state.history.append(Message(role="ai", content=response.final_response))
                state.current_lowball_price = response.suggested_next_price
                await store.save_state(state)

                # 6. Respond to Client with the unified ChatResponse
                chat_res = ChatResponse(
                    synthesis=response,
                    analytical_data=state.analytical_data
                )
                await websocket.send_text(chat_res.model_dump_json())

            except Exception as e:
                logger.exception(f"Error processing turn in session {session_id}")
                # Send the error to the client so it appears in the chat bubbles
                error_msg = str(e)
                if "ResourceExhausted" in error_msg or "429" in error_msg:
                    friendly_error = "Gemini API Quota exceeded. Please wait a minute."
                else:
                    friendly_error = f"Internal Engine Error: {error_msg}"
                
                await websocket.send_text(json.dumps({"error": friendly_error}))

    except WebSocketDisconnect:
        logger.info(f"WebSocket Disconnected: Session {session_id}")
    except Exception:
        logger.exception(f"Fatal error in WebSocket handler: {session_id}")
        if websocket.client_state.name != "DISCONNECTED":
            await websocket.close(code=1011)
    finally:
        # 7. Cleanup
        if 'watcher_task' in locals():
            watcher_task.cancel()
            try:
                await watcher_task
            except asyncio.CancelledError:
                pass
