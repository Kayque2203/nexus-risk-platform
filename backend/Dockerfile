FROM python:3.12-slim

WORKDIR /app

# Copia so o requirements primeiro -- aproveita cache de camadas do
# Docker: se o codigo mudar mas as dependencias nao, o rebuild e rapido.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

EXPOSE 8000

# Em producao, rodar as migrations antes de subir o servidor.
CMD ["sh", "-c", "python -m alembic upgrade head && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]
