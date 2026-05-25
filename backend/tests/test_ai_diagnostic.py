import sys
import os
import asyncio

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ai import ai_provider
from core.config import settings

async def test_ai_diagnostic():
    print(f"Project: {settings.PROJECT_NAME}")
    print(f"API Key Present: {bool(settings.GOOGLE_API_KEY)}")
    
    try:
        model = ai_provider.get_model()
        print(f"Model initialized: {model.model_name}")
        
        vision_model = ai_provider.get_vision_model()
        print(f"Vision model initialized: {vision_model.model_name}")
        
        print("\n--- AI Provider Diagnostic: PASSED ---")
    except Exception as e:
        print(f"\n--- AI Provider Diagnostic: FAILED ---")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_ai_diagnostic())
