from models.schemas import ListingMetadata
from services.resilience import llm_retry_decorator, vision_circuit_breaker
from services.ai import ai_provider
from core.utils import clean_schema, strip_json_markdown
import base64
import json

SYSTEM_PROMPT = """
You are the 'Vision Analysis Agent' for Lowball.ai.
Your task is to analyze a screenshot of a marketplace listing (Facebook Marketplace, OfferUp, eBay, etc.) and extract key information.

EXTRACT THE FOLLOWING:
1. Item Name: The title of the listing.
2. Original Listing Price: The price the seller is currently asking.
3. Condition: The state of the item (e.g., New, Used - Like New, Good, Fair).
4. Description: A brief summary of the item's details.

ANALYTICAL TASKS:
5. Suggested Low Price: A realistic lowball starting offer (e.g., 60-70% of asking).
6. Suggested High Price: A realistic "fair" price (e.g., 85-90% of asking).

OUTPUT FORMAT:
You MUST return a valid JSON object matching the ListingMetadata schema.
"""

@llm_retry_decorator
async def _execute_vision_call(image_bytes: bytes) -> ListingMetadata:
    """
    Internal function to perform the Vision LLM call using Gemini.
    """
    model = ai_provider.get_vision_model()
    
    # Prepare the image part
    image_part = {
        "mime_type": "image/png",
        "data": image_bytes
    }
    
    # Clean the schema for Gemini
    raw_schema = ListingMetadata.model_json_schema()
    safe_schema = clean_schema(raw_schema)
    
    # Invoke Gemini with Structured Output
    response = await model.generate_content_async(
        [SYSTEM_PROMPT, image_part],
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": safe_schema
        }
    )
    
    # Robust extraction
    clean_json_text = strip_json_markdown(response.text)
    return ListingMetadata.model_validate_json(clean_json_text)

async def analyze_image(image_bytes: bytes) -> ListingMetadata:
    """
    Analyzes the image using a Vision LLM, protected by a Circuit Breaker.
    """
    return await vision_circuit_breaker.call(_execute_vision_call, image_bytes)
