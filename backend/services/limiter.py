import time
import logging
from collections import defaultdict
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    A simple in-memory Fixed-Window Rate Limiter.
    In a distributed production environment, this would use Redis.
    """
    def __init__(self, requests_per_window: int = 60, window_seconds: int = 60):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        # In-memory storage: user_token -> (count, window_start_time)
        self.buckets = defaultdict(lambda: [0, time.time()])

    async def check_rate_limit(self, user_key: str):
        """
        Validates if the request is within the rate limit.
        Raises HTTPException if exceeded.
        """
        now = time.time()
        count, window_start = self.buckets[user_key]

        # Reset bucket if window has passed
        if now - window_start > self.window_seconds:
            self.buckets[user_key] = [1, now]
            return

        # Check if limit exceeded
        if count >= self.requests_per_window:
            logger.warning(f"Rate limit exceeded for user: {user_key}")
            raise HTTPException(
                status_code=429, 
                detail="Too many requests. Please try again later."
            )

        # Increment count
        self.buckets[user_key][0] += 1

# Global instance for DI
limiter = RateLimiter(requests_per_window=20, window_seconds=60) # 20 messages per minute
