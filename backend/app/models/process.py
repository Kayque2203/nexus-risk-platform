import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


def generate_uuid():
    return str(uuid.uuid4())


class Process(Base):
    __tablename__ = "processes"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    department = Column(String, nullable=True)

    # Responsavel: referencia um usuario existente. Nullable porque
    # um processo pode ser criado antes de ter um responsavel definido.
    responsible_id = Column(String, ForeignKey("users.id"), nullable=True)
    responsible = relationship("User")

    # Valores livres por enquanto (string), nao enum do banco -- assim
    # podemos adicionar novos status/prioridades sem migration.
    # Validacao de valores permitidos fica na camada de schema (Pydantic).
    status = Column(String, nullable=False, default="aberto")
    priority = Column(String, nullable=False, default="media")

    due_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
