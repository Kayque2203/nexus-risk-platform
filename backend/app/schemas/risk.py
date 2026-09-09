from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict

LevelType = Literal["baixa", "media", "alta", "critica"]
StatusType = Literal["aberto", "em_mitigacao", "mitigado", "aceito", "cancelado"]


class RiskBase(BaseModel):
    process_id: str
    description: str
    category: str | None = None
    probability: LevelType = "media"
    impact: LevelType = "media"
    priority: LevelType = "media"
    responsible_id: str | None = None
    status: StatusType = "aberto"
    due_date: datetime | None = None


class RiskCreate(RiskBase):
    pass


class RiskUpdate(BaseModel):
    description: str | None = None
    category: str | None = None
    probability: LevelType | None = None
    impact: LevelType | None = None
    priority: LevelType | None = None
    responsible_id: str | None = None
    status: StatusType | None = None
    due_date: datetime | None = None


class RiskRead(RiskBase):
    id: str
    severity: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
