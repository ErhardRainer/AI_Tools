"""
Media API — FastAPI-Wrapper für LLM_Client und ImageGen.

Stellt Text- und Bildgenerierung als REST-API bereit.

Umgebungsvariablen:
  LLM_CONFIG    Pfad zur LLM config.json   (Standard: ../LLM_Client/config.json)
  IMAGE_CONFIG  Pfad zur ImageGen config.json (Standard: ../ImageGen/config.json)
  API_KEY       Optionaler HTTP-API-Key (leer = keine Authentifizierung)

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
    fetch_context_urls,
    load_config,
    mapping_reload,
    resolve_preset,
)

# ImageGen — optional (nicht verfügbar wenn nicht installiert)
try:
    from ImageGen import (
        build_provider as image_build_provider,
        load_config as image_load_config,
        mapping_reload as image_mapping_reload,
        PROVIDERS as IMAGE_PROVIDERS,
        PRESET_REGISTRY as IMAGE_PRESET_REGISTRY,
    )
    _IMAGE_GEN_AVAILABLE = True
except ImportError:
    _IMAGE_GEN_AVAILABLE = False

# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------

_DEFAULT_LLM_CONFIG   = str(Path(__file__).parent.parent / "LLM_Client" / "config.json")
_DEFAULT_IMAGE_CONFIG = str(Path(__file__).parent.parent / "ImageGen"  / "config.json")

CONFIG_PATH       = os.environ.get("LLM_CONFIG",   _DEFAULT_LLM_CONFIG)
IMAGE_CONFIG_PATH = os.environ.get("IMAGE_CONFIG", _DEFAULT_IMAGE_CONFIG)
API_KEY           = os.environ.get("API_KEY", "")

config = load_config(CONFIG_PATH)
mapping_reload(config)

image_config: dict = {}
if _IMAGE_GEN_AVAILABLE and Path(IMAGE_CONFIG_PATH).exists():
    image_config = image_load_config(IMAGE_CONFIG_PATH)
    image_mapping_reload(image_config)

# ---------------------------------------------------------------------------
# FastAPI-App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Media API",
    description=(
        "REST-API für LLM_Client und ImageGen.\n\n"
        "**Text-Endpunkte:** OpenAI, Claude, Gemini, Grok, Kimi, DeepSeek, Groq, Mistral.\n\n"
        "**Bild-Endpunkte:** DALL-E, Google Imagen/Gemini, Stability AI, fal.ai FLUX, "
        "Ideogram, Leonardo AI, Adobe Firefly, AUTOMATIC1111 (lokal), ollamadiffuser (lokal).\n\n"
        "Authentifizierung: Header `X-API-Key` (nur wenn Umgebungsvariable `API_KEY` gesetzt)."
    ),
    version="2.0.0",
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


# --- ImageGen-Modelle -------------------------------------------------------

class ImageRequest(BaseModel):
    provider: str | None = Field(
        None,
        description=(
            "Provider: openai, google, stability, fal, ideogram, leonardo, firefly, "
            "auto1111 (lokal), ollamadiffuser (lokal)."
        ),
        examples=["openai", "fal", "ideogram", "local-flux"],
    )
    preset: str | None = Field(
        None,
        description="Preset-Alias aus ImageGen/config.json (z.B. flux, sd3, quality).",
        examples=["flux", "sd3"],
    )
    model: str | None = Field(
        None,
        description="Modell überschreiben (optional).",
        examples=["dall-e-3", "fal-ai/flux-pro"],
    )
    prompt: str = Field(
        ...,
        description="Bild-Prompt.",
        examples=["A serene mountain lake at golden hour, photorealistic"],
    )
    n: int = Field(1, ge=1, le=10, description="Anzahl der Bilder (1–10).")
    # DALL-E spezifisch
    size: str | None = Field(None, description="Bildgröße (DALL-E): 1024x1024, 1792x1024, 1024x1792.")
    quality: str | None = Field(None, description="Qualität (DALL-E 3): standard oder hd.")
    # Stability / Google spezifisch
    aspect_ratio: str | None = Field(None, description="Seitenverhältnis: 1:1, 16:9, 9:16, 4:3, 3:4.")
    # fal.ai spezifisch
    image_size: str | None = Field(
        None,
        description="Bildgröße für fal.ai: square_hd, landscape_4_3, landscape_16_9, portrait_16_9.",
    )


class ImageDataResponse(BaseModel):
    url: str | None = None
    b64_json: str | None = None


class ImageResponse(BaseModel):
    provider: str
    model: str
    revised_prompt: str | None = None
    images: list[ImageDataResponse]


# ---------------------------------------------------------------------------
# Endpunkte
# ---------------------------------------------------------------------------


@app.get("/health", tags=["System"], summary="Liveness-Check")
def health() -> dict:
    """Gibt `{"status": "ok"}` zurück — für Docker-Healthchecks."""
    return {"status": "ok"}


@app.get(
    "/providers",
    tags=["System"],
    summary="Verfügbare Provider und Presets",
)
def list_providers() -> dict:
    """Listet alle registrierten Text- und Bildgenerierungs-Provider."""
    result: dict = {
        "text": {
            "providers": list(PROVIDERS.keys()),
            "presets": {
                name: {"provider": v["provider"], "model": v["model"]}
                for name, v in PRESET_REGISTRY.items()
            },
            "default_provider": config.get("default_provider"),
        },
    }
    if _IMAGE_GEN_AVAILABLE:
        result["image"] = {
            "providers": list(IMAGE_PROVIDERS.keys()),
            "presets": {
                name: {"provider": v["provider"], "model": v["model"]}
                for name, v in IMAGE_PRESET_REGISTRY.items()
            },
            "default_provider": image_config.get("default_provider"),
        }
    return result


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

    # HTTP(S)-URLs im Kontext automatisch abrufen und durch Inhalt ersetzen
    resolved_context = fetch_context_urls(req.context)

    # API-Call
    try:
        raw_response = provider.send(
            system=req.system,
            context=resolved_context,
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


@app.post(
    "/image",
    response_model=ImageResponse,
    tags=["Bild"],
    summary="Bild generieren",
)
def generate_image(
    req: ImageRequest,
    _: None = Security(_verify_api_key),
) -> ImageResponse:
    """
    Generiert ein oder mehrere Bilder aus einem Text-Prompt.

    **Provider-Auflösung (Priorität):**
    1. `provider` (explizit)
    2. `preset` → löst Provider + Modell auf
    3. `default_provider` aus ImageGen/config.json

    **Provider-spezifische Parameter:**
    - DALL-E:    `size`, `quality`
    - Stability: `aspect_ratio`
    - Google:    `aspect_ratio`
    - fal.ai:    `image_size`
    """
    if not _IMAGE_GEN_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ImageGen nicht verfügbar. Installation: pip install '.[imagegen]'",
        )
    if not image_config:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"ImageGen config nicht gefunden: {IMAGE_CONFIG_PATH}",
        )

    provider_name = req.provider
    model_override = req.model

    if req.preset and not provider_name:
        try:
            provider_name, preset_model = IMAGE_PRESET_REGISTRY[req.preset]["provider"], \
                                          IMAGE_PRESET_REGISTRY[req.preset].get("model", "")
            if not model_override:
                model_override = preset_model or None
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unbekanntes Bild-Preset: '{req.preset}'. "
                f"Verfügbar: {list(IMAGE_PRESET_REGISTRY.keys())}",
            )

    if not provider_name:
        provider_name = image_config.get("default_provider")
    if not provider_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kein Provider angegeben und kein default_provider in ImageGen/config.json.",
        )

    try:
        provider = image_build_provider(provider_name, image_config, model_override=model_override)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    # Provider-spezifische Argumente zusammenstellen
    kwargs: dict = {"n": req.n}
    provider_cls_name = type(provider).__name__

    if provider_cls_name == "OpenAIImageProvider":
        if req.size:
            kwargs["size"] = req.size
        if req.quality:
            kwargs["quality"] = req.quality
    elif provider_cls_name in ("StabilityProvider", "GoogleImageProvider", "IdeogramProvider"):
        if req.aspect_ratio:
            kwargs["aspect_ratio"] = req.aspect_ratio
    elif provider_cls_name == "FalProvider":
        if req.image_size:
            kwargs["image_size"] = req.image_size
        elif req.aspect_ratio:
            _ar_map = {
                "1:1": "square_hd", "16:9": "landscape_16_9",
                "9:16": "portrait_16_9", "4:3": "landscape_4_3", "3:4": "portrait_4_3",
            }
            kwargs["image_size"] = _ar_map.get(req.aspect_ratio, req.aspect_ratio)
    elif provider_cls_name in ("FireflyProvider", "Auto1111Provider"):
        if req.size:
            kwargs["size"] = req.size
    # LeonardoProvider, OllamaDiffuserProvider: keine speziellen kwargs nötig

    try:
        result = provider.generate(req.prompt, **kwargs)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Bildgenerierung fehlgeschlagen ({provider_name}): {exc}",
        )

    return ImageResponse(
        provider=result.provider,
        model=result.model,
        revised_prompt=result.revised_prompt,
        images=[ImageDataResponse(url=img.url, b64_json=img.b64_json) for img in result.images],
    )
