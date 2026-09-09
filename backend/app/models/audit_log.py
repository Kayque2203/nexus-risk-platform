import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


def generate_uuid():
    return str(uuid.uuid4())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)

    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    user = relationship("User")

    # Nome da entidade afetada ("Process", "Risk") e o id dela --
    # generico o suficiente para logar qualquer tipo de entidade futura
    # sem precisar de uma tabela de log por entidade.
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)

    action = Column(String, nullable=False)  # "create", "update", "delete"

    # Texto legivel descrevendo a mudanca, ex:
    # "status: aberto -> em_andamento"
    changes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
