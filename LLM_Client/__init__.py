"""
LLM Client — installierbares Python-Paket.

Verwendung als Modul:
    from LLM_Client import OpenAIProvider, GrokProvider, build_provider

Verwendung als CLI:
    python -m LLM_Client --config config.json --provider grok

Nach Installation (pip install .):
    llm-client --config config.json --provider grok
"""

from .llm_client import (
    load_config,
    get_nested,
    OpenAIProvider,
    ClaudeProvider,
    GeminiProvider,
    GrokProvider,
    KimiProvider,
    DeepSeekProvider,
    GroqProvider,
    MistralProvider,
    PROVIDERS,
    build_provider,
)

__all__ = [
    "load_config",
    "get_nested",
    "OpenAIProvider",
    "ClaudeProvider",
    "GeminiProvider",
    "GrokProvider",
    "KimiProvider",
    "DeepSeekProvider",
    "GroqProvider",
    "MistralProvider",
    "PROVIDERS",
    "build_provider",
]
