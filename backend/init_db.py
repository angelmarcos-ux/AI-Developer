import os
import sys
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from app.database import engine, Base
from app.models import EnquiryAnalysis

logger.remove()
logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")

def init_db():
    logger.info("Initializing database...")
    logger.info(f"Connection String: {os.getenv('DATABASE_URL').split('@')[1] if os.getenv('DATABASE_URL') else 'Not Found'}")
    
    try:
        # This creates all tables defined in models.py
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully in Supabase!")
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {str(e)}")

if __name__ == "__main__":
    init_db()