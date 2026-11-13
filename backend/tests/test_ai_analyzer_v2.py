import pytest

from app.services.ai.keyword_analyzer import KeywordAnalyzer
from app.services.risk_engine import calculate_severity


def analyze(text):
    return KeywordAnalyzer().analyze(text)


# ---------- Severidade baixa: atenuantes ----------

def test_isolated_minor_event_produces_low_severity():
    result = analyze(
        "Atraso pontual na emiss\u00e3o do certificado de calibra\u00e7\u00e3o de equipamento auxiliar"
    )
    assert result.category == "Operacional"
    assert result.probability == "baixa"
    assert result.impact == "baixa"
    assert result.severity == "baixa"


def test_recurrence_and_attenuator_cancel_out():
    result = analyze("Atraso recorrente, por\u00e9m pontual no setor.")
    assert result.probability == "media"


def test_negated_attenuator_does_not_lower_level():
    result = analyze("O desvio n\u00e3o \u00e9 pontual.")
    assert result.probability == "media"


# ---------- Negacao de incidentes ----------

def test_negated_incident_is_not_counted():
    result = analyze("Auditoria conclu\u00edda sem vazamento de dados.")
    assert result.category == "Geral"
    assert result.impact == "media"


def test_negated_critical_does_not_raise_impact():
    assert analyze("A situa\u00e7\u00e3o n\u00e3o \u00e9 cr\u00edtica.").impact == "media"


def test_negation_does_not_cross_sentences():
    result = analyze("Sem falha na entrega. Atraso recorrente no envio.")
    assert result.category == "Operacional"
    assert result.probability == "alta"


def test_missing_control_still_counts_as_risk():
    result = analyze("Sistema sem trilha de auditoria para dados cr\u00edticos.")
    assert result.category == "Tecnologia"
    assert result.impact == "alta"


def test_missing_impact_assessment_still_counts_as_risk():
    result = analyze("Mudan\u00e7a implementada sem avalia\u00e7\u00e3o de impacto pr\u00e9via.")
    assert result.category == "Compliance"
    assert result.impact == "media"


# ---------- Casamento por inicio de palavra ----------

def test_short_term_does_not_match_inside_other_word():
    assert analyze("Rotina de debug da equipe.").category == "Geral"


def test_short_term_matches_plural():
    assert analyze("Foram encontrados bugs no m\u00f3dulo.").category == "Tecnologia"


def test_term_does_not_match_in_the_middle_of_a_word():
    assert analyze("Ele desenha o fluxo do processo.").category == "Geral"


def test_short_term_requires_whole_word():
    assert analyze("A capacidade da linha \u00e9 suficiente.").category == "Geral"


# ---------- Pesos e desempate ----------

def test_strong_term_wins_a_tie():
    # Financeiro: multa + fraude = 2 pontos; Tecnologia: integridade de dados = 2 pontos.
    # Empate de pontuacao, mas Tecnologia tem termo forte.
    result = analyze("Integridade de dados afetada com multa e fraude.")
    assert result.category == "Tecnologia"


def test_validation_domain_text_is_technology():
    result = analyze("Perda de integridade de dados no sistema validado.")
    assert result.category == "Tecnologia"


# ---------- Regressoes ----------

def test_supplier_example_validated_in_production_is_unchanged():
    result = analyze(
        "Fornecedor \u00fanico sem plano de conting\u00eancia para mat\u00e9ria-prima cr\u00edtica"
    )
    assert result.category == "Operacional"
    assert result.probability == "media"
    assert result.impact == "critica"
    assert result.severity == "alta"


@pytest.mark.parametrize(
    "text",
    [
        "Texto neutro sem indicadores especiais.",
        "Atraso recorrente, acontece toda semana, com impacto cr\u00edtico e vazamento.",
        "Risco pontual e isolado de baixo impacto.",
    ],
)
def test_severity_always_matches_risk_engine(text):
    result = analyze(text)
    assert result.severity == calculate_severity(result.probability, result.impact)


def test_reason_mentions_attenuators_only_when_present():
    assert "Atenuantes" not in analyze("Texto neutro sem indicadores especiais.").reason
    assert "Atenuantes" in analyze("Atraso pontual no setor.").reason