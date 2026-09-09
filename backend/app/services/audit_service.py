from sqlalchemy.orm import Session
from app.repositories.audit_log_repository import AuditLogRepository


class AuditService:
    """Centraliza a criacao de registros de auditoria. Qualquer service
    que precise logar uma acao (Process, Risk, e futuros) usa esta
    mesma interface -- evita duplicar logica de formatacao de diff
    espalhada pelo codigo."""

    def __init__(self, db: Session):
        self.repository = AuditLogRepository(db)

    def log_create(self, user_id: str | None, entity_type: str, entity_id: str):
        self.repository.create(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action="create",
            changes="Registro criado.",
        )

    def log_update(
        self,
        user_id: str | None,
        entity_type: str,
        entity_id: str,
        before: dict,
        after: dict,
    ):
        """Gera um texto legivel comparando os campos que existiam antes
        e depois do update, no formato 'campo: valor_antigo -> valor_novo'.
        So inclui campos que de fato mudaram."""
        diffs = []
        for field, new_value in after.items():
            old_value = before.get(field)
            if old_value != new_value:
                diffs.append(f"{field}: {old_value} -> {new_value}")

        changes_text = "; ".join(diffs) if diffs else "Nenhuma alteracao detectada."

        self.repository.create(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action="update",
            changes=changes_text,
        )

    def log_delete(self, user_id: str | None, entity_type: str, entity_id: str):
        self.repository.create(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action="delete",
            changes="Registro excluido.",
        )

    def list_logs(self, skip: int = 0, limit: int = 100):
        return self.repository.list_all(skip=skip, limit=limit)
