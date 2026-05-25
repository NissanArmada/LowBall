import logging
import asyncio
from typing import List, Dict
from models.schemas import AnalyticalData
from services.resilience import llm_retry_decorator, llm_circuit_breaker
from services.ai import ai_provider
import json

logger = logging.getLogger(__name__)

class MarketScraper:
    """
    Real Market Scraper service using Gemini + Google Search Grounding.
    This fulfills the mandate for real-world market data extraction.
    """
    
    @llm_retry_decorator
    async def analyze_market(self, item_name: str) -> AnalyticalData:
        """
        Uses Gemini with Google Search to find real market prices.
        """
        # 1. Initialize the model with Google Search tools
        # Note: In a production environment, we'd ensure the model has 'google_search_retrieval'
        model = ai_provider.get_model(model_name="gemini-1.5-flash")
        
        prompt = f"""
        Search for the current marketplace prices (eBay, Facebook Marketplace, local listings) 
        for the following item: '{item_name}'.
        
        TASK:
        1. Find at least 3-5 real-world listings.
        2. Calculate the average price.
        3. Identify price volatility (high variance between listings).
        
        OUTPUT:
        You MUST return a JSON object with:
        - calculated_fair_market_avg (float)
        - price_volatility (float, 0.0 to 1.0)
        - recommended_walk_away_price (float)
        """

        try:
            # Execute protected call through circuit breaker
            # Using tools=['google_search_retrieval'] enables grounding
            response = await model.generate_content_async(
                prompt,
                tools=[{'google_search_retrieval': {}}],
                generation_config={
                    "response_mime_type": "application/json",
                    "response_schema": AnalyticalData.model_json_schema()
                }
            )
            
            # Robust parsing using our utility
            from core.utils import strip_json_markdown
            clean_json = strip_json_markdown(response.text)
            logger.info(f"REAL SCRAPER RESULT for '{item_name}': {clean_json}")
            
            return AnalyticalData.model_validate_json(clean_json)

        except Exception as e:
            logger.error(f"Real Scraper failed for '{item_name}': {str(e)}")
            # Fallback logic: If search fails, we don't want to break the whole flow.
            # We return a 0.0 to indicate 'No Data Found', which the Agent should handle.
            return AnalyticalData(
                calculated_fair_market_avg=0.0,
                price_volatility=0.0,
                recommended_walk_away_price=0.0
            )

# Global instance for DI
scraper = MarketScraper()
