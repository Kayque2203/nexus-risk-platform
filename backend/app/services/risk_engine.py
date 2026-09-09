"""Risk Engine: calcula a severidade de um risco a partir de sua
probabilidade e impacto, usando uma matriz de risco 4x4 -- o mesmo
modelo usado em frameworks de gestao de risco corporativo (ISO 31000).

A matriz nao e simetrica de proposito: um impacto critico pesa mais
que uma probabilidade critica isolada, refletindo que "consequencia"
tende a ser mais grave de ignorar do que "chance de acontecer"."""

RISK_MATRIX: dict[tuple[str, str], str] = {
    ("baixa", "baixa"): "baixa",
    ("baixa", "media"): "baixa",
    ("baixa", "alta"): "media",
    ("baixa", "critica"): "media",

    ("media", "baixa"): "baixa",
    ("media", "media"): "media",
    ("media", "alta"): "media",
    ("media", "critica"): "alta",

    ("alta", "baixa"): "media",
    ("alta", "media"): "media",
    ("alta", "alta"): "alta",
    ("alta", "critica"): "critica",

    ("critica", "baixa"): "media",
    ("critica", "media"): "alta",
    ("critica", "alta"): "critica",
    ("critica", "critica"): "critica",
}


def calculate_severity(probability: str, impact: str) -> str:
    """Retorna a severidade (baixa/media/alta/critica) para a combinacao
    de probabilidade e impacto informada. Lanca KeyError se algum dos
    dois valores nao for um nivel valido -- isso so aconteceria se o
    Pydantic Literal tivesse sido contornado, entao e um erro de
    programacao, nao de entrada do usuario."""
    return RISK_MATRIX[(probability, impact)]
