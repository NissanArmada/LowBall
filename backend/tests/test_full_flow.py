import requests
import asyncio
import websockets
import json
import time
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings

def test_full_listing_to_chat_flow(image_path: str):
    base_url = "http://127.0.0.1:8000"
    ws_url = "ws://127.0.0.1:8000/api/v1/chat"
    analyze_url = f"{base_url}/api/v1/listing/analyze"
    
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found at {image_path}")
        return

    # 1. Analyze Listing (Vision Agent)
    print(f"\n--- STEP 1: VISION ANALYSIS ---")
    print(f"Uploading real screenshot: {image_path}...")
    
    with open(image_path, "rb") as f:
        files = {"file": (os.path.basename(image_path), f, "image/png")}
        response = requests.post(analyze_url, files=files)
    
    if response.status_code != 200:
        print(f"Analysis failed: {response.text}")
        return

    metadata = response.json()
    session_id = metadata["session_id"]
    
    print("\n--- EXTRACTED METADATA ---")
    print(json.dumps(metadata, indent=4))
    print("--------------------------")

    # 2. Wait for Background Scraper
    print("\n--- STEP 2: BACKGROUND RESEARCH ---")
    print("Waiting for background market scraper (simulating multi-platform search)...")
    # Give the scraper time to update the analytical data in SQLite
    time.sleep(6)

    # 3. Connect via WebSocket (Negotiation Agent)
    print("\n--- STEP 3: LIVE NEGOTIATION ---")
    
    async def run_chat():
        api_token = settings.API_SECRET_TOKEN
        
        uri = f"{ws_url}/{session_id}"
        headers = {"X-API-Token": api_token}
        
        async with websockets.connect(uri, additional_headers=headers) as websocket:
            # First Message: Open the negotiation
            user_msg = "Hi, is this still available? I'm interested but have a limited budget."
            print(f"\n[Buyer]: {user_msg}")
            
            await websocket.send(json.dumps({"user_message": user_msg}))
            
            # Recv response
            raw_res = await websocket.recv()
            data = json.loads(raw_res)
            
            if "error" in data:
                print(f"\n[SERVER ERROR]: {data['error']}")
                return
            
            print("\n--- AI COUNCIL-OF-THOUGHT ---")
            print(f"AGGRESSIVE:  {data.get('aggressive_thought')}")
            print(f"SYMPATHETIC: {data.get('sympathetic_thought')}")
            print(f"ANALYTICAL:  {data.get('analytical_thought')}")
            print(f"RATIONALE:   {data.get('rationale')}")
            print("------------------------------")
            
            print(f"\n[AI Assistant]: {data['final_response']}")
            print(f"(Suggested Next Price: ${data['suggested_next_price']})")
            
            # Second Message: Follow up
            time.sleep(2)
            user_msg2 = "What's the best you can do on the price?"
            print(f"\n[Buyer]: {user_msg2}")
            await websocket.send(json.dumps({"user_message": user_msg2}))
            
            raw_res2 = await websocket.recv()
            data2 = json.loads(raw_res2)
            
            print(f"\n[AI Assistant]: {data2['final_response']}")
            print(f"(Suggested Next Price: ${data2['suggested_next_price']})")

    try:
        asyncio.run(run_chat())
        print("\nFULL PIPELINE TEST COMPLETE!")
    except Exception as e:
        print(f"\nNEGOTIATION FAILED: {str(e)}")

if __name__ == "__main__":
    # You can change the image path here to test different scenarios
    # Since we are in tests/, the image is in the same folder
    test_image = os.path.join(os.path.dirname(__file__), "general_image_test.png")
    
    if len(sys.argv) > 1:
        test_image = sys.argv[1]
        
    test_full_listing_to_chat_flow(test_image)
