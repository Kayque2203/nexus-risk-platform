from sqlalchemy.orm import Session
from app.models.action import Action
from app.schemas.action import ActionCreate, ActionUpdate


class ActionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, action_id: str) -> Action | None:
        return self.db.query(Action).filter(Action.id == action_id).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> list[Action]:
        return self.db.query(Action).offset(skip).limit(limit).all()

    def list_by_risk(self, risk_id: str) -> list[Action]:
        return self.db.query(Action).filter(Action.risk_id == risk_id).all()

    def create(self, data: ActionCreate) -> Action:
        action = Action(**data.model_dump())
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        return action

    def update(self, action: Action, data: ActionUpdate) -> Action:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(action, field, value)
        self.db.commit()
        self.db.refresh(action)
        return action

    def delete(self, action: Action) -> None:
        self.db.delete(action)
        self.db.commit()
