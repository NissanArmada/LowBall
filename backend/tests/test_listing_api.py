import requests
import os

def test_listing_analysis():
    url = "http://127.0.0.1:8000/api/v1/listing/analyze"
    
    # Create a dummy image file for testing
    dummy_image_path = "test_screenshot.png"
    with open(dummy_image_path, "wb") as f:
        f.write(b"fake image data")

    try:
        with open(dummy_image_path, "rb") as f:
            files = {"file": (dummy_image_path, f, "image/png")}
            print(f"Uploading {dummy_image_path} to {url}...")
            response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("\n--- Listing Metadata Received ---")
            print(response.json())
            print("---------------------------------\n")
        else:
            print(f"Error: {response.text}")
            
    finally:
        if os.path.exists(dummy_image_path):
            os.remove(dummy_image_path)

if __name__ == "__main__":
    test_listing_analysis()
