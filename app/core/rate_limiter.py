from fastapi import HTTPException, Request
from typing import Callable
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, requests_limit: int, window_seconds: int):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.client_requests = defaultdict(list)

    async def __call__(self, request: Request):
        # Use client IP as identifier
        client_ip = request.client.host
        now = time.time()
        
        # Filter out requests outside the window
        self.client_requests[client_ip] = [
            t for t in self.client_requests[client_ip]
            if now - t < self.window_seconds
        ]
        
        if len(self.client_requests[client_ip]) >= self.requests_limit:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )
        
        self.client_requests[client_ip].append(now)

# Example: 60 requests per minute
rate_limiter = RateLimiter(requests_limit=60, window_seconds=60)
