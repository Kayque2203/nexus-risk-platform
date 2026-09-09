from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict

# Literal restringe os valores aceitos -- a API rejeita automaticamente
# qualquer status/prioridade fora dessa lista, com erro 422 claro.
StatusType = Literal["aberto", "em_andamento", "concluido", "atrasado", "cancelado"]
PriorityType = Literal["baixa", "media", "alta", "critica"]


class ProcessBase(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None
    department: str | None = None
    responsible_id: str | None = None
    status: StatusType = "aberto"
    priority: PriorityType = "media"
    due_date: datetime | None = None


class ProcessCreate(ProcessBase):
    pass


class ProcessUpdate(BaseModel):
    """Todos os campos opcionais -- permite atualizar so o que mudou
    (PATCH), sem exigir reenviar o objeto inteiro."""
    name: str | None = None
    description: str | None = None
    category: str | None = None
    department: str | None = None
    responsible_id: str | None = None
    status: StatusType | None = None
    priority: PriorityType | None = None
    due_date: datetime | None = None


class ProcessRead(ProcessBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
