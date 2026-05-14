from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from app.config import settings

class EnquiryRequest(BaseModel):
    enquiry: str = Field(..., description="The client enquiry text")

    @field_validator("enquiry")
    def validate_enquiry(cls, v):
        v = " ".join(v.split())
        if not v.strip():
            raise ValueError("Enquiry text cannot be empty.")
        if len(v) > settings.MAX_INPUT_LENGTH:
            raise ValueError(f"Enquiry text exceeds the maximum length of {settings.MAX_INPUT_LENGTH} characters.")
        return v

class AnalysisData(BaseModel):
    category: str
    confidence: float
    sentiment: str
    priority: str
    suggested_response: str
    recommended_actions: List[str]
    reasoning: str
    is_vague: bool

class AnalysisResponse(BaseModel):
    success: bool
    data: Optional[AnalysisData] = None
    enquiry: Optional[str] = None
    timestamp: Optional[datetime] = None
    error: Optional[str] = None

class HistoryResponse(BaseModel):
    success: bool
    data: List[AnalysisResponse]
