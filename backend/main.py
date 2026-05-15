import sys
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import Base, engine
from app import routers

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Include routers
app.include_router(routers.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up API...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down API...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
