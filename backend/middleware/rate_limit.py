import time
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from typing import Dict, Tuple

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.
    Limits requests to 100 per minute per IP address.
    """
    
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_history: Dict[str, list] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Get request history for this IP
        requests = self.request_history[client_ip]
        
        # Remove requests older than 1 minute
        requests[:] = [req_time for req_time in requests if current_time - req_time < 60]
        
        # Check if limit exceeded
        if len(requests) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {self.requests_per_minute} requests per minute"
            )
        
        # Record this request
        requests.append(current_time)
        
        # Continue to next middleware/handler
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(self.requests_per_minute - len(requests))
        
        return response
