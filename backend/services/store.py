import aiosqlite
import json
from models.schemas import NegotiationState, ListingMetadata, AnalyticalData, Message
from typing import Optional
from core.config import settings

class SessionStore:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    state_json TEXT
                )
            """)
            await db.commit()

    async def save_state(self, state: NegotiationState):
        async with aiosqlite.connect(self.db_path) as db:
            # Pydantic v2: use model_dump_json() instead of json()
            state_json = state.model_dump_json()
            await db.execute("""
                INSERT OR REPLACE INTO sessions (session_id, state_json)
                VALUES (?, ?)
            """, (state.session_id, state_json))
            await db.commit()

    async def load_state(self, session_id: str) -> Optional[NegotiationState]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT state_json FROM sessions WHERE session_id = ?", (session_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    # Pydantic v2: use model_validate_json() instead of parse_raw()
                    return NegotiationState.model_validate_json(row[0])
        return None

# Global instance for easy injection
store = SessionStore(db_path=settings.DB_PATH)
