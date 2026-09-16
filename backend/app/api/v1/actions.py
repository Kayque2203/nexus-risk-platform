from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.action import ActionCreate, ActionRead, ActionUpdate
from app.services.action_service import ActionService
from app.models.user import User

router = APIRouter(prefix="/api/actions", tags=["Actions"])


@router.get("/", response_model=list[ActionRead])
def list_actions(
    skip: int = 0,
    limit: int = 100,
    risk_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ActionService(db)
    if risk_id:
        return service.list_by_risk(risk_id)
    return service.list_actions(skip=skip, limit=limit)


@router.get("/{action_id}", response_model=ActionRead)
def get_action(
    action_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ActionService(db)
    action = service.get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Acao nao encontrada.")
    return action


@router.post("/", response_model=ActionRead, status_code=201)
def create_action(
    data: ActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ActionService(db)
    try:
        return service.create_action(data, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{action_id}", response_model=ActionRead)
def update_action(
    action_id: str,
    data: ActionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ActionService(db)
    action = service.update_action(action_id, data, user_id=current_user.id)
    if not action:
        raise HTTPException(status_code=404, detail="Acao nao encontrada.")
    return action


@router.delete("/{action_id}", status_code=204)
def delete_action(
    action_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ActionService(db)
    deleted = service.delete_action(action_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Acao nao encontrada.")
