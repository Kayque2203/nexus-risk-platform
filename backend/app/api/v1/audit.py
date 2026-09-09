from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.audit_log import AuditLogRead
from app.services.audit_service import AuditService
from app.models.user import User

router = APIRouter(prefix="/api/audit-logs", tags=["Audit"])


@router.get("/", response_model=list[AuditLogRead])
def list_audit_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AuditService(db)
    return service.list_logs(skip=skip, limit=limit)
