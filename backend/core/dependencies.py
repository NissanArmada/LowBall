from services.store import store, SessionStore
from services.limiter import limiter, RateLimiter
from services.ai import ai_provider, AIProvider
from services.vision import analyze_image
from services.scraper import scraper, MarketScraper
from fastapi import Header, HTTPException, Depends
from core.config import settings
from typing import Callable, Awaitable

def get_store() -> SessionStore:
    """Dependency provider for the SessionStore."""
    return store

def get_limiter() -> RateLimiter:
    """Dependency provider for the RateLimiter."""
    return limiter

def get_ai_provider() -> AIProvider:
    """Dependency provider for the AI service."""
    return ai_provider

def get_scraper() -> MarketScraper:
    """Dependency provider for the MarketScraper service."""
    return scraper

def get_vision_service() -> Callable[[bytes], Awaitable]:
    """Dependency provider for the Vision Analysis service."""
    return analyze_image

async def verify_token(x_api_token: str = Header(...)):
    """
    Security dependency to verify the X-API-Token header.
    """
    if x_api_token != settings.API_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing API Token")
    return x_api_token
