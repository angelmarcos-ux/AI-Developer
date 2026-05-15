import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from loguru import logger

from app.config import settings
from app.database import engine, Base
from app.routers import router as api_router
from app.routers import limiter

# Setup structured logging
logger.remove()
logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

# Initialize Database tables
Base.metadata.create_all(bind=engine)

# FastAPI Application Initialization
app = FastAPI(
    title="AI Developer API",
    description="Backend services for the AI Developer application",
    version="1.0.0"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach rate limiter state and exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(routers.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting up API...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down API...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
