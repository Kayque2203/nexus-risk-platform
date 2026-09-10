import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime
from app.db.base_class import Base


def generate_uuid():
    return str(uuid.uuid4())


class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    id = Column(String, primary_key=True, default=generate_uuid)
    input_text = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    probability = Column(String, nullable=False)
    impact = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
