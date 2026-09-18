from pydantic import BaseModel


class RisksBySeverity(BaseModel):
    baixa: int
    media: int
    alta: int
    critica: int


class DashboardStats(BaseModel):
    total_processes: int
    overdue_processes: int
    total_risks: int
    critical_risks: int
    overdue_risks: int
    risks_by_severity: RisksBySeverity
    top_risk_category: str | None = None
    top_risk_category_count: int = 0

