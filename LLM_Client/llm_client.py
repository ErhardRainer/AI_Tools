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

Preset aliases (defined in config.json under "presets"):
    --preset coding     → claude + claude-opus-4-6
    --preset fast       → groq  + llama-3.1-8b-instant
    --preset cheap      → deepseek + deepseek-chat
    --preset reasoning  → deepseek + deepseek-reasoner

Usage:
    python llm_client.py --config config.json
    python llm_client.py --config config.json --provider grok
    python llm_client.py --config config.json --provider kimi --model kimi-k2
    python llm_client.py --config config.json --preset coding
    python llm_client.py --config config.json --preset fast
    python -m LLM_Client --config config.json --preset reasoning
    llm-client           --config config.json --preset cheap   (after: pip install .)

Config file format: see config.template.json
"""

import argparse
import json
import re
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
# Preset / Alias registry
# ---------------------------------------------------------------------------

# Module-level registry: maps alias name → {"provider": ..., "model": ...}
PRESET_REGISTRY: dict[str, dict] = {}


def mapping_reload(source: str | dict) -> dict:
    """
    Load (or reload) the preset mapping from a JSON file or a config dict.

    The source can be:
    - A file path (str) pointing to a JSON file that contains a "presets" key
      OR is itself a flat presets mapping.
    - A dict (e.g. the already-loaded config) that contains a "presets" key
      OR is itself a flat presets mapping.

    Each preset entry must have the form:
        "<alias>": {"provider": "<provider-name>", "model": "<model-name>"}

    Returns the loaded presets dict (also updates the global PRESET_REGISTRY).

    Example (in config.json):
        {
          "presets": {
            "coding":    {"provider": "claude",   "model": "claude-opus-4-6"},
            "fast":      {"provider": "groq",     "model": "llama-3.1-8b-instant"},
            "cheap":     {"provider": "deepseek", "model": "deepseek-chat"}
          }
        }

    Programmatic usage:
        from LLM_Client import mapping_reload, resolve_preset
        mapping_reload("config.json")
        provider, model = resolve_preset("coding")
    """
    if isinstance(source, str):
        data = load_config(source)
    else:
        data = source

    # Accept {"presets": {...}} or the flat dict {"coding": {...}, ...} directly
    new_presets = data.get("presets", data) if isinstance(data, dict) else {}

    # Validate each entry has at minimum a "provider" key
    for alias, entry in new_presets.items():
        if not isinstance(entry, dict) or "provider" not in entry:
            raise ValueError(
                f"Preset '{alias}' is invalid. "
                f"Expected {{\"provider\": \"...\", \"model\": \"...\"}}, got: {entry}"
            )

    # Mutate the existing dict object (clear + update) so that all references
    # to PRESET_REGISTRY (e.g. from `from LLM_Client import PRESET_REGISTRY`)
    # see the updated values without re-importing.
    PRESET_REGISTRY.clear()
    PRESET_REGISTRY.update(new_presets)
    return PRESET_REGISTRY


def resolve_preset(name: str) -> tuple[str, str]:
    """
    Resolve a preset alias to a (provider, model) tuple.

    Raises KeyError if the alias is not in PRESET_REGISTRY.
    Call mapping_reload() first to populate the registry.

    Example:
        mapping_reload("config.json")
        provider, model = resolve_preset("coding")
        # → ("claude", "claude-opus-4-6")
    """
    if name not in PRESET_REGISTRY:
        available = list(PRESET_REGISTRY.keys()) or ["(registry is empty — call mapping_reload first)"]
        raise KeyError(f"Unknown preset '{name}'. Available: {available}")
    entry = PRESET_REGISTRY[name]
    return entry["provider"], entry.get("model", "")


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
# Config writer
# ---------------------------------------------------------------------------

def set_api_key(provider: str, api_key: str, config_path: str) -> None:
    """
    Schreibt den API-Key eines Providers in die config.json.

    Legt den Pfad ``providers.<provider>.api_key`` an, falls er noch nicht
    existiert. Alle anderen Felder der Datei bleiben unverändert.

    Args:
        provider:    Provider-Name (z. B. ``"openai"``, ``"claude"``).
        api_key:     Der API-Key-String.
        config_path: Pfad zur config.json (wird überschrieben).

    Raises:
        FileNotFoundError: Wenn ``config_path`` nicht existiert.
        ValueError:        Wenn ``provider`` oder ``api_key`` leer sind.

    Example:
        set_api_key("openai", "sk-...", "LLM_Client/config.json")
        set_api_key("claude", "sk-ant-...", "LLM_Client/config.json")
    """
    if not provider:
        raise ValueError("provider darf nicht leer sein.")
    if not api_key:
        raise ValueError("api_key darf nicht leer sein.")

    config = load_config(config_path)
    config.setdefault("providers", {}).setdefault(provider, {})["api_key"] = api_key

    _write_config(config_path, config)


def set_default_model(provider: str, model: str, config_path: str) -> None:
    """
    Setzt das Standard-Modell eines Providers in der config.json.

    Legt den Pfad ``providers.<provider>.model`` an, falls er noch nicht
    existiert. Alle anderen Felder der Datei bleiben unverändert.

    Args:
        provider:    Provider-Name (z. B. ``"openai"``, ``"deepseek"``).
        model:       Modell-Bezeichnung (z. B. ``"gpt-4o"``, ``"deepseek-reasoner"``).
        config_path: Pfad zur config.json (wird überschrieben).

    Raises:
        FileNotFoundError: Wenn ``config_path`` nicht existiert.
        ValueError:        Wenn ``provider`` oder ``model`` leer sind.

    Example:
        set_default_model("openai",    "gpt-4o",             "LLM_Client/config.json")
        set_default_model("deepseek",  "deepseek-reasoner",  "LLM_Client/config.json")
    """
    if not provider:
        raise ValueError("provider darf nicht leer sein.")
    if not model:
        raise ValueError("model darf nicht leer sein.")

    config = load_config(config_path)
    config.setdefault("providers", {}).setdefault(provider, {})["model"] = model

    _write_config(config_path, config)


def load_prompts_file(prompts_path: str, name: str | None = None) -> dict:
    """
    Lädt System-, Kontext- und Aufgaben-Prompt aus einer externen JSON-Datei.

    Unterstützt zwei Formate:

    **Variante a — einzelnes Prompt-Set** (direkt verwendbar):

    .. code-block:: json

        {
          "system":  "Du bist ein hilfreicher Assistent.",
          "context": "Optionaler Hintergrundtext.",
          "task":    "Fasse den Kontext zusammen."
        }

    **Variante b — mehrere benannte Prompt-Sets** (Auswahl per ``name``):

    .. code-block:: json

        {
          "summarize": {
            "system":  "Du bist ein Zusammenfassungs-Assistent.",
            "context": "",
            "task":    "Fasse den Text in drei Stichpunkten zusammen."
          },
          "translate": {
            "system":  "Du bist ein Übersetzer.",
            "context": "",
            "task":    "Übersetze den folgenden Text ins Englische."
          }
        }

    Args:
        prompts_path: Pfad zur JSON-Datei.
        name:         Optionaler Name des Prompt-Sets (nur für Variante b).
                      Bei Variante a wird ``name`` ignoriert.
                      Fehlt ``name`` bei Variante b, wird ``"default"`` verwendet.

    Returns:
        Dict mit den Schlüsseln ``system``, ``context``, ``task``.
        Fehlende Schlüssel werden mit leerem String aufgefüllt.

    Raises:
        FileNotFoundError: Wenn ``prompts_path`` nicht existiert.
        KeyError:          Wenn ``name`` in Variante b nicht gefunden wird.
        ValueError:        Wenn das Format nicht erkennbar ist.

    Examples:
        # Variante a — einzelnes Set
        prompts = load_prompts_file("prompts.json")

        # Variante b — benanntes Set
        prompts = load_prompts_file("prompts.json", name="summarize")
        prompts = load_prompts_file("prompts.json", name="translate")
    """
    data = load_config(prompts_path)

    if not isinstance(data, dict):
        raise ValueError(f"'{prompts_path}' enthält kein JSON-Objekt.")

    # Variante a erkennen: mindestens einer der Prompt-Schlüssel vorhanden
    prompt_keys = {"system", "context", "task"}
    if prompt_keys & data.keys():
        # Einzelnes Prompt-Set — name wird ignoriert
        return {
            "system":  data.get("system",  ""),
            "context": data.get("context", ""),
            "task":    data.get("task",    ""),
        }

    # Variante b: jeder Wert muss ein Dict sein
    for key, val in data.items():
        if not isinstance(val, dict):
            raise ValueError(
                f"'{prompts_path}' hat weder das Format eines einzelnen Prompt-Sets "
                f"(Schlüssel: system/context/task) noch einer benannten Sammlung "
                f"(jeder Wert muss ein Dict sein). Gefunden bei Schlüssel '{key}': {val!r}"
            )

    # Namen auflösen: explizit > "default" > einziger Eintrag
    resolved_name = name or "default"
    if resolved_name not in data:
        if not name and len(data) == 1:
            resolved_name = next(iter(data))
        else:
            available = list(data.keys())
            raise KeyError(
                f"Prompt-Set '{resolved_name}' nicht in '{prompts_path}' gefunden. "
                f"Verfügbar: {available}"
            )

    entry = data[resolved_name]
    return {
        "system":  entry.get("system",  ""),
        "context": entry.get("context", ""),
        "task":    entry.get("task",    ""),
    }


def _write_config(config_path: str, data: dict) -> None:
    """Schreibt *data* als formatiertes JSON nach *config_path*."""
    path = Path(config_path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


# ---------------------------------------------------------------------------
# URL-Context-Resolver
# ---------------------------------------------------------------------------

_URL_PATTERN = re.compile(r"https?://\S+")


def fetch_context_urls(text: str) -> str:
    """
    Erkennt HTTP(S)-URLs in text (via Regex) und ersetzt jede URL
    durch den abgerufenen Textinhalt.

    Unterstützte Formate (anhand Content-Type-Header und Dateiendung):
        PDF  (application/pdf, .pdf)   → Textextraktion via pypdf
        HTML (text/html, .html/.htm)   → Textextraktion via BeautifulSoup
        Text (text/plain, JSON, XML …) → direkt verwenden

    Optionale Abhängigkeiten — nur bei Bedarf importiert:
        pip install requests           # Basis-HTTP-Abruf
        pip install pypdf              # PDF-Unterstützung
        pip install beautifulsoup4     # HTML-Bereinigung
    oder gemeinsam:
        pip install ".[url-fetch]"

    Kann nicht abgerufene URLs (Netzwerkfehler, fehlende Pakete) werden
    durch eine lesbare Fehlermeldung ersetzt; der Rest des Textes bleibt
    unverändert.

    Args:
        text: Beliebiger Text, der 0–n URLs enthalten kann.

    Returns:
        text mit ersetzten URL-Inhalten.

    Example:
        ctx = "Analysiere bitte https://example.com/report.pdf"
        resolved = fetch_context_urls(ctx)
        # → "Analysiere bitte [Inhalt von https://example.com/report.pdf]\\n<PDF-Text>"
    """
    if not text or not _URL_PATTERN.search(text):
        return text

    def _fetch(url: str) -> str:
        try:
            import requests as _req
        except ImportError:
            raise ImportError(
                "requests-Paket für URL-Abruf erforderlich: pip install requests"
            )
        resp = _req.get(url, timeout=30, headers={"User-Agent": "LLM-Client/1.0"})
        resp.raise_for_status()
        ct = resp.headers.get("Content-Type", "").lower()
        url_path = url.lower().split("?")[0]

        if "pdf" in ct or url_path.endswith(".pdf"):
            return _extract_pdf(resp.content)
        if "html" in ct or url_path.endswith((".html", ".htm")):
            return _extract_html(resp.text)
        return resp.text

    def _extract_pdf(data: bytes) -> str:
        try:
            import pypdf
        except ImportError:
            raise ImportError(
                "pypdf-Paket für PDF-Unterstützung erforderlich: pip install pypdf"
            )
        from io import BytesIO
        reader = pypdf.PdfReader(BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(p.strip() for p in pages if p.strip())

    def _extract_html(html: str) -> str:
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            return soup.get_text(separator="\n", strip=True)
        except ImportError:
            # Fallback ohne beautifulsoup4: einfache Tag-Entfernung
            return re.sub(r"<[^>]+>", " ", html).strip()

    def _replace(match: re.Match) -> str:
        url = match.group(0).rstrip(".,;:!?\"')>]")
        try:
            content = _fetch(url)
            return f"[Inhalt von {url}]\n{content}"
        except Exception as exc:
            return f"[Fehler beim Laden von {url}: {exc}]"

    return _URL_PATTERN.sub(_replace, text)


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def extract_json(text: str) -> str:
    """
    Extrahiert den ersten gültigen JSON-Block aus text.

    Sucht in folgender Reihenfolge:
    1. Markdown-Code-Block  ```json ... ```  oder  ``` ... ```
    2. Rohes JSON-Objekt  { ... }
    3. Rohes JSON-Array   [ ... ]

    Returns:
        Der extrahierte JSON-String (ohne umgebenden Markdown).

    Raises:
        ValueError: Wenn kein gültiges JSON gefunden wird.

    Example:
        extract_json('Ergebnis:\\n```json\\n{"x": 1}\\n```')
        # → '{"x": 1}'
    """
    # 1. Markdown-Code-Block
    match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', text)
    if match:
        candidate = match.group(1).strip()
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            pass

    # 2. Rohes JSON-Objekt oder -Array (greedy: von erstem Zeichen bis letztem)
    for pattern in (r'\{[\s\S]*\}', r'\[[\s\S]*\]'):
        match = re.search(pattern, text)
        if match:
            candidate = match.group(0).strip()
            try:
                json.loads(candidate)
                return candidate
            except json.JSONDecodeError:
                pass

    raise ValueError("Kein gültiges JSON in der Antwort gefunden.")


def format_output(response: str, header_lines: list, fmt: str) -> str:
    """
    Formatiert die Ausgabe für das Schreiben in eine Datei oder stdout.

    Args:
        response:     Die rohe Antwort des Modells.
        header_lines: Liste der Header-Zeilen (Provider, Model, ...).
        fmt:          Ausgabeformat:
                        'header' — Header + Trennlinie + "Response:" + Antwort
                        'plain'  — nur der Antwort-Text
                        'json'   — nur der extrahierte JSON-Block

    Returns:
        Formatierter String (endet immer mit \\n).

    Raises:
        ValueError: Bei unbekanntem Format oder wenn JSON-Extraktion fehlschlägt.

    Examples:
        format_output(resp, lines, "header")  # vollständige Ausgabe mit Header
        format_output(resp, lines, "plain")   # nur die Antwort
        format_output(resp, lines, "json")    # nur der JSON-Block
    """
    if fmt == "header":
        return "\n".join(header_lines) + "\n" + "-" * 60 + "\nResponse:\n" + response + "\n"
    if fmt == "plain":
        return response + "\n"
    if fmt == "json":
        return extract_json(response) + "\n"
    raise ValueError(f"Unbekanntes Ausgabeformat: '{fmt}'. Wähle: header, plain, json")


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
    parser.add_argument("--config",   required=True, help="Path to JSON config file")
    parser.add_argument("--preset",   default=None,  help=(
        "Preset alias defined in config.json under 'presets'.\n"
        "Sets provider + model in one step. Overridden by explicit --provider/--model."
    ))
    parser.add_argument("--provider", default=None,  choices=provider_choices,
                        help="Provider override (overrides --preset):\n  " + "\n  ".join(provider_choices))
    parser.add_argument("--model",    default=None,  help="Model override (overrides --preset, optional)")
    parser.add_argument("--prompts-file", default=None, metavar="PATH",
                        help=(
                            "Externe JSON-Datei mit Prompts (überschreibt 'prompts' in config.json).\n"
                            "Variante a — einzelnes Set:  {\"system\":..., \"context\":..., \"task\":...}\n"
                            "Variante b — benannte Sets:  {\"name\": {\"system\":..., ...}, ...}"
                        ))
    parser.add_argument("--prompts-name", default=None, metavar="NAME",
                        help="Name des Prompt-Sets (nur für Variante b, Standard: 'default')")
    parser.add_argument("--output", default=None, metavar="DATEI",
                        help="Ausgabe zusätzlich in eine Datei schreiben.\n"
                             "Format wird durch --output-format gesteuert.")
    parser.add_argument("--output-format", default="header", dest="output_format",
                        choices=["header", "plain", "json"],
                        help=(
                            "Format der Dateiausgabe (Standard: header):\n"
                            "  header — Header + Trennlinie + Response (wie Konsole)\n"
                            "  plain  — nur der Antwort-Text, kein Header\n"
                            "  json   — nur der extrahierte JSON-Block (alles andere wird weggeschnitten)"
                        ))
    parser.add_argument("--set-api-key",      nargs=2, metavar=("PROVIDER", "KEY"),
                        help="API-Key in config.json schreiben und beenden.\n"
                             "Beispiel: --set-api-key openai sk-...")
    parser.add_argument("--set-default-model", nargs=2, metavar=("PROVIDER", "MODEL"),
                        help="Standard-Modell in config.json schreiben und beenden.\n"
                             "Beispiel: --set-default-model openai gpt-4o")
    args = parser.parse_args()

    # --- Write-Modus: config.json aktualisieren und sofort beenden -----------
    if args.set_api_key:
        provider_w, key_w = args.set_api_key
        set_api_key(provider_w, key_w, args.config)
        print(f"API-Key für '{provider_w}' wurde in '{args.config}' gespeichert.")
        sys.exit(0)

    if args.set_default_model:
        provider_w, model_w = args.set_default_model
        set_default_model(provider_w, model_w, args.config)
        print(f"Standard-Modell für '{provider_w}' auf '{model_w}' gesetzt in '{args.config}'.")
        sys.exit(0)
    # -------------------------------------------------------------------------

    config = load_config(args.config)

    # Auto-load presets from config if present
    if config.get("presets"):
        mapping_reload(config)

    # Resolve provider + model:
    # Priority: --provider/--model (explicit) > --preset > config default_provider
    provider_name = args.provider
    model_override = args.model

    if args.preset and not (args.provider and args.model):
        preset_provider, preset_model = resolve_preset(args.preset)
        if not provider_name:
            provider_name = preset_provider
        if not model_override:
            model_override = preset_model or None

    provider_name = provider_name or config.get("default_provider", "openai")

    if args.prompts_file:
        prompts = load_prompts_file(args.prompts_file, name=args.prompts_name)
    else:
        prompts = config.get("prompts", {})
    system  = prompts.get("system",  "Du bist ein hilfreicher Assistent.")
    context = prompts.get("context", "")
    task    = prompts.get("task",    "")

    # HTTP(S)-URLs im Kontext automatisch abrufen und durch Inhalt ersetzen
    context = fetch_context_urls(context)

    if not task.strip():
        print("ERROR: 'prompts.task' is empty in the config file.", file=sys.stderr)
        sys.exit(1)

    provider = build_provider(provider_name, config, model_override=model_override)

    preset_info = f" (preset: {args.preset})" if args.preset else ""
    prompts_info = f" (file: {args.prompts_file}" + (f", name: {args.prompts_name}" if args.prompts_name else "") + ")" if args.prompts_file else ""

    header_lines = [f"Provider : {provider_name}{preset_info}"]
    if prompts_info:
        header_lines.append(f"Prompts  :{prompts_info}")
    header_lines.append(f"Model    : {provider.model}")
    header_lines.append(f"System   : {system[:80]}{'...' if len(system) > 80 else ''}")
    header_lines.append(f"Context  : {context[:80]}{'...' if len(context) > 80 else ''}" if context else "Context  : (none)")
    header_lines.append(f"Task     : {task[:80]}{'...' if len(task) > 80 else ''}")

    for line in header_lines:
        print(line)
    print("-" * 60)

    response = provider.send(system=system, context=context, task=task)

    # Konsolenausgabe: bei json-Format JSON extrahieren, sonst Originalantwort
    if args.output_format == "json":
        try:
            console_response = extract_json(response)
        except ValueError as exc:
            print(f"WARNUNG: {exc}", file=sys.stderr)
            console_response = response
    else:
        console_response = response

    print("Response:")
    print(console_response)

    # Dateiausgabe (zusätzlich zur Konsole)
    if args.output:
        try:
            content = format_output(response, header_lines, args.output_format)
            Path(args.output).write_text(content, encoding="utf-8")
            print(f"\nAusgabe geschrieben nach: {args.output}")
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
