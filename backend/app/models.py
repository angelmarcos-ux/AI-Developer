from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base

class EnquiryAnalysis(Base):
    __tablename__ = "enquiry_analyses"

    id = Column(Integer, primary_key=True, index=True)
    enquiry_text = Column(Text, nullable=False)
    
    # Analysis results
    category = Column(String, index=True, nullable=False)
    confidence = Column(Float, nullable=False)
    sentiment = Column(String, nullable=False)
    priority = Column(String, index=True, nullable=False)
    suggested_response = Column(Text, nullable=False)
    recommended_actions = Column(Text, nullable=False) # stored as JSON string
    reasoning = Column(Text, nullable=False)
    is_vague = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
