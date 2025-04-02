from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime
import logging
from typing import Optional, Dict, Any

from core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)
security = HTTPBearer()

class AuthMiddleware:
    def __init__(self):
        self.excluded_paths = {
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
            "/api/health",
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/refresh"
        }
    
    async def __call__(self, request: Request, call_next):
        # Skip authentication for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        try:
            # Get token from header
            credentials: HTTPAuthorizationCredentials = await security(request)
            token = credentials.credentials
            
            # Verify token
            payload = self._verify_token(token)
            
            # Add user info to request state
            request.state.user = payload
            
            # Process request
            response = await call_next(request)
            return response
            
        except HTTPException as e:
            logger.warning(f"Authentication failed: {str(e)}")
            return response
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )
    
    def _verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Check token expiration
            exp = payload.get("exp")
            if exp is None or datetime.fromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(
                    status_code=401,
                    detail="Token has expired"
                )
            
            return payload
            
        except JWTError as e:
            logger.error(f"JWT verification failed: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
    
    def _get_token_from_header(self, request: Request) -> Optional[str]:
        """Extract token from Authorization header"""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None
            
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                return None
            return token
        except ValueError:
            return None 