from sqlalchemy.orm import Session
from app.models.risk import Risk
from app.schemas.risk import RiskCreate, RiskUpdate


class RiskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, risk_id: str) -> Risk | None:
        return self.db.query(Risk).filter(Risk.id == risk_id).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> list[Risk]:
        return self.db.query(Risk).offset(skip).limit(limit).all()

    def list_by_process(self, process_id: str) -> list[Risk]:
        return self.db.query(Risk).filter(Risk.process_id == process_id).all()

    def create(self, data: RiskCreate, severity: str) -> Risk:
        risk = Risk(**data.model_dump(), severity=severity)
        self.db.add(risk)
        self.db.commit()
        self.db.refresh(risk)
        return risk

    def update(self, risk: Risk, data: RiskUpdate) -> Risk:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(risk, field, value)
        self.db.commit()
        self.db.refresh(risk)
        return risk

    def update_severity(self, risk: Risk, severity: str) -> Risk:
        risk.severity = severity
        self.db.commit()
        self.db.refresh(risk)
        return risk

    def delete(self, risk: Risk) -> None:
        self.db.delete(risk)
        self.db.commit()
