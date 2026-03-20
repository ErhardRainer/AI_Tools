# OpenAI / Media AI Toolkit

Python-Tools für OpenAI und weitere KI-Provider: Textgenerierung, Bildgenerierung, und mehr.

## Module

| Modul | Beschreibung | Provider |
|---|---|---|
| [`LLM_Client/`](LLM_Client/README.md) | Text → Text | OpenAI, Claude, Gemini, Grok, Kimi, DeepSeek, Groq, Mistral |
| [`ImageGen/`](ImageGen/README.md) | Text → Bild | DALL-E, Google Imagen, Stability AI, fal.ai FLUX |
| [`llm-api/`](llm-api/README.md) | REST-API für alle Module | FastAPI, Docker |
| [`Assistant_AI/`](Assistant_AI/) | OpenAI Assistants API | Notebook-Referenzimplementierung |

## Schnellstart

```bash
# Alles installieren
pip install ".[all]"
pip install openai  # für DALL-E und LLM

# Konfiguration
cp LLM_Client/config.template.json LLM_Client/config.json
cp ImageGen/config.template.json   ImageGen/config.json
# API-Keys eintragen

# Text generieren
llm-client --config LLM_Client/config.json --provider openai

# Bild generieren
image-gen --config ImageGen/config.json --prompt "A sunset over mountains" --output out.png

# REST-API starten
docker compose -f llm-api/docker-compose.yml up --build
```
