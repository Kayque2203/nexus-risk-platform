import re
from app.services.ai.analyzer_interface import AIAnalyzer, AIAnalysisResult
from app.services.risk_engine import calculate_severity

CATEGORY_KEYWORDS = {
    "Segurança": [
        "vazamento", "acesso indevido", "invasao", "hacker", "senha",
        "dados pessoais", "phishing", "malware", "violacao de dados",
    ],
    "Financeiro": [
        "prejuizo", "perda financeira", "multa", "pagamento indevido",
        "fraude", "orcamento", "custo adicional", "reembolso",
    ],
    "Compliance": [
        "processo judicial", "regulatorio", "lgpd", "auditoria externa",
        "nao conformidade", "penalidade", "contrato", "clausula",
    ],
    "Operacional": [
        "atraso", "retrabalho", "inconsistencia", "falha no processo",
        "interrupcao", "erro humano", "gargalo", "sobrecarga",
    ],
    "Tecnologia": [
        "sistema fora do ar", "bug", "erro de sistema", "indisponibilidade",
        "instabilidade", "servidor", "banco de dados", "integracao falhou",
    ],
}

PROBABILITY_BOOSTERS = [
    "recorrente", "frequente", "novamente", "de novo", "toda semana",
    "constantemente", "repetidamente", "diversas vezes", "sempre",
]

IMPACT_BOOSTERS = [
    "grave", "critico", "urgente", "vazamento", "perda financeira",
    "processo judicial", "multa", "parada total", "todos os clientes",
    "dados sensiveis", "irreversivel",
]

RECOMMENDED_ACTIONS = {
    "critica": "Escalar imediatamente para o responsavel e abrir plano de acao emergencial.",
    "alta": "Priorizar investigacao nas proximas 48h e definir responsavel pela mitigacao.",
    "media": "Incluir na proxima revisao de riscos do departamento responsavel.",
    "baixa": "Monitorar periodicamente; nenhuma acao imediata necessaria.",
}


def _normalize(text: str) -> str:
    text = text.lower()
    replacements = {
        "á": "a", "à": "a", "ã": "a", "â": "a",
        "é": "e", "ê": "e",
        "í": "i",
        "ó": "o", "õ": "o", "ô": "o",
        "ú": "u",
        "ç": "c",
    }
    for accented, plain in replacements.items():
        text = text.replace(accented, plain)
    return text


def _count_matches(text: str, keywords: list[str]) -> int:
    return sum(1 for kw in keywords if kw in text)


class KeywordAnalyzer(AIAnalyzer):
    def analyze(self, text: str) -> AIAnalysisResult:
        normalized = _normalize(text)

        category_scores = {
            category: _count_matches(normalized, keywords)
            for category, keywords in CATEGORY_KEYWORDS.items()
        }
        best_category = max(category_scores, key=category_scores.get)
        # Guarda a contagem ANTES de possivelmente trocar o nome da
        # categoria para "Geral" -- corrige um KeyError que ocorria
        # quando nenhuma palavra-chave era encontrada (categoria_scores
        # nao tem uma chave "Geral").
        best_category_score = category_scores[best_category]
        if best_category_score == 0:
            best_category = "Geral"

        probability_hits = _count_matches(normalized, PROBABILITY_BOOSTERS)
        if probability_hits >= 2:
            probability = "critica"
        elif probability_hits == 1:
            probability = "alta"
        else:
            probability = "media"

        impact_hits = _count_matches(normalized, IMPACT_BOOSTERS)
        if impact_hits >= 2:
            impact = "critica"
        elif impact_hits == 1:
            impact = "alta"
        else:
            impact = "media"

        severity = calculate_severity(probability, impact)

        reason = (
            f"Categoria identificada como '{best_category}' com base em "
            f"{best_category_score} termo(s) reconhecido(s) no texto. "
            f"Foram encontrados {probability_hits} indicativo(s) de recorrencia "
            f"e {impact_hits} indicativo(s) de impacto significativo."
        )

        return AIAnalysisResult(
            category=best_category,
            probability=probability,
            impact=impact,
            severity=severity,
            reason=reason,
            recommended_action=RECOMMENDED_ACTIONS[severity],
        )
