from models.schemas import SupervisorSynthesis, NegotiationState
from core.config import settings
from services.resilience import llm_retry_decorator, llm_circuit_breaker
from services.ai import ai_provider
from core.utils import clean_schema, strip_json_markdown
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are the 'Unified Negotiation Agent' for Lowball.ai, an expert at marketplace negotiations.
Your goal is to secure the absolute lowest possible price for your client (the buyer) while ensuring the seller remains engaged.

CONTEXT:
- Item: {item_name}
- Condition: {condition}
- Fair Market Avg: ${market_avg}
- Walk-away Price: ${walk_away}

COUNCIL-OF-THOUGHT INSTRUCTIONS:
Before providing the final response, you must internally simulate three distinct personas to reach the optimal strategy:

1. AGGRESSIVE THOUGHT: Identify leverage points and firm anchoring strategies.
2. SYMPATHETIC THOUGHT: Identify ways to build rapport and stay polite.
3. ANALYTICAL THOUGHT: Compare the current situation against market data and walk-away price.

FINAL OUTPUT:
Synthesize these thoughts into a professional, realistic, and effective message to the seller.
IMPORTANT: DO NOT use em-dashes (—) or en-dashes (–) in your final response. Use simple commas or periods for a more casual, human feel.
"""

def get_windowed_history(state: NegotiationState, window_size: int = settings.CONVERSATION_WINDOW) -> str:
    """Returns the last N messages from history."""
    recent_history = state.history[-window_size:]
    formatted = []
    for msg in recent_history:
        role_label = "Buyer" if msg.role == "user" else "Seller" if msg.role == "seller" else "AI"
        formatted.append(f"{role_label}: {msg.content}")
    return "\n".join(formatted)

@llm_retry_decorator
async def _execute_llm_call(prompt: str, history: str) -> SupervisorSynthesis:
    """
    Internal function to perform the actual LLM call using Gemini.
    """
    model = ai_provider.get_model()
    full_content = f"{prompt}\n\nCONVERSATION HISTORY:\n{history}"
    
    # Clean the schema for Gemini
    raw_schema = SupervisorSynthesis.model_json_schema()
    safe_schema = clean_schema(raw_schema)
    
    # Invoke Gemini with Structured Output
    response = await model.generate_content_async(
        full_content,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": safe_schema
        }
    )
    
    # Robust extraction: Strip markdown if model hallucinated it
    clean_json_text = strip_json_markdown(response.text)
    logger.info(f"LLM Response Parsed: {clean_json_text}")
    
    return SupervisorSynthesis.model_validate_json(clean_json_text)

async def get_negotiation_response(state: NegotiationState) -> SupervisorSynthesis:
    """
    Invokes the Unified Agent with Council-of-Thought, protected by 
    Circuit Breakers and Retry logic.
    """
    try:
        prompt = SYSTEM_PROMPT.format(
            item_name=state.item_metadata.item_name,
            condition=state.item_metadata.condition,
            market_avg=state.analytical_data.calculated_fair_market_avg,
            walk_away=state.analytical_data.recommended_walk_away_price
        )
        history_str = get_windowed_history(state)
        if not history_str.strip():
            history_str = "[No previous messages. You are initiating the conversation with the seller.]"
        
        return await llm_circuit_breaker.call(_execute_llm_call, prompt, history_str)
    except Exception as e:
        error_msg = str(e)
        # Gracefully handle Quota (429) or Server Errors (500)
        if any(token in error_msg for token in ["429", "ResourceExhausted", "500", "InternalServerError"]):
            logger.warning(f"Gemini API issue detected: {error_msg}. Yielding cooling off message.")
            return SupervisorSynthesis(
                aggressive_thought="Error",
                sympathetic_thought="Error",
                analytical_thought="Error",
                final_response="Whoa, slow down! The AI is cooling off! Please wait a minute.",
                rationale="Gemini API rate limit or internal error hit. Graceful fallback engaged.",
                suggested_next_price=state.current_lowball_price
            )
        raise e
