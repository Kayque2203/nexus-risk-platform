from sqlalchemy.orm import Session

from app.services.ai.keyword_analyzer import KeywordAnalyzer
from app.services.ai.analyzer_interface import AIAnalysisResult
from app.models.ai_analysis import AIAnalysis


class AIAnalysisService:
    """Orquestra a analise de texto: chama o analisador configurado,
    aplica um fallback seguro caso ele falhe por qualquer motivo, e
    persiste o resultado para rastreabilidade."""

    def __init__(self, db: Session):
        self.db = db
        # Trocar o analisador (ex: para uma implementacao baseada em
        # LLM) exige mudar APENAS esta linha -- nenhum outro codigo
        # do sistema precisa saber qual analisador esta sendo usado.
        self.analyzer = KeywordAnalyzer()

    def _fallback_result(self) -> AIAnalysisResult:
        """Resultado conservador retornado quando o analisador falha
        por qualquer motivo -- garante que a API nunca quebra por
        causa de um erro na camada de IA, apenas degrada com uma
        resposta generica e sinaliza isso claramente no campo 'reason'."""
        return AIAnalysisResult(
            category="Geral",
            probability="media",
            impact="media",
            severity="media",
            reason="Nao foi possivel processar o texto automaticamente. "
                   "Resultado padrao retornado como fallback.",
            recommended_action="Revisar manualmente e classificar o risco.",
        )

    def analyze_text(self, text: str) -> AIAnalysisResult:
        try:
            result = self.analyzer.analyze(text)
        except Exception:
            result = self._fallback_result()

        # Persiste toda analise feita, mesmo as que caíram no fallback --
        # rastreabilidade e um requisito explicito do projeto.
        record = AIAnalysis(
            input_text=text,
            category=result.category,
            probability=result.probability,
            impact=result.impact,
            severity=result.severity,
            reason=result.reason,
            recommended_action=result.recommended_action,
        )
        self.db.add(record)
        self.db.commit()

        return result
