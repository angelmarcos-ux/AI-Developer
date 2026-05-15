from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from loguru import logger
import json

from app.schemas import EnquiryRequest, AnalysisResponse, HistoryResponse
from app.database import get_db
from app.models import EnquiryAnalysis
from app.ai_service import analyse_enquiry

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.post("/analyse", response_model=AnalysisResponse)
@limiter.limit("5/minute")
async def analyse(request_data: EnquiryRequest, request: Request, db: Session = Depends(get_db)):
    logger.info("Received new enquiry analysis request.")
    
    result = await analyse_enquiry(request_data.enquiry)
    
    if not result["success"]:
        logger.warning(f"AI analysis failed: {result['error']}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=result["error"]
        )
        
    data = result["data"]
    
    # Save to database
    try:
        db_analysis = EnquiryAnalysis(
            enquiry_text=request_data.enquiry,
            category=data["category"],
            confidence=data["confidence"],
            sentiment=data["sentiment"],
            priority=data["priority"],
            suggested_response=data["suggested_response"],
            recommended_actions=json.dumps(data["recommended_actions"]),
            reasoning=data["reasoning"],
            is_vague=data.get("is_vague", False)
        )
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        logger.info(f"Saved analysis to database with ID: {db_analysis.id}")
    except Exception as e:
        logger.error(f"Failed to save analysis to database: {e}")
        db.rollback()
        # We don't fail the request if DB save fails, just log it.
        # Alternatively, we could raise an HTTPException.
        
    return AnalysisResponse(
        success=True,
        data=data,
        enquiry=request_data.enquiry,
        timestamp=db_analysis.created_at if 'db_analysis' in locals() else None
    )

@router.get("/history", response_model=HistoryResponse)
def get_history(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    logger.info("Fetching analysis history.")
    analyses = db.query(EnquiryAnalysis).order_by(EnquiryAnalysis.created_at.desc()).offset(skip).limit(limit).all()
    
    history_data = []
    for item in analyses:
        history_data.append(AnalysisResponse(
            success=True,
            data={
                "category": item.category,
                "confidence": item.confidence,
                "sentiment": item.sentiment,
                "priority": item.priority,
                "suggested_response": item.suggested_response,
                "recommended_actions": json.loads(item.recommended_actions),
                "reasoning": item.reasoning,
                "is_vague": item.is_vague
            },
            enquiry=item.enquiry_text,
            timestamp=item.created_at
        ))
        
    return HistoryResponse(
        success=True,
        data=history_data
    )

@router.delete("/history")
def delete_history(db: Session = Depends(get_db)):
    logger.info("Clearing analysis history.")
    try:
        db.query(EnquiryAnalysis).delete()
        db.commit()
        return {"success": True, "message": "History cleared"}
    except Exception as e:
        logger.error(f"Failed to clear history: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear history"
        )

@router.get("/health")
def health():
    return {"status": "healthy"}
