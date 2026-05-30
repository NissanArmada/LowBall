import pytest
import httpx
from main import app
from unittest.mock import patch

@pytest.mark.asyncio
async def test_root_endpoint():
    """Verify basic API availability."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "online" in response.json()["message"]

@pytest.mark.asyncio
async def test_observability_middleware_headers():
    """
    Architectural Mandate: Observability middleware to track request latency.
    """
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert "X-Process-Time" in response.headers
        # Latency should be a small float
        latency = float(response.headers["X-Process-Time"])
        assert latency > 0

@pytest.mark.asyncio
async def test_listing_analyze_background_task_trigger():
    """
    Architectural Mandate: Scraper architecture decoupled from primary request flow.
    Verification: We mock the background task to ensure it is triggered.
    Requires: X-API-Token header for security alignment.
    """
    from core.config import settings
    test_token = "test-token-123"
    
    with patch("api.v1.endpoints.listing.background_market_scrape") as mock_scrape, \
         patch.object(settings, "API_SECRET_TOKEN", test_token):
        
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            import os
            # Use a real image to prevent Gemini 400 Invalid Argument error
            test_image_path = os.path.join(os.path.dirname(__file__), "general_image_test.png")
            with open(test_image_path, "rb") as f:
                files = {"file": ("test.png", f, "image/png")}
                headers = {"X-API-Token": test_token}
                response = await client.post("/api/v1/listing/analyze", files=files, headers=headers)
            
            assert response.status_code == 200
            assert "session_id" in response.json()
            # Verify background task was added
            assert mock_scrape.called

@pytest.mark.asyncio
async def test_listing_analyze_security_enforcement():
    """
    Verify that the /analyze endpoint rejects requests without a valid token.
    """
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        import os
        test_image_path = os.path.join(os.path.dirname(__file__), "general_image_test.png")
        with open(test_image_path, "rb") as f:
            files = {"file": ("test.png", f, "image/png")}
            
            # 1. No header -> 422 (FastAPI default for required header)
            response = await client.post("/api/v1/listing/analyze", files=files)
            assert response.status_code == 422
            
            # 2. Invalid token -> 401 (Our custom logic)
            headers = {"X-API-Token": "wrong-token"}
            response = await client.post("/api/v1/listing/analyze", files=files, headers=headers)
            assert response.status_code == 401
