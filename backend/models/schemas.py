from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Message(BaseModel):
    role: str  # "user", "seller", "ai"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ListingAnalyzeRequest(BaseModel):
    image_base64: str

class ListingMetadata(BaseModel):
    session_id: Optional[str] = None
    item_name: str
    original_listing_price: float
    suggested_low_price: float
    suggested_high_price: float
    condition: str
    description: str

class AnalyticalData(BaseModel):
    calculated_fair_market_avg: float
    price_volatility: float
    recommended_walk_away_price: float

class SupervisorSynthesis(BaseModel):
    aggressive_thought: str
    sympathetic_thought: str
    analytical_thought: str
    final_response: str
    rationale: str
    suggested_next_price: float

class NegotiationState(BaseModel):
    session_id: str
    item_metadata: ListingMetadata
    analytical_data: AnalyticalData
    history: List[Message]
    current_lowball_price: float

class ChatMessage(BaseModel):
    user_message: str
