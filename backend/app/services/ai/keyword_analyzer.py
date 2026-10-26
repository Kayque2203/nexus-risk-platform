import unicodedata

from app.services.ai.analyzer_interface import AIAnalyzer, AIAnalysisResult
from app.services.risk_engine import calculate_severity

# Todas as palavras-chave abaixo estao em minusculas e SEM acentos nem hifens,
# porque o texto de entrada passa por _normalize() antes da comparacao.
# Radicais (ex: "critic") casam com varias flexoes: critico, critica, criticos.

CATEGORY_KEYWORDS = {
    "Segurança": [
        "vazamento", "acesso indevido", "acesso nao autorizado", "invasao",
        "hacker", "senha", "credenciais", "dados pessoais", "phishing",
        "malware", "ransomware", "violacao de dados", "planilhas compartilhadas",
    ],
    "Financeiro": [
        "prejuizo", "perda financeira", "multa", "pagamento indevido",
        "fraude", "orcamento", "custo adicional", "reembolso",
        "reajuste de preco", "inadimplencia",
    ],
    "Compliance": [
        "processo judicial", "regulatorio", "lgpd", "auditoria externa",
        "nao conformidade", "penalidade", "contrato", "clausula",
        "anvisa", "boas praticas de fabricacao", "rastreabilidade",
        "versoes obsoletas", "sem treinamento", "sem registro formal",
        "verificacao de eficacia", "avaliacao de impacto",
    ],
    "Operacional": [
        "atraso", "retrabalho", "inconsistencia", "falha no processo",
        "interrupcao", "erro humano", "gargalo", "sobrecarga",
        "fornecedor", "contingencia", "materia prima", "desabastecimento",
        "ruptura de estoque", "calibracao", "reclamacoes", "desvio",
        "matriz de treinamento",
    ],
    "Tecnologia": [
        "sistema fora do ar", "bug", "erro de sistema", "indisponibilidade",
        "instabilidade", "servidor", "banco de dados", "integracao falhou",
        "trilha de auditoria", "sistema validado", "computadorizado",
        "backup", "vulnerabilidade", "falha de sistema",
    ],
}

PROBABILITY_BOOSTERS = [
    "recorrent", "recorrenc", "frequente", "novamente", "de novo",
    "toda semana", "constantemente", "repetidamente", "diversas vezes",
    "sempre", "mais de uma vez", "reincident",
]

IMPACT_BOOSTERS = [
    "grave", "critic", "urgente", "vazamento", "perda financeira",
    "processo judicial", "multa", "parada total", "todos os clientes",
    "dados sensiveis", "irreversivel", "estrategic", "fornecedor unico",
    "sem plano de contingencia", "paralisacao", "desabastecimento",
]

RECOMMENDED_ACTIONS = {
    "critica": "Escalar imediatamente para o responsável e abrir plano de ação emergencial.",
    "alta": "Priorizar investigação nas próximas 48h e definir responsável pela mitigação.",
    "media": "Incluir na próxima revisão de riscos do departamento responsável.",
    "baixa": "Monitorar periodicamente; nenhuma ação imediata necessária.",
}


def _normalize(text: str) -> str:
    """Minusculas, sem acentos, hifen vira espaco e espacos colapsados."""
    decomposed = unicodedata.normalize("NFKD", text.lower())
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return " ".join(stripped.replace("-", " ").split())


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
        # quando nenhuma palavra-chave era encontrada (category_scores
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
            f"Foram encontrados {probability_hits} indicativo(s) de recorrência "
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