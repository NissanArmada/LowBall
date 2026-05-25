from services.store import store, SessionStore
from services.limiter import limiter, RateLimiter
from services.ai import ai_provider, AIProvider

def get_store() -> SessionStore:
    """Dependency provider for the SessionStore."""
    return store

def get_limiter() -> RateLimiter:
    """Dependency provider for the RateLimiter."""
    return limiter

def get_ai_provider() -> AIProvider:
    """Dependency provider for the AI service."""
    return ai_provider
