from sqlalchemy.orm import Session

from app.core.security import pwd_context
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.models.user import User


class UserService:
    """Regras de negócio relacionadas a usuários. A camada de API
    nunca deve chamar o repository diretamente — sempre passa pelo
    service, que decide COMO e QUANDO os dados são manipulados."""

    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.repository.list_all(skip=skip, limit=limit)

    def get_user(self, user_id: str) -> User | None:
        return self.repository.get_by_id(user_id)

    def create_user(self, user_data: UserCreate) -> User:
        existing = self.repository.get_by_email(user_data.email)
        if existing:
            raise ValueError("Já existe um usuário com este e-mail.")

        hashed_password = pwd_context.hash(user_data.password)
        return self.repository.create(user_data, hashed_password)

    def authenticate(self, email: str, password: str) -> User | None:
        """Retorna o usuário se e-mail e senha forem válidos, senão None.
        Não diferenciamos 'e-mail não existe' de 'senha errada' na resposta
        da API — isso evita que um atacante descubra quais e-mails estão
        cadastrados no sistema (enumeration attack)."""
        user = self.repository.get_by_email(email)
        if not user:
            return None
        if not pwd_context.verify(password, user.hashed_password):
            return None
        return user
