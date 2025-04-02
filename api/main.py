from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_client import Counter, Histogram
import time
import logging
from typing import Dict, Any

from core.config import get_settings
from core.logger import setup_logging, get_api_logger
from api.routes import (
    auth,
    market_analysis,
    trading,
    content,
    users,
    subscriptions
)
from api.middleware.rate_limit import RateLimitMiddleware
from api.middleware.auth import AuthMiddleware

# Initialize settings
settings = get_settings()

# Setup logging
setup_logging()
logger = get_api_logger()

# Initialize FastAPI app
app = FastAPI(
    title="Prometheus Bot API",
    description="API for automated trading, content generation, and service delivery",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(market_analysis.router, prefix="/api/market-analysis", tags=["Market Analysis"])
app.include_router(trading.router, prefix="/api/trading", tags=["Trading"])
app.include_router(content.router, prefix="/api/content", tags=["Content"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["Subscriptions"])

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers and record metrics"""
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        # Record metrics
        process_time = time.time() - start_time
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(process_time)
        
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        # Add processing time to response headers
        response.headers["X-Process-Time"] = str(process_time)
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise

@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time()
    }

@app.get("/api/metrics")
async def metrics() -> Dict[str, Any]:
    """Basic metrics endpoint"""
    return {
        "requests_total": REQUEST_COUNT._value.sum(),
        "request_latency_seconds": REQUEST_LATENCY._sum.sum() / REQUEST_LATENCY._count.sum() if REQUEST_LATENCY._count.sum() > 0 else 0
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Global exception handler for HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "path": request.url.path,
            "method": request.method
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "path": request.url.path,
            "method": request.method
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 