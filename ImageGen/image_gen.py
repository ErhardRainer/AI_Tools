"""
ImageGen — Unified image generation client for multiple providers.

Sends a text prompt to the configured image generation provider and
returns the generated images as URLs or base64-encoded data.

Supported providers:
    openai     — DALL-E 3, DALL-E 2 (via openai SDK)
    google     — Google Imagen 3 (via google-genai SDK)
    stability  — Stability AI SD3, Core, Ultra (via REST API)
    fal        — fal.ai FLUX and other models (via REST API)

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
# Provider: Google Imagen
# ---------------------------------------------------------------------------

class GoogleImageProvider:
    """
    Google Imagen 3 via google-genai SDK.
    https://ai.google.dev/api/generate-images

    Modelle:
        imagen-3.0-generate-002  — Imagen 3 (Standard)
        imagen-3.0-fast-generate-001  — Imagen 3 Fast

    Seitenverhältnisse: 1:1, 3:4, 4:3, 9:16, 16:9

    Abhängigkeit: pip install google-genai
    """

    DEFAULT_MODEL = "imagen-3.0-generate-002"

    def __init__(self, api_key: str, model: str = ""):
        try:
            from google import genai
        except ImportError:
            raise ImportError(
                "google-genai package required for Google Imagen: pip install google-genai"
            )
        self.client = genai.Client(api_key=api_key)
        self.model = model or self.DEFAULT_MODEL
        self._genai = genai

    def generate(
        self,
        prompt: str,
        *,
        n: int = 1,
        aspect_ratio: str = "1:1",
    ) -> ImageResult:
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
        return ImageResult(
            provider="google",
            model=self.model,
            images=images,
        )


# ---------------------------------------------------------------------------
# Provider: Stability AI
# ---------------------------------------------------------------------------

class StabilityProvider:
    """
    Stability AI — Stable Image via REST API v2beta.
    https://platform.stability.ai/docs/api-reference

    Modelle / Endpunkte:
        core         — Stable Image Core        (schnell, günstig)
        sd3-large    — Stable Diffusion 3 Large  (höchste Qualität)
        sd3-large-turbo — SD3 Large Turbo        (schneller als Large)
        sd3-medium   — SD3 Medium                (ausgewogen)
        ultra        — Stable Image Ultra        (SDXL, sehr detailliert)

    Seitenverhältnisse: 1:1, 16:9, 21:9, 2:3, 3:2, 4:5, 5:4, 9:16, 9:21
    Ausgabeformate:     png, jpeg, webp

    Abhängigkeit: pip install requests
    """

    DEFAULT_MODEL = "core"
    BASE_URL = "https://api.stability.ai/v2beta/stable-image/generate"

    _SD3_MODELS = {"sd3-large", "sd3-large-turbo", "sd3-medium"}
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
    "openai":    OpenAIImageProvider,
    "google":    GoogleImageProvider,
    "stability": StabilityProvider,
    "fal":       FalProvider,
}


def build_provider(provider_name: str, config: dict, model_override: str | None = None):
    """Instanziiert den richtigen Provider aus config."""
    provider_name = provider_name.lower()
    if provider_name not in PROVIDERS:
        raise ValueError(
            f"Unbekannter Provider '{provider_name}'. Wähle aus: {list(PROVIDERS)}"
        )
    provider_cfg = get_nested(config, f"providers.{provider_name}", {})
    api_key = provider_cfg.get("api_key")
    if not api_key:
        raise ValueError(
            f"Kein api_key für Provider '{provider_name}' in config gefunden."
        )
    model = model_override or provider_cfg.get("model", "")
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
    elif isinstance(provider, (StabilityProvider, GoogleImageProvider)):
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
