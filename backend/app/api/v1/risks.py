from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.risk import RiskCreate, RiskRead, RiskUpdate
from app.services.risk_service import RiskService
from app.models.user import User

router = APIRouter(prefix="/api/risks", tags=["Risks"])


@router.get("/", response_model=list[RiskRead])
def list_risks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RiskService(db)
    return service.list_risks(skip=skip, limit=limit)


@router.get("/{risk_id}", response_model=RiskRead)
def get_risk(
    risk_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RiskService(db)
    risk = service.get_risk(risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risco nao encontrado.")
    return risk


@router.post("/", response_model=RiskRead, status_code=201)
def create_risk(
    data: RiskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RiskService(db)
    try:
        return service.create_risk(data, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{risk_id}", response_model=RiskRead)
def update_risk(
    risk_id: str,
    data: RiskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RiskService(db)
    risk = service.update_risk(risk_id, data, user_id=current_user.id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risco nao encontrado.")
    return risk


@router.delete("/{risk_id}", status_code=204)
def delete_risk(
    risk_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RiskService(db)
    deleted = service.delete_risk(risk_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Risco nao encontrado.")
