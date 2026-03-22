"""
ImageGen — Unified image generation client for multiple providers.

Sends a text prompt to the configured image generation provider and
returns the generated images as URLs or base64-encoded data.

Supported providers:
    openai         — DALL-E 3, DALL-E 2 (via openai SDK)
    google         — Google Imagen 4, Imagen 3, Gemini Flash Image (via google-genai SDK)
    stability      — Stability AI SD3/SD3.5, Core, Ultra (via REST API)
    fal            — fal.ai FLUX and other models (via REST API)
    ideogram       — Ideogram V3, V2A, V2 (via REST API)
    leonardo       — Leonardo AI Phoenix, Kino XL, etc. (via REST API, async polling)
    firefly        — Adobe Firefly Image Model 3 (via REST API, OAuth2)
    auto1111       — AUTOMATIC1111 Stable Diffusion WebUI (lokal, REST API)
    ollamadiffuser — ollamadiffuser lokaler Server: FLUX, SDXL, SD3, SD1.5 (lokal, REST API)

Usage:
    python ImageGen/image_gen.py --config ImageGen/config.json --prompt "A sunset over mountains"
    python ImageGen/image_gen.py --config ImageGen/config.json --provider openai --output sunset.png
    python -m ImageGen --config ImageGen/config.json --provider stability --prompt "..."
    image-gen  --config ImageGen/config.json --preset flux  (after: pip install ".[imagegen]")

Config file format: see ImageGen/config.template.json
"""

import argparse
import base64
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def load_config(config_path: str) -> dict:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_nested(data: dict, key_path: str, default=None):
    """Retrieve a value from a nested dict using a dot-separated key path."""
    keys = key_path.split(".")
    for key in keys:
        if not isinstance(data, dict):
            return default
        data = data.get(key, default)
    return data


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class ImageData:
    """Ein einzelnes generiertes Bild (URL oder base64-kodierte Bytes)."""

    url: str | None = None
    b64_json: str | None = None

    def save(self, path: str) -> None:
        """Bild in eine Datei speichern."""
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)

        if self.b64_json:
            dest.write_bytes(base64.b64decode(self.b64_json))
        elif self.url:
            try:
                import requests as _req
            except ImportError:
                raise ImportError(
                    "requests-Paket zum Herunterladen von URLs erforderlich: pip install requests"
                )
            resp = _req.get(self.url, timeout=60)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
        else:
            raise ValueError("Weder URL noch b64_json vorhanden — Bild kann nicht gespeichert werden.")

    def to_dict(self) -> dict:
        return {"url": self.url, "b64_json": self.b64_json}


@dataclass
class ImageResult:
    """Ergebnis einer Bildgenerierung mit 1–n Bildern."""

    provider: str
    model: str
    images: list[ImageData] = field(default_factory=list)
    revised_prompt: str | None = None

    def save_all(self, pattern: str = "image_{n}.png") -> list[str]:
        """
        Alle Bilder speichern. {n} im Muster wird durch den 1-basierten Index ersetzt.

        Beispiele:
            result.save_all("output/bild_{n}.png")   → output/bild_1.png, output/bild_2.png
            result.save_all("ergebnis.png")           → ergebnis.png  (nur bei n=1 sinnvoll)
        """
        paths = []
        for i, img in enumerate(self.images, start=1):
            dest = pattern.replace("{n}", str(i))
            img.save(dest)
            paths.append(dest)
        return paths


# ---------------------------------------------------------------------------
# Provider: OpenAI (DALL-E)
# ---------------------------------------------------------------------------

class OpenAIImageProvider:
    """
    OpenAI Image Generation — DALL-E 3 und DALL-E 2.
    https://platform.openai.com/docs/guides/images

    Modelle:
        dall-e-3  — Höchste Qualität, max. 1 Bild pro Request
        dall-e-2  — Günstiger, bis zu 10 Bilder pro Request

    Größen (DALL-E 3):  1024x1024, 1792x1024, 1024x1792
    Größen (DALL-E 2):  256x256, 512x512, 1024x1024
    Qualität:           standard, hd  (nur DALL-E 3)
    """

    DEFAULT_MODEL = "dall-e-3"

    def __init__(self, api_key: str, model: str = ""):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package required: pip install openai")
        self.client = OpenAI(api_key=api_key)
        self.model = model or self.DEFAULT_MODEL

    def generate(
        self,
        prompt: str,
        *,
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1,
        response_format: str = "url",
    ) -> ImageResult:
        response = self.client.images.generate(
            model=self.model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=n,
            response_format=response_format,
        )
        images = [
            ImageData(
                url=item.url,
                b64_json=item.b64_json,
            )
            for item in response.data
        ]
        revised = response.data[0].revised_prompt if response.data else None
        return ImageResult(
            provider="openai",
            model=self.model,
            images=images,
            revised_prompt=revised,
        )


# ---------------------------------------------------------------------------
# Provider: Google Imagen & Gemini Flash Image
# ---------------------------------------------------------------------------

class GoogleImageProvider:
    """
    Google Bildgenerierung via google-genai SDK — zwei API-Varianten:

    ── Imagen-Familie (generate_images) ────────────────────────────────────
        imagen-4.0-generate-001       — Imagen 4 (Standard, GA)
        imagen-4.0-ultra-generate-001 — Imagen 4 Ultra (höchste Qualität)
        imagen-4.0-fast-generate-001  — Imagen 4 Fast (günstig/schnell)
        imagen-3.0-generate-002       — Imagen 3 (ältere Generation)

    ── Gemini Flash Image (generate_content + response_modalities) ─────────
        gemini-2.5-flash-image-preview — Gemini 2.5 Flash Image (Vorschau)
        gemini-2.0-flash-exp           — Gemini 2.0 Flash Experimental

        Diese Modelle kombinieren Text- und Bildgenerierung. Der Provider
        extrahiert automatisch alle Bild-Teile aus der Antwort.

    Seitenverhältnisse (Imagen): 1:1, 3:4, 4:3, 9:16, 16:9
    Abhängigkeit: pip install google-genai
    """

    DEFAULT_MODEL = "imagen-4.0-generate-001"

    _GEMINI_MODELS = ("gemini-",)  # Prefix-Erkennung für Gemini Flash Image

    def __init__(self, api_key: str, model: str = ""):
        try:
            from google import genai
        except ImportError:
            raise ImportError(
                "google-genai package required for Google image generation: pip install google-genai"
            )
        self.client = genai.Client(api_key=api_key)
        self.model = model or self.DEFAULT_MODEL
        self._genai = genai

    def _is_gemini_model(self) -> bool:
        return any(self.model.startswith(prefix) for prefix in self._GEMINI_MODELS)

    def generate(
        self,
        prompt: str,
        *,
        n: int = 1,
        aspect_ratio: str = "1:1",
    ) -> ImageResult:
        if self._is_gemini_model():
            return self._generate_gemini_flash(prompt, n=n)
        return self._generate_imagen(prompt, n=n, aspect_ratio=aspect_ratio)

    def _generate_imagen(self, prompt: str, *, n: int, aspect_ratio: str) -> ImageResult:
        """Imagen 3/4 via generate_images()."""
        response = self.client.models.generate_images(
            model=self.model,
            prompt=prompt,
            config=self._genai.types.GenerateImagesConfig(
                number_of_images=n,
                aspect_ratio=aspect_ratio,
            ),
        )
        images = [
            ImageData(b64_json=base64.b64encode(img.image.image_bytes).decode())
            for img in response.generated_images
        ]
        return ImageResult(provider="google", model=self.model, images=images)

    def _generate_gemini_flash(self, prompt: str, *, n: int) -> ImageResult:
        """
        Gemini 2.0/2.5 Flash Image via generate_content() mit response_modalities.
        Generiert n Bilder durch n aufeinanderfolgende API-Calls (Modell liefert
        je Aufruf ein Bild und optionalen Begleittext).
        """
        images = []
        for _ in range(max(1, n)):
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=self._genai.types.GenerateContentConfig(
                    response_modalities=["Text", "Image"],
                ),
            )
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    b64 = base64.b64encode(part.inline_data.data).decode()
                    images.append(ImageData(b64_json=b64))

        if not images:
            raise ValueError(
                f"Gemini Modell '{self.model}' hat keine Bild-Daten zurückgegeben. "
                "Prüfe ob das Modell Bildgenerierung unterstützt."
            )
        return ImageResult(provider="google", model=self.model, images=images)


# ---------------------------------------------------------------------------
# Provider: Stability AI
# ---------------------------------------------------------------------------

class StabilityProvider:
    """
    Stability AI — Stable Image via REST API v2beta.
    https://platform.stability.ai/docs/api-reference

    Modelle / Endpunkte:
        core              — Stable Image Core          (schnell, günstig)
        ultra             — Stable Image Ultra         (SDXL-basiert, sehr detailliert)
        sd3-large         — SD3 Large                  (höchste Qualität)
        sd3-large-turbo   — SD3 Large Turbo            (schneller als Large)
        sd3-medium        — SD3 Medium                 (ausgewogen)
        sd3.5-large       — SD3.5 Large (8B, GA)       (beste Qualität, aktuell)
        sd3.5-large-turbo — SD3.5 Large Turbo          (4 Steps, sehr schnell)
        sd3.5-medium      — SD3.5 Medium               (leichtgewichtig)

    Seitenverhältnisse: 1:1, 16:9, 21:9, 2:3, 3:2, 4:5, 5:4, 9:16, 9:21
    Ausgabeformate:     png, jpeg, webp

    Abhängigkeit: pip install requests
    """

    DEFAULT_MODEL = "core"
    BASE_URL = "https://api.stability.ai/v2beta/stable-image/generate"

    _SD3_MODELS = {
        "sd3-large", "sd3-large-turbo", "sd3-medium",
        "sd3.5-large", "sd3.5-large-turbo", "sd3.5-medium",
    }
    _ULTRA_MODELS = {"ultra"}

    def __init__(self, api_key: str, model: str = ""):
        try:
            import requests  # noqa: F401
        except ImportError:
            raise ImportError("requests package required: pip install requests")
        self.api_key = api_key
        self.model = model or self.DEFAULT_MODEL

    def _endpoint(self) -> str:
        if self.model in self._SD3_MODELS:
            return f"{self.BASE_URL}/sd3"
        if self.model in self._ULTRA_MODELS:
            return f"{self.BASE_URL}/ultra"
        return f"{self.BASE_URL}/core"

    def generate(
        self,
        prompt: str,
        *,
        aspect_ratio: str = "1:1",
        output_format: str = "png",
        negative_prompt: str = "",
        n: int = 1,
    ) -> ImageResult:
        import requests as _req

        data: dict = {
            "prompt": prompt,
            "output_format": output_format,
            "aspect_ratio": aspect_ratio,
        }
        if self.model in self._SD3_MODELS:
            data["model"] = self.model
        if negative_prompt:
            data["negative_prompt"] = negative_prompt

        images = []
        for _ in range(max(1, n)):
            resp = _req.post(
                self._endpoint(),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "application/json",
                },
                files={k: (None, v) for k, v in data.items()},
                timeout=120,
            )
            resp.raise_for_status()
            payload = resp.json()
            b64 = payload.get("image")
            if not b64:
                raise ValueError(f"Stability API: Kein Bild in der Antwort. {payload}")
            images.append(ImageData(b64_json=b64))

        return ImageResult(
            provider="stability",
            model=self.model,
            images=images,
        )


# ---------------------------------------------------------------------------
# Provider: fal.ai
# ---------------------------------------------------------------------------

class FalProvider:
    """
    fal.ai — FLUX und weitere Modelle via REST API.
    https://fal.ai/models

    Modelle (Beispiele):
        fal-ai/flux/dev          — FLUX.1 Dev (Standardmodell)
        fal-ai/flux/schnell      — FLUX.1 Schnell (sehr schnell)
        fal-ai/flux-pro          — FLUX.1 Pro (höchste Qualität)
        fal-ai/flux-realism      — FLUX Realism LoRA
        fal-ai/stable-diffusion-v3-medium — SD3 Medium

    Bildgrößen: square_hd, square, portrait_4_3, portrait_16_9,
                landscape_4_3, landscape_16_9

    Abhängigkeit: pip install requests
    """

    DEFAULT_MODEL = "fal-ai/flux/dev"
    BASE_URL = "https://fal.run"

    def __init__(self, api_key: str, model: str = ""):
        try:
            import requests  # noqa: F401
        except ImportError:
            raise ImportError("requests package required: pip install requests")
        self.api_key = api_key
        self.model = model or self.DEFAULT_MODEL

    def generate(
        self,
        prompt: str,
        *,
        image_size: str = "landscape_4_3",
        n: int = 1,
        enable_safety_checker: bool = True,
    ) -> ImageResult:
        import requests as _req

        resp = _req.post(
            f"{self.BASE_URL}/{self.model}",
            headers={
                "Authorization": f"Key {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "prompt": prompt,
                "image_size": image_size,
                "num_images": n,
                "enable_safety_checker": enable_safety_checker,
            },
            timeout=120,
        )
        resp.raise_for_status()
        payload = resp.json()

        raw_images = payload.get("images", [])
        if not raw_images:
            raise ValueError(f"fal.ai API: Keine Bilder in der Antwort. {payload}")

        images = [ImageData(url=img.get("url")) for img in raw_images]
        return ImageResult(
            provider="fal",
            model=self.model,
            images=images,
        )


# ---------------------------------------------------------------------------
# Provider: Ideogram
# ---------------------------------------------------------------------------

class IdeogramProvider:
    """
    Ideogram — Bildgenerierung via REST API.
    https://developer.ideogram.ai/

    Modelle:
        V_3  — Ideogram 3.0 (Mai 2025, aktuellste)
        V_2A — Ideogram 2a  (Feb 2025)
        V_2  — Ideogram 2.0

    Authentifizierung: Api-Key Header (kein Bearer-Token)
    Hinweis: Antwort-URLs verfallen — Provider lädt Bilder sofort herunter.
    Abhängigkeit: pip install requests
    """

    DEFAULT_MODEL = "V_3"
    BASE_URL = "https://api.ideogram.ai"

    _ASPECT_MAP = {
        "1:1":  "ASPECT_1_1",  "16:9": "ASPECT_16_9", "9:16": "ASPECT_10_16",
        "4:3":  "ASPECT_4_3",  "3:4":  "ASPECT_3_4",  "3:2":  "ASPECT_3_2",
        "2:3":  "ASPECT_2_3",
    }

    def __init__(self, api_key: str, model: str = ""):
        try:
            import requests  # noqa: F401
        except ImportError:
            raise ImportError("requests package required: pip install requests")
        self.api_key = api_key
        self.model = model or self.DEFAULT_MODEL

    def generate(
        self,
        prompt: str,
        *,
        n: int = 1,
        aspect_ratio: str = "1:1",
        style_type: str = "AUTO",
        negative_prompt: str = "",
    ) -> ImageResult:
        import requests as _req

        image_request: dict = {
            "prompt": prompt,
            "model": self.model,
            "aspect_ratio": self._ASPECT_MAP.get(aspect_ratio, "ASPECT_1_1"),
            "style_type": style_type,
            "num_images": n,
        }
        if negative_prompt:
            image_request["negative_prompt"] = negative_prompt

        resp = _req.post(
            f"{self.BASE_URL}/v1/ideogram-v3/generate",
            headers={"Api-Key": self.api_key, "Content-Type": "application/json"},
            json={"image_request": image_request},
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])
        if not data:
            raise ValueError(f"Ideogram API: Keine Bilder in der Antwort. {resp.json()}")

        images = []
        for item in data:
            url = item.get("url")
            if url:
                # URLs verfallen — sofort als b64 herunterladen
                img_resp = _req.get(url, timeout=60)
                img_resp.raise_for_status()
                images.append(ImageData(b64_json=base64.b64encode(img_resp.content).decode(), url=url))

        return ImageResult(provider="ideogram", model=self.model, images=images)


# ---------------------------------------------------------------------------
# Provider: Leonardo AI
# ---------------------------------------------------------------------------

class LeonardoProvider:
    """
    Leonardo AI — Bildgenerierung via REST API (asynchrones Job-System).
    https://docs.leonardo.ai/

    Modelle (Modell-IDs):
        de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3 — Phoenix 1.0 (Standard, empfohlen)
        aa77f04e-3eec-4034-9c07-d0f619684628 — Leonardo Kino XL
        Weitere IDs: GET https://cloud.leonardo.ai/api/rest/v1/platformModels

    Leonardo nutzt ein asynchrones System: Job erstellen → auf Status pollen.
    Authentifizierung: Bearer <UUID-API-Key>
    Abhängigkeit: pip install requests
    """

    DEFAULT_MODEL = "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3"  # Phoenix 1.0
    BASE_URL = "https://cloud.leonardo.ai/api/rest/v1"
    POLL_INTERVAL = 5    # Sekunden zwischen Polls
    POLL_TIMEOUT  = 300  # Sekunden bis Timeout

    def __init__(self, api_key: str, model: str = ""):
        try:
            import requests  # noqa: F401
        except ImportError:
            raise ImportError("requests package required: pip install requests")
        self.api_key = api_key
        self.model = model or self.DEFAULT_MODEL

    def _headers(self) -> dict:
        return {
            "authorization": f"Bearer {self.api_key}",
            "content-type": "application/json",
        }

    def generate(
        self,
        prompt: str,
        *,
        n: int = 1,
        width: int = 1472,
        height: int = 832,
        negative_prompt: str = "",
    ) -> ImageResult:
        import requests as _req

        body: dict = {
            "prompt": prompt,
            "modelId": self.model,
            "num_images": n,
            "width": width,
            "height": height,
            "alchemy": True,
        }
        if negative_prompt:
            body["negative_prompt"] = negative_prompt

        # 1. Generierungs-Job anlegen
        resp = _req.post(
            f"{self.BASE_URL}/generations",
            headers=self._headers(),
            json=body,
            timeout=30,
        )
        resp.raise_for_status()
        gen_id = resp.json()["sdGenerationJob"]["generationId"]

        # 2. Auf Fertigstellung warten
        deadline = time.time() + self.POLL_TIMEOUT
        while time.time() < deadline:
            time.sleep(self.POLL_INTERVAL)
            poll = _req.get(
                f"{self.BASE_URL}/generations/{gen_id}",
                headers=self._headers(),
                timeout=30,
            )
            poll.raise_for_status()
            job = poll.json().get("generations_by_pk", {})
            status = job.get("status")
            if status == "COMPLETE":
                images = [ImageData(url=img["url"]) for img in job.get("generated_images", [])]
                return ImageResult(provider="leonardo", model=self.model, images=images)
            if status == "FAILED":
                raise ValueError(f"Leonardo API: Generierung fehlgeschlagen. {job}")

        raise TimeoutError(f"Leonardo API: Timeout nach {self.POLL_TIMEOUT}s für Job {gen_id}.")


# ---------------------------------------------------------------------------
# Provider: Adobe Firefly
# ---------------------------------------------------------------------------

class FireflyProvider:
    """
    Adobe Firefly — Bildgenerierung via REST API mit OAuth2.
    https://developer.adobe.com/firefly-api/

    Modelle:
        firefly-image-model-3      — Firefly Image Model 3 (Standard, GA)
        firefly-image-model-3-fast — Firefly Image Model 3 Fast

    Authentifizierung: OAuth 2.0 Client Credentials (kein einfacher API-Key).
    Config:  providers.firefly.client_id   und   providers.firefly.client_secret
    Der Access Token wird pro Instanz gecacht (gültig 24h).

    Voraussetzung: Adobe Developer Console Projekt mit Firefly API aktiviert.
    https://developer.adobe.com/console/projects

    Abhängigkeit: pip install requests
    """

    DEFAULT_MODEL = "firefly-image-model-3"
    TOKEN_URL = "https://ims-na1.adobelogin.com/ims/token/v3"
    BASE_URL   = "https://firefly-api.adobe.io"
    _SCOPES    = "openid,AdobeID,session,additional_info,read_organizations,firefly_api,ff_apis"

    def __init__(self, client_id: str, client_secret: str, model: str = ""):
        try:
            import requests  # noqa: F401
        except ImportError:
            raise ImportError("requests package required: pip install requests")
        self.client_id     = client_id
        self.client_secret = client_secret
        self.model         = model or self.DEFAULT_MODEL
        self._token: str | None = None

    def _get_token(self) -> str:
        """OAuth2 Client Credentials Token abrufen (wird gecacht)."""
        if self._token:
            return self._token
        import requests as _req
        resp = _req.post(
            self.TOKEN_URL,
            data={
                "grant_type":    "client_credentials",
                "client_id":     self.client_id,
                "client_secret": self.client_secret,
                "scope":         self._SCOPES,
            },
            timeout=30,
        )
        resp.raise_for_status()
        self._token = resp.json()["access_token"]
        return self._token

    def generate(
        self,
        prompt: str,
        *,
        n: int = 1,
        size: str = "1024x1024",
    ) -> ImageResult:
        import requests as _req

        w, h = (int(x) for x in size.split("x"))
        token = self._get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "x-api-key":     self.client_id,
            "Content-Type":  "application/json",
        }
        images = []
        for _ in range(max(1, n)):
            resp = _req.post(
                f"{self.BASE_URL}/v3/images/generate",
                headers=headers,
                json={
                    "prompt":        prompt,
                    "size":          {"width": w, "height": h},
                    "numVariations": 1,
                },
                timeout=120,
            )
            resp.raise_for_status()
            for out in resp.json().get("outputs", []):
                img_meta = out.get("image", {})
                url = img_meta.get("presignedUrl") or img_meta.get("url")
                if url:
                    img_resp = _req.get(url, timeout=60)
                    img_resp.raise_for_status()
                    images.append(ImageData(b64_json=base64.b64encode(img_resp.content).decode(), url=url))

        if not images:
            raise ValueError("Firefly API: Keine Bilder in der Antwort.")
        return ImageResult(provider="firefly", model=self.model, images=images)


# ---------------------------------------------------------------------------
# Provider: AUTOMATIC1111 WebUI (lokal)
# ---------------------------------------------------------------------------

class Auto1111Provider:
    """
    AUTOMATIC1111 Stable Diffusion WebUI — lokale Instanz via REST API.
    https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/API

    Lokal starten: python launch.py --api
    Standard-URL:  http://127.0.0.1:7860

    Unterstützte Modelle (Auswahl, werden als Checkpoint-Name angegeben):
        sd_xl_base_1.0                     — SDXL Base (1024x1024)
        juggernautXL_v9Rdphoto2Lightning    — Juggernaut XL (beliebt)
        dreamshaperXL_v21TurboDPMSDE        — DreamShaper XL Turbo
        FLUX.1-schnell                      — FLUX.1 Schnell (Apache 2.0)
        FLUX.1-dev                          — FLUX.1 Dev (beste Qualität)
        v1-5-pruned-emaonly                 — SD 1.5 (leichtgewichtig)

    Config:  providers.auto1111.base_url  (Standard: http://127.0.0.1:7860)
    Kein API-Key erforderlich (lokale Installation).
    Abhängigkeit: pip install requests
    """

    DEFAULT_MODEL   = ""  # Nutzt das in A1111 aktuell geladene Modell
    DEFAULT_BASE_URL = "http://127.0.0.1:7860"

    def __init__(self, api_key: str = "", model: str = "", base_url: str = ""):
        try:
            import requests  # noqa: F401
        except ImportError:
            raise ImportError("requests package required: pip install requests")
        self.model    = model
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")

    def generate(
        self,
        prompt: str,
        *,
        n: int = 1,
        size: str = "512x512",
        steps: int = 20,
        cfg_scale: float = 7.0,
        negative_prompt: str = "",
    ) -> ImageResult:
        import requests as _req

        w, h = (int(x) for x in size.split("x"))

        # Ggf. Checkpoint wechseln (sofern angegeben)
        if self.model:
            _req.post(
                f"{self.base_url}/sdapi/v1/options",
                json={"sd_model_checkpoint": self.model},
                timeout=30,
            )

        resp = _req.post(
            f"{self.base_url}/sdapi/v1/txt2img",
            json={
                "prompt":          prompt,
                "negative_prompt": negative_prompt,
                "steps":           steps,
                "cfg_scale":       cfg_scale,
                "width":           w,
                "height":          h,
                "batch_size":      n,
            },
            timeout=300,
        )
        resp.raise_for_status()
        raw = resp.json().get("images", [])
        if not raw:
            raise ValueError(f"Auto1111 API: Keine Bilder in der Antwort. {resp.json()}")
        images = [ImageData(b64_json=b64) for b64 in raw]
        return ImageResult(provider="auto1111", model=self.model or "current", images=images)


# ---------------------------------------------------------------------------
# Provider: ollamadiffuser (lokal)
# ---------------------------------------------------------------------------

class OllamaDiffuserProvider:
    """
    ollamadiffuser — Lokale Bildgenerierung mit einfacher REST API.
    https://pypi.org/project/ollamadiffuser/

    Installation & Start:
        pip install ollamadiffuser
        ollamadiffuser pull flux.1-schnell
        ollamadiffuser run flux.1-schnell   (startet Server auf Port 8000)

    Unterstützte Modelle (Beispiele):
        flux.1-schnell  — FLUX.1 Schnell (Apache 2.0, 1–4 Steps, empfohlen)
        flux.1-dev      — FLUX.1 Dev (non-commercial, beste Qualität)
        sdxl            — Stable Diffusion XL
        sd3-medium      — SD 3 Medium
        sd1.5           — SD 1.5 (leichtgewichtig, schnell)

    Config:  providers.ollamadiffuser.base_url  (Standard: http://localhost:8000)
    Kein API-Key erforderlich (lokale Installation).
    Abhängigkeit: pip install requests  (ollamadiffuser läuft als separater Server)
    """

    DEFAULT_MODEL    = "flux.1-schnell"
    DEFAULT_BASE_URL = "http://localhost:8000"

    def __init__(self, api_key: str = "", model: str = "", base_url: str = ""):
        try:
            import requests  # noqa: F401
        except ImportError:
            raise ImportError("requests package required: pip install requests")
        self.model    = model or self.DEFAULT_MODEL
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")

    def generate(
        self,
        prompt: str,
        *,
        n: int = 1,
        negative_prompt: str = "",
    ) -> ImageResult:
        import requests as _req

        payload: dict = {"prompt": prompt, "model": self.model}
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        images = []
        for _ in range(max(1, n)):
            resp = _req.post(f"{self.base_url}/api/generate", json=payload, timeout=300)
            resp.raise_for_status()
            images.append(ImageData(b64_json=base64.b64encode(resp.content).decode()))

        return ImageResult(provider="ollamadiffuser", model=self.model, images=images)


# ---------------------------------------------------------------------------
# Preset registry
# ---------------------------------------------------------------------------

PRESET_REGISTRY: dict[str, dict] = {}


def mapping_reload(source: str | dict) -> dict:
    """Lädt Presets aus einer JSON-Datei oder einem dict in PRESET_REGISTRY."""
    data = load_config(source) if isinstance(source, str) else source
    new_presets = data.get("presets", {}) if isinstance(data, dict) else {}
    for alias, entry in new_presets.items():
        if not isinstance(entry, dict) or "provider" not in entry:
            raise ValueError(
                f"Preset '{alias}' ungültig. "
                f"Erwartet {{\"provider\": \"...\", \"model\": \"...\"}}, gefunden: {entry}"
            )
    PRESET_REGISTRY.clear()
    PRESET_REGISTRY.update(new_presets)
    return PRESET_REGISTRY


def resolve_preset(name: str) -> tuple[str, str]:
    """Löst einen Preset-Alias zu (provider, model) auf."""
    if name not in PRESET_REGISTRY:
        available = list(PRESET_REGISTRY.keys()) or ["(leer — mapping_reload() aufrufen)"]
        raise KeyError(f"Unbekanntes Preset '{name}'. Verfügbar: {available}")
    entry = PRESET_REGISTRY[name]
    return entry["provider"], entry.get("model", "")


# ---------------------------------------------------------------------------
# Registry & Factory
# ---------------------------------------------------------------------------

PROVIDERS: dict[str, type] = {
    "openai":          OpenAIImageProvider,
    "google":          GoogleImageProvider,
    "stability":       StabilityProvider,
    "fal":             FalProvider,
    "ideogram":        IdeogramProvider,
    "leonardo":        LeonardoProvider,
    "firefly":         FireflyProvider,
    "auto1111":        Auto1111Provider,
    "ollamadiffuser":  OllamaDiffuserProvider,
}


def build_provider(provider_name: str, config: dict, model_override: str | None = None):
    """Instanziiert den richtigen Provider aus config."""
    provider_name = provider_name.lower()
    if provider_name not in PROVIDERS:
        raise ValueError(
            f"Unbekannter Provider '{provider_name}'. Wähle aus: {list(PROVIDERS)}"
        )
    provider_cfg = get_nested(config, f"providers.{provider_name}", {})
    model = model_override or provider_cfg.get("model", "")

    # FireflyProvider: OAuth2 — client_id + client_secret statt api_key
    if provider_name == "firefly":
        client_id     = provider_cfg.get("client_id", "")
        client_secret = provider_cfg.get("client_secret", "")
        if not (client_id and client_secret):
            raise ValueError(
                "FireflyProvider: 'client_id' und 'client_secret' in providers.firefly erforderlich."
            )
        kwargs: dict = {"client_id": client_id, "client_secret": client_secret}

    # Lokale Provider: kein api_key erforderlich, optionale base_url
    elif provider_name in ("auto1111", "ollamadiffuser"):
        kwargs = {"api_key": provider_cfg.get("api_key", "")}
        if "base_url" in provider_cfg:
            kwargs["base_url"] = provider_cfg["base_url"]

    # Alle anderen Provider: api_key erforderlich
    else:
        api_key = provider_cfg.get("api_key", "")
        if not api_key:
            raise ValueError(
                f"Kein api_key für Provider '{provider_name}' in config gefunden."
            )
        kwargs = {"api_key": api_key}

    if model:
        kwargs["model"] = model
    return PROVIDERS[provider_name](**kwargs)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    provider_choices = list(PROVIDERS.keys())
    parser = argparse.ArgumentParser(
        description="Bildgenerierung via verschiedene KI-Provider.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--config",   required=True, help="Pfad zur config.json")
    parser.add_argument("--prompt",   default=None,  help="Bild-Prompt (überschreibt config)")
    parser.add_argument("--preset",   default=None,  help="Preset-Alias aus config.json")
    parser.add_argument("--provider", default=None,  choices=provider_choices,
                        help="Provider:\n  " + "\n  ".join(provider_choices))
    parser.add_argument("--model",    default=None,  help="Modell überschreiben (optional)")
    parser.add_argument("--output",   default="image_{n}.png", metavar="DATEI",
                        help=(
                            "Ausgabedatei (Standard: image_{n}.png).\n"
                            "{n} wird durch den 1-basierten Bildindex ersetzt."
                        ))
    parser.add_argument("--n",        default=1, type=int,
                        help="Anzahl der zu generierenden Bilder (Standard: 1)")
    parser.add_argument("--size",     default=None,
                        help="Bildgröße, z.B. 1024x1024 (nur DALL-E)")
    parser.add_argument("--quality",  default=None, choices=["standard", "hd"],
                        help="Qualität: standard oder hd (nur DALL-E 3)")
    parser.add_argument("--aspect-ratio", default=None, dest="aspect_ratio",
                        help="Seitenverhältnis, z.B. 16:9 (Stability, Google, fal)")
    parser.add_argument("--no-save",  action="store_true",
                        help="Bilder nicht speichern (nur URL/Info ausgeben)")
    args = parser.parse_args()

    config = load_config(args.config)
    if config.get("presets"):
        mapping_reload(config)

    provider_name = args.provider
    model_override = args.model

    if args.preset and not provider_name:
        preset_provider, preset_model = resolve_preset(args.preset)
        provider_name = preset_provider
        if not model_override:
            model_override = preset_model or None

    provider_name = provider_name or config.get("default_provider", "openai")
    prompt = args.prompt or get_nested(config, "defaults.prompt", "")

    if not prompt.strip():
        print("ERROR: Kein Prompt angegeben (--prompt oder config defaults.prompt).", file=sys.stderr)
        sys.exit(1)

    provider = build_provider(provider_name, config, model_override=model_override)

    print(f"Provider : {provider_name}")
    print(f"Model    : {provider.model}")
    print(f"Prompt   : {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    print(f"Bilder   : {args.n}")
    print("-" * 60)

    # Provider-spezifische Argumente
    kwargs: dict = {"n": args.n}
    if isinstance(provider, OpenAIImageProvider):
        if args.size:
            kwargs["size"] = args.size
        if args.quality:
            kwargs["quality"] = args.quality
    elif isinstance(provider, (StabilityProvider, GoogleImageProvider, IdeogramProvider)):
        if args.aspect_ratio:
            kwargs["aspect_ratio"] = args.aspect_ratio
    elif isinstance(provider, FalProvider):
        if args.aspect_ratio:
            # fal.ai verwendet image_size statt aspect_ratio
            mapping = {
                "1:1": "square_hd", "16:9": "landscape_16_9",
                "9:16": "portrait_16_9", "4:3": "landscape_4_3", "3:4": "portrait_4_3",
            }
            kwargs["image_size"] = mapping.get(args.aspect_ratio, args.aspect_ratio)
    elif isinstance(provider, (FireflyProvider, Auto1111Provider)):
        if args.size:
            kwargs["size"] = args.size

    result = provider.generate(prompt, **kwargs)

    if result.revised_prompt:
        print(f"Überarbeiteter Prompt: {result.revised_prompt}")

    if args.no_save:
        for i, img in enumerate(result.images, start=1):
            print(f"Bild {i}: url={img.url} b64={'<vorhanden>' if img.b64_json else None}")
    else:
        paths = result.save_all(args.output)
        for path in paths:
            print(f"Gespeichert: {path}")


if __name__ == "__main__":
    main()
