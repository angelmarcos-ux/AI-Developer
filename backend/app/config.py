from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Application Config
    PROJECT_NAME: str = "Enterprise AI Enquiry Analyser"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # OpenAI Config
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TEMPERATURE: float = 0.3

    # Database Config
    DATABASE_URL: str = "sqlite:///./enterprise_app.db"

    # CORS Config
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]

    # Input Constraints
    MAX_INPUT_LENGTH: int = 5000

    # Categories
    CATEGORIES: List[str] = [
        "New Client Enquiry",
        "Support Request",
        "Complaint",
        "General Question",
        "Urgent/Escalation",
    ]

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
