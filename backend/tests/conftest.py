import pytest
import asyncio
import os
from services.store import SessionStore
from core.config import settings
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_store():
    test_db = "test_lowball.db"
    store = SessionStore(db_path=test_db)
    await store.init_db()
    yield store
    # Cleanup
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except PermissionError:
            pass

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
