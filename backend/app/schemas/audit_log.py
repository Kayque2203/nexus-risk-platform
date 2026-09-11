from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    id: str
    user_id: str | None = None
    user_name: str | None = None
    entity_type: str
    entity_id: str
    action: str
    changes: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
