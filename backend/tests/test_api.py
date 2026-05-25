import pytest
from core.config import settings
import time
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
            dummy_image = b"fake image"
            files = {"file": ("test.png", dummy_image, "image/png")}
            
            response = await client.post("/api/v1/listing/analyze", files=files)
            
            assert response.status_code == 200
            assert "session_id" in response.json()
            # Verify background task was added
            assert mock_scrape.called
