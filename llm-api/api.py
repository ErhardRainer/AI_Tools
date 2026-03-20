"""
LLM API — FastAPI-Wrapper für den LLM Client.

Stellt alle konfigurierten LLM-Provider als REST-API bereit.
Konfiguration: config.json (identisch zu LLM_Client/config.json)

Umgebungsvariablen:
  LLM_CONFIG   Pfad zur config.json (Standard: ../LLM_Client/config.json)
  API_KEY      Optionaler HTTP-API-Key (leer = keine Authentifizierung)

Starten:
  uvicorn api:app --reload
  python -m uvicorn api:app --host 0.0.0.0 --port 8000
"""

import os
import sys
from pathlib import Path

# LLM_Client aus dem Elternverzeichnis laden (für Direktstart ohne pip install)
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from LLM_Client import (
    PRESET_REGISTRY,
    PROVIDERS,
    build_provider,
    extract_json,
    load_config,
    mapping_reload,
    resolve_preset,
)

# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------

_DEFAULT_CONFIG = str(Path(__file__).parent.parent / "LLM_Client" / "config.json")
CONFIG_PATH = os.environ.get("LLM_CONFIG", _DEFAULT_CONFIG)
API_KEY = os.environ.get("API_KEY", "")  # leer → keine Authentifizierung erforderlich

config = load_config(CONFIG_PATH)
mapping_reload(config)

# ---------------------------------------------------------------------------
# FastAPI-App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="LLM API",
    description=(
        "REST-API für den LLM Client.\n\n"
        "Unterstützte Provider: OpenAI, Claude, Gemini, Grok, Kimi, DeepSeek, Groq, Mistral.\n\n"
        "Authentifizierung: Header `X-API-Key` (nur wenn Umgebungsvariable `API_KEY` gesetzt)."
    ),
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Authentifizierung (optional)
# ---------------------------------------------------------------------------

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def _verify_api_key(key: str | None = Security(_api_key_header)) -> None:
    """Prüft den API-Key, wenn API_KEY-Umgebungsvariable gesetzt ist."""
    if not API_KEY:
        return  # keine Authentifizierung konfiguriert
    if key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger oder fehlender API-Key. Header: X-API-Key",
        )


# ---------------------------------------------------------------------------
# Request- / Response-Modelle
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    provider: str | None = Field(
        None,
        description="Provider-Name (openai, claude, gemini, grok, kimi, deepseek, groq, mistral). "
        "Überschreibt default_provider aus config.json.",
        examples=["openai", "grok"],
    )
    preset: str | None = Field(
        None,
        description="Preset-Alias aus config.json (z.B. coding, fast). "
        "Wird von provider/model überschrieben falls angegeben.",
        examples=["coding", "fast"],
    )
    model: str | None = Field(
        None,
        description="Modellname überschreiben (optional).",
        examples=["gpt-4o-mini", "grok-3-mini"],
    )
    system: str = Field(
        ...,
        description="System-Prompt / Rollenanweisung für das Modell.",
        examples=["Du bist ein hilfreicher Assistent."],
    )
    context: str = Field(
        "",
        description="Optionaler Hintergrundtext (Dokument, E-Mail, Code …). "
        "Leer lassen wenn nicht benötigt.",
    )
    task: str = Field(
        ...,
        description="Die eigentliche Aufgabe oder Frage.",
        examples=["Erkläre Quantencomputing in drei Sätzen."],
    )
    output_format: str | None = Field(
        None,
        description=(
            "Ausgabeformat der Antwort:\n"
            "  plain (Standard) — roher Antwort-Text\n"
            "  json             — nur der extrahierte JSON-Block; "
            "422 wenn kein gültiges JSON vorhanden"
        ),
        examples=["plain", "json"],
    )


class ChatResponse(BaseModel):
    provider: str = Field(..., description="Verwendeter Provider.")
    model: str = Field(..., description="Verwendetes Modell.")
    response: str = Field(..., description="Antwort des Modells.")


class ProvidersResponse(BaseModel):
    providers: list[str]
    presets: dict[str, dict[str, str]]
    default_provider: str | None


# ---------------------------------------------------------------------------
# Endpunkte
# ---------------------------------------------------------------------------


@app.get("/health", tags=["System"], summary="Liveness-Check")
def health() -> dict:
    """Gibt `{"status": "ok"}` zurück — für Docker-Healthchecks."""
    return {"status": "ok"}


@app.get(
    "/providers",
    response_model=ProvidersResponse,
    tags=["System"],
    summary="Verfügbare Provider und Presets",
)
def list_providers() -> ProvidersResponse:
    """Listet alle registrierten Provider und konfigurierten Preset-Aliases."""
    return ProvidersResponse(
        providers=list(PROVIDERS.keys()),
        presets={
            name: {"provider": v["provider"], "model": v["model"]}
            for name, v in PRESET_REGISTRY.items()
        },
        default_provider=config.get("default_provider"),
    )


@app.post(
    "/chat",
    response_model=ChatResponse,
    tags=["Chat"],
    summary="Prompt an einen LLM-Provider senden",
)
def chat(
    req: ChatRequest,
    _: None = Security(_verify_api_key),
) -> ChatResponse:
    """
    Sendet System-, Kontext- und Aufgaben-Prompt an den gewählten Provider
    und gibt die Modellantwort zurück.

    **Provider-Auflösung (Priorität):**
    1. `provider` (explizit angegeben)
    2. `preset` → löst Provider + Modell auf
    3. `default_provider` aus config.json
    """
    provider_name = req.provider
    model_override = req.model

    # Preset auflösen (nur wenn kein expliziter Provider angegeben)
    if req.preset and not provider_name:
        try:
            provider_name, preset_model = resolve_preset(req.preset)
            if not model_override:
                model_override = preset_model
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unbekanntes Preset: '{req.preset}'. "
                f"Verfügbar: {list(PRESET_REGISTRY.keys())}",
            )

    # Fallback auf default_provider
    if not provider_name:
        provider_name = config.get("default_provider")
    if not provider_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kein Provider angegeben und kein default_provider in config.json.",
        )

    # Provider instanziieren
    try:
        provider = build_provider(provider_name, config, model_override=model_override)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    # API-Call
    try:
        raw_response = provider.send(
            system=req.system,
            context=req.context,
            task=req.task,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Provider-Fehler ({provider_name}): {exc}",
        )

    # Ausgabeformat
    if req.output_format == "json":
        try:
            response_text = extract_json(raw_response)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="output_format=json: Kein gültiges JSON in der Modell-Antwort gefunden.",
            )
    else:
        response_text = raw_response

    return ChatResponse(
        provider=provider_name,
        model=provider.model,
        response=response_text,
    )
