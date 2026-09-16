import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


def generate_uuid():
    return str(uuid.uuid4())


class Action(Base):
    __tablename__ = "actions"

    id = Column(String, primary_key=True, default=generate_uuid)

    # Toda acao pertence a um risco -- relacao obrigatoria, um risco
    # pode ter multiplas acoes de mitigacao.
    risk_id = Column(String, ForeignKey("risks.id"), nullable=False)
    risk = relationship("Risk")

    description = Column(Text, nullable=False)
    responsible_id = Column(String, ForeignKey("users.id"), nullable=True)
    responsible = relationship("User")

    status = Column(String, nullable=False, default="aberta")
    due_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
