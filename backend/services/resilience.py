import logging
import asyncio
from typing import Callable, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

logger = logging.getLogger(__name__)

# Define custom exceptions for the resilience layer
class ExternalAPIFailure(Exception):
    """Raised when an external LLM or Vision API fails permanently."""
    pass

class CircuitBreakerOpen(Exception):
    """Raised when the circuit breaker is open and requests are blocked."""
    pass

# Retry configuration for LLM calls:
# - Retry up to 3 times
# - Exponential backoff starting at 1s
# - Only retry on transient/network exceptions
llm_retry_decorator = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)

class CircuitBreaker:
    """
    A simplified Circuit Breaker to protect the system from failing external services.
    If failures exceed a threshold, it 'opens' and blocks calls for a cooldown period.
    """
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.is_open = False

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.is_open:
            import time
            if time.time() - self.last_failure_time > self.recovery_timeout:
                logger.info("Circuit Breaker: Attempting recovery (half-open).")
                self.is_open = False
                self.failure_count = 0
            else:
                raise CircuitBreakerOpen("External service is currently unavailable (Circuit Open).")

        try:
            result = await func(*args, **kwargs)
            # Success! Reset counter
            self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            import time
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.is_open = True
                logger.error(f"Circuit Breaker: OPENED due to error: {str(e)}")
            
            raise e

# Global Circuit Breakers for different external domains
llm_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
vision_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)
