from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.ai_analysis import AIAnalyzeRequest, AIAnalyzeResponse
from app.services.ai_analysis_service import AIAnalysisService
from app.models.user import User

router = APIRouter(prefix="/api/ai", tags=["AI"])


@router.post("/analyze", response_model=AIAnalyzeResponse)
def analyze_text(
    data: AIAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AIAnalysisService(db)
    return service.analyze_text(data.text)
