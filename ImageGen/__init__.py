"""
ImageGen — installierbares Python-Paket für Bildgenerierung.

Verwendung als Modul:
    from ImageGen import OpenAIImageProvider, build_provider, ImageResult

Verwendung als CLI:
    python -m ImageGen --config ImageGen/config.json --prompt "..."

Nach Installation (pip install ".[imagegen]"):
    image-gen --config ImageGen/config.json --prompt "..."
"""

from .image_gen import (
    load_config,
    get_nested,
    ImageData,
    ImageResult,
    OpenAIImageProvider,
    GoogleImageProvider,
    StabilityProvider,
    FalProvider,
    PROVIDERS,
    PRESET_REGISTRY,
    mapping_reload,
    resolve_preset,
    build_provider,
)

__all__ = [
    "load_config",
    "get_nested",
    "ImageData",
    "ImageResult",
    "OpenAIImageProvider",
    "GoogleImageProvider",
    "StabilityProvider",
    "FalProvider",
    "PROVIDERS",
    "PRESET_REGISTRY",
    "mapping_reload",
    "resolve_preset",
    "build_provider",
]
