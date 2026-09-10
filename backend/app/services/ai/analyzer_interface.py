from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Literal


class AIAnalysisResult(BaseModel):
    """Formato padronizado que QUALQUER implementacao de analisador
    deve retornar -- seja este analisador baseado em palavras-chave,
    ou um LLM de verdade no futuro. Isso e o que garante que o
    sistema nao fica acoplado a uma tecnologia de IA especifica."""

    category: str
    probability: Literal["baixa", "media", "alta", "critica"]
    impact: Literal["baixa", "media", "alta", "critica"]
    severity: Literal["baixa", "media", "alta", "critica"]
    reason: str
    recommended_action: str


class AIAnalyzer(ABC):
    """Contrato que todo analisador de IA deve seguir. Trocar de
    implementacao (ex: para uma API de LLM) significa apenas criar
    uma nova classe que implementa este metodo -- nenhuma outra
    parte do sistema precisa mudar."""

    @abstractmethod
    def analyze(self, text: str) -> AIAnalysisResult:
        raise NotImplementedError
