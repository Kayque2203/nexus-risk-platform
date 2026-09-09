from sqlalchemy.orm import Session

from app.repositories.risk_repository import RiskRepository
from app.repositories.process_repository import ProcessRepository
from app.schemas.risk import RiskCreate, RiskUpdate
from app.services.risk_engine import calculate_severity
from app.services.audit_service import AuditService
from app.models.risk import Risk


class RiskService:
    def __init__(self, db: Session):
        self.repository = RiskRepository(db)
        self.process_repository = ProcessRepository(db)
        self.audit = AuditService(db)

    def list_risks(self, skip: int = 0, limit: int = 100) -> list[Risk]:
        return self.repository.list_all(skip=skip, limit=limit)

    def get_risk(self, risk_id: str) -> Risk | None:
        return self.repository.get_by_id(risk_id)

    def create_risk(self, data: RiskCreate, user_id: str | None = None) -> Risk:
        process = self.process_repository.get_by_id(data.process_id)
        if not process:
            raise ValueError("Processo informado nao existe.")

        severity = calculate_severity(data.probability, data.impact)
        risk = self.repository.create(data, severity)
        self.audit.log_create(user_id, "Risk", risk.id)
        return risk

    def update_risk(
        self, risk_id: str, data: RiskUpdate, user_id: str | None = None
    ) -> Risk | None:
        risk = self.repository.get_by_id(risk_id)
        if not risk:
            return None

        before = {
            "status": risk.status,
            "probability": risk.probability,
            "impact": risk.impact,
            "severity": risk.severity,
        }

        updated = self.repository.update(risk, data)

        new_severity = calculate_severity(updated.probability, updated.impact)
        if new_severity != updated.severity:
            updated = self.repository.update_severity(updated, new_severity)

        after = {
            "status": updated.status,
            "probability": updated.probability,
            "impact": updated.impact,
            "severity": updated.severity,
        }

        self.audit.log_update(user_id, "Risk", updated.id, before, after)
        return updated

    def delete_risk(self, risk_id: str, user_id: str | None = None) -> bool:
        risk = self.repository.get_by_id(risk_id)
        if not risk:
            return False
        self.repository.delete(risk)
        self.audit.log_delete(user_id, "Risk", risk_id)
        return True
