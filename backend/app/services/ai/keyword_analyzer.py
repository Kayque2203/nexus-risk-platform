import re
import unicodedata

from app.services.ai.analyzer_interface import AIAnalyzer, AIAnalysisResult
from app.services.risk_engine import calculate_severity

# Todas as palavras-chave abaixo estao em minusculas e SEM acentos nem hifens,
# porque o texto de entrada passa por _normalize() antes da comparacao.
#
# Como o casamento funciona (_pattern):
# - O termo precisa comecar no INICIO de uma palavra: "bug" nao casa com
#   "debug" e "senha" nao casa com "desenha".
# - Termos longos (mais de 4 letras) funcionam como radicais: "critic" casa com
#   critico, critica, criticos; "recorrent" com recorrente, recorrentes.
# - Termos curtos (ate 4 letras) exigem a palavra inteira (aceitam plural com
#   "s"): "bug" casa com "bugs", mas "capa" nao casa com "capacidade".

# Termos de peso 1.
CATEGORY_KEYWORDS = {
    "Segurança": [
        "hacker", "senha", "phishing", "malware", "planilhas compartilhadas",
        "login compartilhado", "usuario generico", "perfil de acesso",
        "criptografia", "engenharia social",
    ],
    "Financeiro": [
        "prejuizo", "perda financeira", "multa", "pagamento indevido",
        "fraude", "orcamento", "custo adicional", "reembolso",
        "reajuste de preco", "inadimplencia", "desperdicio",
        "perda de receita", "custo elevado",
    ],
    "Compliance": [
        "processo judicial", "regulatorio", "lgpd", "auditoria externa",
        "penalidade", "contrato", "clausula", "anvisa",
        "versoes obsoletas", "sem treinamento", "sem registro formal",
        "verificacao de eficacia", "avaliacao de impacto",
        "inspecao", "auditoria interna", "gxp", "bpf", "capa",
    ],
    "Operacional": [
        "atraso", "retrabalho", "inconsistencia", "falha no processo",
        "interrupcao", "erro humano", "gargalo", "sobrecarga",
        "fornecedor", "contingencia", "materia prima", "desabastecimento",
        "ruptura de estoque", "calibracao", "reclamacoes", "desvio",
        "matriz de treinamento", "fora do prazo", "prazo vencido",
        "parada de linha", "falta de insumo",
    ],
    "Tecnologia": [
        "sistema fora do ar", "bug", "erro de sistema", "indisponibilidade",
        "instabilidade", "servidor", "banco de dados", "integracao falhou",
        "computadorizado", "backup", "vulnerabilidade", "falha de sistema",
        "restauracao",
    ],
}

# Termos de peso 2: sinais fortes, tipicos do dominio de qualidade, compliance
# e validacao de sistemas computadorizados. Um termo fica em UMA lista so.
CATEGORY_STRONG_KEYWORDS = {
    "Segurança": [
        "vazamento", "acesso indevido", "acesso nao autorizado", "invasao",
        "ransomware", "violacao de dados", "dados pessoais", "credenciais",
    ],
    "Financeiro": [],
    "Compliance": [
        "nao conformidade", "boas praticas de fabricacao", "rastreabilidade",
        "21 cfr",
    ],
    "Operacional": [],
    "Tecnologia": [
        "trilha de auditoria", "sistema validado", "integridade de dados",
        "validacao de sistema", "assinatura eletronica", "gamp",
        "perda de dados", "dados corrompidos",
    ],
}

PROBABILITY_BOOSTERS = [
    "recorrent", "recorrenc", "frequente", "novamente", "de novo",
    "toda semana", "constantemente", "repetidamente", "diversas vezes",
    "sempre", "mais de uma vez", "reincident", "diariamente", "todo dia",
    "todo mes", "varias vezes",
]

IMPACT_BOOSTERS = [
    "grave", "critic", "urgente", "vazamento", "perda financeira",
    "processo judicial", "multa", "parada total", "todos os clientes",
    "dados sensiveis", "irreversivel", "estrategic", "fornecedor unico",
    "sem plano de contingencia", "paralisacao", "desabastecimento",
    "seguranca do paciente", "risco a saude", "recall", "contaminacao",
    "interdicao",
]

# Atenuantes: reduzem um nivel. E o que permite a severidade "baixa".
PROBABILITY_ATTENUATORS = [
    "pontual", "isolad", "eventual", "ocasional", "raramente", "rara", "raro",
    "excepcional", "primeira vez", "unica vez",
]

IMPACT_ATTENUATORS = [
    "auxiliar", "menor", "pequen", "baixo impacto", "impacto baixo",
    "impacto minimo", "impacto limitado", "sem impacto", "nao afet",
    "sem relevancia", "pouco relevante",
]

# Palavras que negam um INCIDENTE logo antes dele ("sem vazamento",
# "nao houve fraude"). A negacao so vale para os termos de NEGATABLE_TERMS:
# a falta de um CONTROLE e o proprio risco ("sem trilha de auditoria",
# "sem avaliacao de impacto" continuam contando como risco).
NEGATORS = {"sem", "nao", "nenhum", "nenhuma", "nunca", "nem", "ausencia"}
NEGATION_WINDOW = 3  # palavras antes do termo, dentro da mesma frase

NEGATABLE_TERMS = {
    # Seguranca
    "vazamento", "acesso indevido", "acesso nao autorizado", "invasao",
    "hacker", "phishing", "malware", "ransomware", "violacao de dados",
    # Financeiro
    "prejuizo", "perda financeira", "multa", "pagamento indevido", "fraude",
    "custo adicional", "inadimplencia",
    # Compliance
    "processo judicial", "nao conformidade", "penalidade",
    # Operacional
    "atraso", "retrabalho", "inconsistencia", "falha no processo",
    "interrupcao", "erro humano", "gargalo", "sobrecarga",
    "desabastecimento", "ruptura de estoque", "reclamacoes", "desvio",
    # Tecnologia
    "sistema fora do ar", "bug", "erro de sistema", "indisponibilidade",
    "instabilidade", "integracao falhou", "vulnerabilidade",
    "falha de sistema", "perda de dados", "dados corrompidos",
    # Intensidade
    "grave", "critic", "urgente", "irreversivel", "paralisacao",
    "parada total", "dados sensiveis", "contaminacao", "recall",
    # Atenuantes tambem podem ser negados ("nao e pontual")
    "pontual", "isolad", "eventual", "ocasional", "auxiliar",
}

RECOMMENDED_ACTIONS = {
    "critica": "Escalar imediatamente para o responsável e abrir plano de ação emergencial.",
    "alta": "Priorizar investigação nas próximas 48h e definir responsável pela mitigação.",
    "media": "Incluir na próxima revisão de riscos do departamento responsável.",
    "baixa": "Monitorar periodicamente; nenhuma ação imediata necessária.",
}

LEVELS = ["baixa", "media", "alta", "critica"]

_CLAUSE_BREAK = re.compile(r"[.;:!?,()]")
_PATTERN_CACHE: dict[str, re.Pattern] = {}


def _normalize(text: str) -> str:
    """Minusculas, sem acentos, hifen vira espaco e espacos colapsados."""
    decomposed = unicodedata.normalize("NFKD", text.lower())
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return " ".join(stripped.replace("-", " ").split())


def _pattern(term: str) -> re.Pattern:
    pattern = _PATTERN_CACHE.get(term)
    if pattern is None:
        suffix = r"s?(?![a-z0-9])" if len(term) <= 4 else ""
        pattern = re.compile(r"(?<![a-z0-9])" + re.escape(term) + suffix)
        _PATTERN_CACHE[term] = pattern
    return pattern


def _is_negated(text: str, start: int) -> bool:
    """True se ha uma palavra de negacao nas ultimas palavras da mesma frase."""
    clause = _CLAUSE_BREAK.split(text[:start])[-1]
    return any(word in NEGATORS for word in clause.split()[-NEGATION_WINDOW:])


def _has_hit(text: str, term: str) -> bool:
    negatable = term in NEGATABLE_TERMS
    for match in _pattern(term).finditer(text):
        if not negatable or not _is_negated(text, match.start()):
            return True
    return False


def _count_matches(text: str, keywords: list[str]) -> int:
    return sum(1 for kw in keywords if _has_hit(text, kw))


def _score_category(text: str, category: str) -> tuple[int, int, int]:
    """Devolve (pontuacao, termos fortes, total de termos) da categoria."""
    weak = _count_matches(text, CATEGORY_KEYWORDS[category])
    strong = _count_matches(text, CATEGORY_STRONG_KEYWORDS.get(category, []))
    return weak + 2 * strong, strong, weak + strong


def _level(boost_hits: int, attenuator_hits: int) -> str:
    """Padrao 'media'; cada reforco sobe (ate 2 niveis); atenuante desce 1."""
    index = 1 + min(boost_hits, 2) - min(attenuator_hits, 1)
    return LEVELS[max(0, min(index, 3))]


class KeywordAnalyzer(AIAnalyzer):
    def analyze(self, text: str) -> AIAnalysisResult:
        normalized = _normalize(text)

        scores = {category: _score_category(normalized, category) for category in CATEGORY_KEYWORDS}
        # Desempate: maior pontuacao, depois mais termos fortes; se ainda
        # empatar, vale a ordem de CATEGORY_KEYWORDS (max devolve o primeiro).
        best_category = max(scores, key=lambda c: (scores[c][0], scores[c][1]))
        best_score, _, best_terms = scores[best_category]
        if best_score == 0:
            best_category = "Geral"

        probability_hits = _count_matches(normalized, PROBABILITY_BOOSTERS)
        probability_softeners = _count_matches(normalized, PROBABILITY_ATTENUATORS)
        impact_hits = _count_matches(normalized, IMPACT_BOOSTERS)
        impact_softeners = _count_matches(normalized, IMPACT_ATTENUATORS)

        probability = _level(probability_hits, probability_softeners)
        impact = _level(impact_hits, impact_softeners)
        severity = calculate_severity(probability, impact)

        reason = (
            f"Categoria identificada como '{best_category}' com base em "
            f"{best_terms} termo(s) reconhecido(s) no texto. "
            f"Foram encontrados {probability_hits} indicativo(s) de recorrência "
            f"e {impact_hits} indicativo(s) de impacto significativo."
        )
        if probability_softeners or impact_softeners:
            reason += (
                f" Atenuantes identificados: {probability_softeners} na "
                f"probabilidade e {impact_softeners} no impacto, o que reduziu o nível."
            )

        return AIAnalysisResult(
            category=best_category,
            probability=probability,
            impact=impact,
            severity=severity,
            reason=reason,
            recommended_action=RECOMMENDED_ACTIONS[severity],
        )