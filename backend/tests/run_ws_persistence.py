import asyncio
import websockets
import json
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings

async def test_chat():
    uri = f"ws://127.0.0.1:8000/api/v1/chat/test_session_123?token={settings.API_SECRET_TOKEN}"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to {uri}")
        
        # Message 1
        message1 = {"user_message": "Is this still available?"}
        print(f"Sending 1: {message1}")
        await websocket.send(json.dumps(message1))
        await websocket.recv()
        
        # Message 2
        message2 = {"user_message": "I can offer $35."}
        print(f"Sending 2: {message2}")
        await websocket.send(json.dumps(message2))
        
        response = await websocket.recv()
        data = json.loads(response)
        
        print("\n--- Final Supervisor Response ---")
        print(json.dumps(data, indent=4))
        print("------------------------------------\n")

if __name__ == "__main__":
    try:
        asyncio.run(test_chat())
    except Exception as e:
        print(f"Test failed: {e}")
