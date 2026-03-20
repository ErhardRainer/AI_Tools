"""
LLM Client — Unified interface for multiple LLM providers.

Sends a system prompt, context prompt, and task prompt to the configured provider.
All keys and settings are read from a JSON config file.

Supported providers:
    openai    — OpenAI (GPT-4o, GPT-4o-mini, ...)
    claude    — Anthropic Claude (claude-sonnet-4-6, claude-opus-4-6, ...)
    gemini    — Google Gemini (gemini-2.0-flash, gemini-2.0-pro, ...)
    grok      — xAI Grok (grok-3, grok-3-mini, ...)
    kimi      — Moonshot AI Kimi (kimi-k2, moonshot-v1-8k, ...)
    deepseek  — DeepSeek (deepseek-chat, deepseek-reasoner, ...)
    groq      — Groq inference (llama-3.3-70b-versatile, gemma2-9b-it, ...)
    mistral   — Mistral AI (mistral-large-latest, mistral-small-latest, ...)

Usage:
    python llm_client.py --config config.json
    python llm_client.py --config config.json --provider grok
    python llm_client.py --config config.json --provider kimi --model kimi-k2
    python llm_client.py --config config.json --provider deepseek --model deepseek-reasoner

Config file format: see config.template.json
"""

import argparse
import json
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Config loader
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
# Provider implementations
# ---------------------------------------------------------------------------

class OpenAIProvider:
    """OpenAI Chat Completions API — https://platform.openai.com"""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package required: pip install openai")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def send(self, system: str, context: str, task: str) -> str:
        messages = [{"role": "system", "content": system}]
        if context.strip():
            messages.append({"role": "user", "content": context})
            messages.append({"role": "assistant", "content": "Verstanden, ich habe den Kontext aufgenommen."})
        messages.append({"role": "user", "content": task})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content


class ClaudeProvider:
    """Anthropic Claude Messages API — https://console.anthropic.com"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package required: pip install anthropic")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def send(self, system: str, context: str, task: str) -> str:
        messages = []
        if context.strip():
            messages.append({"role": "user", "content": context})
            messages.append({"role": "assistant", "content": "Verstanden, ich habe den Kontext aufgenommen."})
        messages.append({"role": "user", "content": task})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=messages,
        )
        return response.content[0].text


class GeminiProvider:
    """Google Gemini Generative AI — https://aistudio.google.com"""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("google-generativeai package required: pip install google-generativeai")
        genai.configure(api_key=api_key)
        self.genai = genai
        self.model = model

    def send(self, system: str, context: str, task: str) -> str:
        model = self.genai.GenerativeModel(
            model_name=self.model,
            system_instruction=system,
        )
        user_content = f"{context}\n\n{task}".strip() if context.strip() else task
        response = model.generate_content(user_content)
        return response.text


# ---------------------------------------------------------------------------
# OpenAI-compatible providers (reuse the openai SDK, only base_url differs)
# ---------------------------------------------------------------------------

class _OpenAICompatibleProvider:
    """
    Base class for providers that implement the OpenAI Chat Completions API.
    Subclasses only need to set BASE_URL and DEFAULT_MODEL.
    Requires: pip install openai
    """
    BASE_URL: str = ""
    DEFAULT_MODEL: str = ""

    def __init__(self, api_key: str, model: str = ""):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package required: pip install openai")
        self.client = OpenAI(api_key=api_key, base_url=self.BASE_URL)
        self.model = model or self.DEFAULT_MODEL

    def send(self, system: str, context: str, task: str) -> str:
        messages = [{"role": "system", "content": system}]
        if context.strip():
            messages.append({"role": "user", "content": context})
            messages.append({"role": "assistant", "content": "Verstanden, ich habe den Kontext aufgenommen."})
        messages.append({"role": "user", "content": task})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content


class GrokProvider(_OpenAICompatibleProvider):
    """xAI Grok — https://console.x.ai
    Models: grok-3, grok-3-mini, grok-3-fast, grok-2-1212
    """
    BASE_URL = "https://api.x.ai/v1"
    DEFAULT_MODEL = "grok-3"


class KimiProvider(_OpenAICompatibleProvider):
    """Moonshot AI Kimi — https://platform.moonshot.cn
    Models: kimi-k2, moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k
    """
    BASE_URL = "https://api.moonshot.cn/v1"
    DEFAULT_MODEL = "kimi-k2"


class DeepSeekProvider(_OpenAICompatibleProvider):
    """DeepSeek — https://platform.deepseek.com
    Models: deepseek-chat (V3), deepseek-reasoner (R1)
    """
    BASE_URL = "https://api.deepseek.com"
    DEFAULT_MODEL = "deepseek-chat"


class GroqProvider(_OpenAICompatibleProvider):
    """Groq (fast inference) — https://console.groq.com
    Models: llama-3.3-70b-versatile, llama-3.1-8b-instant, gemma2-9b-it, mixtral-8x7b-32768
    """
    BASE_URL = "https://api.groq.com/openai/v1"
    DEFAULT_MODEL = "llama-3.3-70b-versatile"


class MistralProvider(_OpenAICompatibleProvider):
    """Mistral AI — https://console.mistral.ai
    Models: mistral-large-latest, mistral-small-latest, codestral-latest, open-mixtral-8x22b
    """
    BASE_URL = "https://api.mistral.ai/v1"
    DEFAULT_MODEL = "mistral-large-latest"


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

PROVIDERS = {
    "openai":   OpenAIProvider,
    "claude":   ClaudeProvider,
    "gemini":   GeminiProvider,
    "grok":     GrokProvider,
    "kimi":     KimiProvider,
    "deepseek": DeepSeekProvider,
    "groq":     GroqProvider,
    "mistral":  MistralProvider,
}


def build_provider(provider_name: str, config: dict, model_override: str | None = None):
    provider_name = provider_name.lower()
    if provider_name not in PROVIDERS:
        raise ValueError(f"Unknown provider '{provider_name}'. Choose from: {list(PROVIDERS)}")

    provider_cfg = get_nested(config, f"providers.{provider_name}", {})
    api_key = provider_cfg.get("api_key")
    if not api_key:
        raise ValueError(f"No api_key found for provider '{provider_name}' in config.")

    model = model_override or provider_cfg.get("model")
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
        description="Send system/context/task prompts to an LLM provider.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--config",   required=True,  help="Path to JSON config file")
    parser.add_argument("--provider", default=None,   choices=provider_choices,
                        help="Provider override:\n  " + "\n  ".join(provider_choices))
    parser.add_argument("--model",    default=None,   help="Model override (optional)")
    args = parser.parse_args()

    config = load_config(args.config)

    # Resolve provider: CLI flag → config default_provider → openai
    provider_name = args.provider or config.get("default_provider", "openai")

    prompts = config.get("prompts", {})
    system  = prompts.get("system",  "Du bist ein hilfreicher Assistent.")
    context = prompts.get("context", "")
    task    = prompts.get("task",    "")

    if not task.strip():
        print("ERROR: 'prompts.task' is empty in the config file.", file=sys.stderr)
        sys.exit(1)

    provider = build_provider(provider_name, config, model_override=args.model)

    print(f"Provider : {provider_name}")
    print(f"Model    : {provider.model}")
    print(f"System   : {system[:80]}{'...' if len(system) > 80 else ''}")
    print(f"Context  : {context[:80]}{'...' if len(context) > 80 else ''}" if context else "Context  : (none)")
    print(f"Task     : {task[:80]}{'...' if len(task) > 80 else ''}")
    print("-" * 60)

    response = provider.send(system=system, context=context, task=task)

    print("Response:")
    print(response)


if __name__ == "__main__":
    main()
