from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService
from app.models.user import User

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=list[UserRead])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    return service.list_users(skip=skip, limit=limit)


@router.post("/", response_model=UserRead, status_code=201)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Criação de usuário continua pública por enquanto (não exige login) —
    # faz sentido, já que é assim que o primeiro usuário do sistema existe.
    service = UserService(db)
    try:
        return service.create_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
