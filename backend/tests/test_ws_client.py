import asyncio
import websockets
import json
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings

async def test_chat():
    uri = "ws://127.0.0.1:8000/api/v1/chat/test_session_123"
    headers = {"X-API-Token": settings.API_SECRET_TOKEN}
    async with websockets.connect(uri, additional_headers=headers) as websocket:
        print(f"Connected to {uri}")
        
        # Simulate a user message
        message = {
            "user_message": "Hi, I'm interested in the item. Would you take $40 for it?"
        }
        
        print(f"Sending: {message}")
        await websocket.send(json.dumps(message))
        
        # Wait for the Supervisor response
        response = await websocket.recv()
        data = json.loads(response)
        
        print("\n--- Supervisor Response Received ---")
        print(json.dumps(data, indent=4))
        print("------------------------------------\n")

if __name__ == "__main__":
    try:
        asyncio.run(test_chat())
    except Exception as e:
        print(f"Test failed: {e}")
