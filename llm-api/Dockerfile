# llm-api/Dockerfile
#
# Build-Kontext muss das Repo-Root sein (wegen LLM_Client als Abhängigkeit):
#
#   docker build -f llm-api/Dockerfile -t llm-api .
#
# Oder über docker-compose (Build-Kontext wird automatisch auf .. gesetzt):
#
#   docker compose -f llm-api/docker-compose.yml up --build

FROM python:3.12-slim

WORKDIR /app

# LLM_Client installieren (openai + anthropic + google-generativeai)
COPY LLM_Client/ ./LLM_Client/
COPY pyproject.toml ./
RUN pip install --no-cache-dir ".[all]"

# API-Abhängigkeiten installieren
COPY llm-api/requirements.txt ./llm-api/
RUN pip install --no-cache-dir -r llm-api/requirements.txt

# API-Code kopieren
COPY llm-api/api.py ./llm-api/

WORKDIR /app/llm-api

EXPOSE 8000

# config.json wird per Volume eingebunden — niemals ins Image!
# Pfad über Umgebungsvariable LLM_CONFIG steuerbar.
ENV LLM_CONFIG=/app/LLM_Client/config.json

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
