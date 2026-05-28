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
    Note: In test environments, background tasks may be awaited by the runner.
    """
    with patch("api.v1.endpoints.listing.background_market_scrape") as mock_scrape:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            import os
            # Use a real image to prevent Gemini 400 Invalid Argument error
            test_image_path = os.path.join(os.path.dirname(__file__), "general_image_test.png")
            with open(test_image_path, "rb") as f:
                files = {"file": ("test.png", f, "image/png")}
                response = await client.post("/api/v1/listing/analyze", files=files)
            
            assert response.status_code == 200
            assert "session_id" in response.json()
            # Verify background task was added
            assert mock_scrape.called
