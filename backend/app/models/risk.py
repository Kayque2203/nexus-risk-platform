import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


def generate_uuid():
    return str(uuid.uuid4())


class Risk(Base):
    __tablename__ = "risks"

    id = Column(String, primary_key=True, default=generate_uuid)

    # Todo risco pertence a um processo -- relacao obrigatoria.
    process_id = Column(String, ForeignKey("processes.id"), nullable=False)
    process = relationship("Process")

    description = Column(Text, nullable=False)
    category = Column(String, nullable=True)

    # Probabilidade e impacto como niveis (nao numeros) por simplicidade
    # no CRUD manual. A severidade sera calculada automaticamente pelo
    # Risk Engine na proxima fase, a partir desses dois campos.
    probability = Column(String, nullable=False, default="media")
    impact = Column(String, nullable=False, default="media")
    severity = Column(String, nullable=True)  # preenchido pelo Risk Engine

    priority = Column(String, nullable=False, default="media")
    responsible_id = Column(String, ForeignKey("users.id"), nullable=True)
    responsible = relationship("User")

    status = Column(String, nullable=False, default="aberto")
    due_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
