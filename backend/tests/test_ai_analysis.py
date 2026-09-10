from app.services.ai.keyword_analyzer import KeywordAnalyzer
from app.services.ai_analysis_service import AIAnalysisService
from app.models.ai_analysis import AIAnalysis


# ---------- Testes do endpoint (integracao) ----------

def test_analyze_requires_auth(client):
    response = client.post("/api/ai/analyze", json={"text": "qualquer texto"})
    assert response.status_code == 401


def test_analyze_security_text(client, auth_headers):
    response = client.post(
        "/api/ai/analyze",
        json={"text": "Houve um vazamento de dados sensíveis por acesso indevido."},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "Segurança"
    assert "reason" in data
    assert "recommended_action" in data


def test_analyze_operational_text_with_recurrence(client, auth_headers):
    response = client.post(
        "/api/ai/analyze",
        json={"text": "Foi identificado atraso recorrente no processo, acontece toda semana."},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "Operacional"
    # Duas palavras de recorrencia ("recorrente", "toda semana") devem
    # elevar a probabilidade ao nivel mais alto da escala.
    assert data["probability"] == "critica"


def test_analyze_generic_text_falls_back_to_geral(client, auth_headers):
    response = client.post(
        "/api/ai/analyze",
        json={"text": "Texto sem nenhuma palavra-chave reconhecida pelo sistema."},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["category"] == "Geral"


def test_analyze_persists_record(client, auth_headers, db_session):
    client.post(
        "/api/ai/analyze",
        json={"text": "Risco de vazamento de dados."},
        headers=auth_headers,
    )
    records = db_session.query(AIAnalysis).all()
    assert len(records) == 1
    assert records[0].category == "Segurança"


# ---------- Testes unitarios do analisador (sem API) ----------

def test_keyword_analyzer_returns_valid_severity_levels():
    analyzer = KeywordAnalyzer()
    result = analyzer.analyze("Sistema fora do ar, indisponibilidade critica e urgente.")
    assert result.severity in ["baixa", "media", "alta", "critica"]
    assert result.category == "Tecnologia"


def test_keyword_analyzer_severity_matches_risk_engine():
    """Garante que a severidade retornada pelo analisador de IA e
    EXATAMENTE a mesma que o Risk Engine calcularia para a mesma
    combinacao de probabilidade/impacto -- nao pode haver dois
    'motores de severidade' divergentes no sistema."""
    from app.services.risk_engine import calculate_severity

    analyzer = KeywordAnalyzer()
    result = analyzer.analyze("Texto neutro sem indicadores especiais.")
    expected_severity = calculate_severity(result.probability, result.impact)
    assert result.severity == expected_severity
