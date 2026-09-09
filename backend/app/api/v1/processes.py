from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.process import ProcessCreate, ProcessRead, ProcessUpdate
from app.services.process_service import ProcessService
from app.models.user import User

router = APIRouter(prefix="/api/processes", tags=["Processes"])


@router.get("/", response_model=list[ProcessRead])
def list_processes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProcessService(db)
    return service.list_processes(skip=skip, limit=limit)


@router.get("/{process_id}", response_model=ProcessRead)
def get_process(
    process_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProcessService(db)
    process = service.get_process(process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Processo nao encontrado.")
    return process


@router.post("/", response_model=ProcessRead, status_code=201)
def create_process(
    data: ProcessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProcessService(db)
    return service.create_process(data, user_id=current_user.id)


@router.patch("/{process_id}", response_model=ProcessRead)
def update_process(
    process_id: str,
    data: ProcessUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProcessService(db)
    process = service.update_process(process_id, data, user_id=current_user.id)
    if not process:
        raise HTTPException(status_code=404, detail="Processo nao encontrado.")
    return process


@router.delete("/{process_id}", status_code=204)
def delete_process(
    process_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProcessService(db)
    deleted = service.delete_process(process_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Processo nao encontrado.")
