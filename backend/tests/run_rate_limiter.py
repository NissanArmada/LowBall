import asyncio
import websockets
import json

import requests

async def test_rate_limiter():
    # 1. Create a session
    print("Step 1: Creating session...")
    analyze_url = "http://127.0.0.1:8000/api/v1/listing/analyze"
    import os
    test_image_path = os.path.join(os.path.dirname(__file__), "general_image_test.png")
    with open(test_image_path, "rb") as f:
        files = {"file": ("test.png", f, "image/png")}
        res = requests.post(analyze_url, files=files)
    session_id = res.json()["session_id"]
    
    uri = f"ws://127.0.0.1:8000/api/v1/chat/{session_id}"
    from core.config import settings
    headers = {"X-API-Token": settings.API_SECRET_TOKEN}
    async with websockets.connect(uri, additional_headers=headers) as websocket:
        print(f"Connected to {uri}")
        
        # Send 25 messages rapidly (limit is 20)
        for i in range(25):
            message = {"user_message": f"Message {i}"}
            print(f"Sending {i}...")
            await websocket.send(json.dumps(message))
            
            response = await websocket.recv()
            data = json.loads(response)
            
            if "error" in data:
                print(f"\n--- Rate Limit Triggered at message {i} ---")
                print(f"Error: {data['error']}")
                print("------------------------------------------\n")
                return
        
        print("FAILED: Rate limit not triggered.")

if __name__ == "__main__":
    try:
        asyncio.run(test_rate_limiter())
    except Exception as e:
        print(f"Test failed: {e}")
