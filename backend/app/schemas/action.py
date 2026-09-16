from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict

StatusType = Literal["aberta", "em_andamento", "concluida", "atrasada", "cancelada"]


class ActionBase(BaseModel):
    risk_id: str
    description: str
    responsible_id: str | None = None
    status: StatusType = "aberta"
    due_date: datetime | None = None


class ActionCreate(ActionBase):
    pass


class ActionUpdate(BaseModel):
    description: str | None = None
    responsible_id: str | None = None
    status: StatusType | None = None
    due_date: datetime | None = None


class ActionRead(ActionBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
