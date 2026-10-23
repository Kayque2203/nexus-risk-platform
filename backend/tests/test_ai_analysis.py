# ---------- Melhorias da heuristica (dominio de qualidade e compliance) ----------

def test_keyword_analyzer_recognizes_supplier_risk_text():
    result = KeywordAnalyzer().analyze(
        "Fornecedor \u00fanico sem plano de conting\u00eancia para mat\u00e9ria-prima cr\u00edtica"
    )
    assert result.category == "Operacional"
    assert result.impact == "critica"


def test_keyword_analyzer_ignores_accents():
    with_accents = KeywordAnalyzer().analyze("Falha de sistema com indisponibilidade cr\u00edtica.")
    without_accents = KeywordAnalyzer().analyze("Falha de sistema com indisponibilidade critica.")
    assert with_accents == without_accents


def test_keyword_analyzer_critic_stem_matches_feminine_form():
    result = KeywordAnalyzer().analyze("Situacao critica na linha de producao.")
    assert result.impact == "alta"


def test_keyword_analyzer_recognizes_personal_data_in_spreadsheets():
    result = KeywordAnalyzer().analyze(
        "Dados pessoais de clientes armazenados em planilhas compartilhadas"
    )
    assert result.category == "Seguran\u00e7a"


def test_keyword_analyzer_recommended_action_has_accents():
    result = KeywordAnalyzer().analyze("Texto neutro sem indicadores especiais.")
    assert "revis\u00e3o" in result.recommended_action