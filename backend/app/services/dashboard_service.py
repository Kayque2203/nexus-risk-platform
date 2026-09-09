from datetime import datetime
from sqlalchemy.orm import Session

from app.repositories.process_repository import ProcessRepository
from app.repositories.risk_repository import RiskRepository

PROCESS_CLOSED_STATUSES = {"concluido", "cancelado"}
RISK_CLOSED_STATUSES = {"mitigado", "cancelado", "aceito"}


class DashboardService:
    """Agrega dados de processos e riscos em indicadores resumidos.
    Para o volume de dados de um MVP, calcular em Python sobre listas
    ja carregadas e mais simples e legivel do que SQL de agregacao --
    isso pode ser revisitado com queries agregadas se o volume crescer."""

    def __init__(self, db: Session):
        self.process_repo = ProcessRepository(db)
        self.risk_repo = RiskRepository(db)

    def get_stats(self) -> dict:
        processes = self.process_repo.list_all(limit=10000)
        risks = self.risk_repo.list_all(limit=10000)
        now = datetime.utcnow()

        overdue_processes = sum(
            1 for p in processes
            if p.due_date and p.due_date < now and p.status not in PROCESS_CLOSED_STATUSES
        )
        overdue_risks = sum(
            1 for r in risks
            if r.due_date and r.due_date < now and r.status not in RISK_CLOSED_STATUSES
        )

        risks_by_severity = {"baixa": 0, "media": 0, "alta": 0, "critica": 0}
        for r in risks:
            if r.severity in risks_by_severity:
                risks_by_severity[r.severity] += 1

        return {
            "total_processes": len(processes),
            "overdue_processes": overdue_processes,
            "total_risks": len(risks),
            "critical_risks": risks_by_severity["critica"],
            "overdue_risks": overdue_risks,
            "risks_by_severity": risks_by_severity,
        }
