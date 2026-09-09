from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: str | None,
        entity_type: str,
        entity_id: str,
        action: str,
        changes: str | None,
    ) -> AuditLog:
        log = AuditLog(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            changes=changes,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def list_all(self, skip: int = 0, limit: int = 100) -> list[AuditLog]:
        return (
            self.db.query(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_entity(self, entity_type: str, entity_id: str) -> list[AuditLog]:
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
            .order_by(AuditLog.created_at.desc())
            .all()
        )
