from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
    """Encapsula todo acesso à tabela users. Nenhuma outra parte do
    sistema deve montar queries SQLAlchemy para User diretamente —
    isso mantém a lógica de acesso a dados em um único lugar,
    facilitando testes e futura troca de banco."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def create(self, user_data: UserCreate, hashed_password: str) -> User:
        user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_data.role,
            department=user_data.department,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
