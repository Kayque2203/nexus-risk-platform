from sqlalchemy.orm import Session

from app.repositories.action_repository import ActionRepository
from app.repositories.risk_repository import RiskRepository
from app.services.audit_service import AuditService
from app.schemas.action import ActionCreate, ActionUpdate
from app.models.action import Action


class ActionService:
    def __init__(self, db: Session):
        self.repository = ActionRepository(db)
        self.risk_repository = RiskRepository(db)
        self.audit = AuditService(db)

    def list_actions(self, skip: int = 0, limit: int = 100) -> list[Action]:
        return self.repository.list_all(skip=skip, limit=limit)

    def list_by_risk(self, risk_id: str) -> list[Action]:
        return self.repository.list_by_risk(risk_id)

    def get_action(self, action_id: str) -> Action | None:
        return self.repository.get_by_id(action_id)

    def create_action(self, data: ActionCreate, user_id: str | None = None) -> Action:
        risk = self.risk_repository.get_by_id(data.risk_id)
        if not risk:
            raise ValueError("Risco informado nao existe.")
        action = self.repository.create(data)
        self.audit.log_create(user_id, "Action", action.id)
        return action

    def update_action(self, action_id: str, data: ActionUpdate, user_id: str | None = None) -> Action | None:
        action = self.repository.get_by_id(action_id)
        if not action:
            return None

        before = {"status": action.status, "description": action.description}
        updated = self.repository.update(action, data)
        after = {"status": updated.status, "description": updated.description}

        self.audit.log_update(user_id, "Action", updated.id, before, after)
        return updated

    def delete_action(self, action_id: str, user_id: str | None = None) -> bool:
        action = self.repository.get_by_id(action_id)
        if not action:
            return False
        self.repository.delete(action)
        self.audit.log_delete(user_id, "Action", action_id)
        return True
