from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AIAnalyzeRequest(BaseModel):
    text: str


class AIAnalyzeResponse(BaseModel):
    category: str
    probability: str
    impact: str
    severity: str
    reason: str
    recommended_action: str


class AIAnalysisRead(BaseModel):
    id: str
    input_text: str
    category: str
    probability: str
    impact: str
    severity: str
    reason: str
    recommended_action: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
