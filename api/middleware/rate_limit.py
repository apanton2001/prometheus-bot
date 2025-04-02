from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Dict, Tuple
import time
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_size: int = 10
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_size = burst_size
        self.requests: Dict[str, list] = defaultdict(list)
        
    async def __call__(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean up old requests
        self._cleanup_old_requests(client_ip, current_time)
        
        # Check rate limits
        if self._is_rate_limited(client_ip, current_time):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too many requests",
                    "retry_after": self._get_retry_after(client_ip, current_time)
                }
            )
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        return response
    
    def _cleanup_old_requests(self, client_ip: str, current_time: float):
        """Remove requests older than 1 hour"""
        one_hour_ago = current_time - 3600
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > one_hour_ago
        ]
    
    def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """Check if the client is rate limited"""
        # Check burst limit
        recent_requests = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time <= 1  # Last second
        ]
        if len(recent_requests) > self.burst_size:
            return True
        
        # Check per-minute limit
        minute_ago = current_time - 60
        minute_requests = [
            req_time for req_time in self.requests[client_ip]
            if req_time > minute_ago
        ]
        if len(minute_requests) > self.requests_per_minute:
            return True
        
        # Check per-hour limit
        hour_ago = current_time - 3600
        hour_requests = [
            req_time for req_time in self.requests[client_ip]
            if req_time > hour_ago
        ]
        if len(hour_requests) > self.requests_per_hour:
            return True
        
        return False
    
    def _get_retry_after(self, client_ip: str, current_time: float) -> int:
        """Calculate retry-after time in seconds"""
        if not self.requests[client_ip]:
            return 0
        
        # Check burst limit
        recent_requests = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time <= 1
        ]
        if len(recent_requests) > self.burst_size:
            return 1
        
        # Check per-minute limit
        minute_ago = current_time - 60
        minute_requests = [
            req_time for req_time in self.requests[client_ip]
            if req_time > minute_ago
        ]
        if len(minute_requests) > self.requests_per_minute:
            return 60 - (current_time - minute_requests[0])
        
        # Check per-hour limit
        hour_ago = current_time - 3600
        hour_requests = [
            req_time for req_time in self.requests[client_ip]
            if req_time > hour_ago
        ]
        if len(hour_requests) > self.requests_per_hour:
            return 3600 - (current_time - hour_requests[0])
        
        return 0 