import google.generativeai as genai
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class AIProvider:
    """
    Centralized provider for Google Gemini models.
    """
    def __init__(self, api_key: str):
        if not api_key:
            logger.warning("GOOGLE_API_KEY not set. AI services will fail.")
        else:
            genai.configure(api_key=api_key)
            logger.info("Gemini AI configured successfully.")

    def get_model(self, model_name: str = "gemini-flash-latest"):
        """Returns a configured GenerativeModel instance."""
        # Using Flash for everything to ensure free-tier compatibility
        return genai.GenerativeModel(model_name)

    def get_vision_model(self, model_name: str = "gemini-flash-latest"):
        """Returns a configured model suitable for Vision tasks."""
        return genai.GenerativeModel(model_name)

# Global instance for DI
ai_provider = AIProvider(api_key=settings.GOOGLE_API_KEY)
