from sqlalchemy.orm import Session
from app.repositories.audit_log_repository import AuditLogRepository


class AuditService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = AuditLogRepository(db)

    def log_create(self, user_id: str | None, entity_type: str, entity_id: str):
        self.repository.create(user_id, entity_type, entity_id, "create", "Registro criado.")

    def log_update(self, user_id, entity_type, entity_id, before: dict, after: dict):
        diffs = [f"{f}: {before.get(f)} -> {v}" for f, v in after.items() if before.get(f) != v]
        changes_text = "; ".join(diffs) if diffs else "Nenhuma alteracao detectada."
        self.repository.create(user_id, entity_type, entity_id, "update", changes_text)

    def log_delete(self, user_id, entity_type, entity_id):
        self.repository.create(user_id, entity_type, entity_id, "delete", "Registro excluido.")

    def list_logs(self, skip: int = 0, limit: int = 100):
        logs = self.repository.list_all(skip=skip, limit=limit)
        result = []
        for log in logs:
            result.append({
                "id": log.id,
                "user_id": log.user_id,
                "user_name": log.user.name if log.user else None,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "action": log.action,
                "changes": log.changes,
                "created_at": log.created_at,
            })
        return result
