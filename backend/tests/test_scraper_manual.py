import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.scraper import scraper
from core.config import settings

async def main():
    print(f"Using API Key: {bool(settings.GOOGLE_API_KEY)}")
    print("Testing scraper...")
    result = await scraper.analyze_market("used gaming pc")
    print(result.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(main())
