# LLM Client

Ein Python-Paket, das einen **System-Prompt**, **Kontext-Prompt** und **Aufgaben-Prompt** an verschiedene KI-Anbieter sendet. Verwendbar als **Script**, **Python-Modul**, **installierbares CLI** oder **importierbare Bibliothek**. Alle API-Keys und Einstellungen werden aus einer JSON-Konfigurationsdatei gelesen — kein Hardcoding von Secrets.

---

## Drei Aufrufmöglichkeiten

```bash
# 1. Direktes Script (kein Install nötig)
python LLM_Client/llm_client.py --config LLM_Client/config.json --provider grok

# 2. Als Python-Modul (vom Repo-Root aus)
python -m LLM_Client --config LLM_Client/config.json --provider grok

# 3. Als installiertes CLI (nach: pip install .)
llm-client --config LLM_Client/config.json --provider grok

# Mit Preset-Alias statt Provider + Modell:
python LLM_Client/llm_client.py --config LLM_Client/config.json --preset coding
llm-client                      --config LLM_Client/config.json --preset fast
```

---

## Preset-Aliases

Statt Provider und Modellnamen auswendig zu kennen, kann man **sprechende Kurznamen** verwenden. Die Mapping-Tabelle wird in `config.json` unter `"presets"` definiert und ist vollständig konfigurierbar.

### Standard-Presets (aus `config.template.json`)

| Alias | Provider | Modell | Einsatz |
|---|---|---|---|
| `coding` | claude | claude-opus-4-6 | Beste Code-Qualität |
| `balanced` | openai | gpt-4o | Allgemein ausgewogen |
| `fast` | groq | llama-3.1-8b-instant | Maximale Geschwindigkeit |
| `cheap` | deepseek | deepseek-chat | Günstigste Option |
| `reasoning` | deepseek | deepseek-reasoner | Chain-of-Thought / R1 |
| `longctx` | kimi | moonshot-v1-128k | Sehr langer Kontext |
| `creative` | gemini | gemini-2.0-flash | Kreative Aufgaben |
| `code` | mistral | codestral-latest | Code-Spezialist |

### Eigene Presets definieren

In `config.json` einfach neue Einträge unter `"presets"` hinzufügen:

```json
{
  "presets": {
    "coding":   {"provider": "claude",   "model": "claude-opus-4-6"},
    "fast":     {"provider": "groq",     "model": "llama-3.1-8b-instant"},
    "myprojekt":{"provider": "openai",   "model": "gpt-4o-mini"}
  }
}
```

### Preset mit Override kombinieren

`--provider` und `--model` überschreiben einzelne Felder des Presets:

```bash
# Preset "coding" → claude + claude-opus-4-6
# --model überschreibt nur das Modell → claude + claude-sonnet-4-6
llm-client --config config.json --preset coding --model claude-sonnet-4-6
```

### Programmatische Verwendung

```python
from LLM_Client import mapping_reload, resolve_preset, build_provider, load_config

config = load_config("config.json")
mapping_reload(config)                        # Lädt Presets aus config.json

provider_name, model = resolve_preset("coding")
# → ("claude", "claude-opus-4-6")

provider = build_provider(provider_name, config, model_override=model)
print(provider.send("System", "", "Schreibe eine Funktion in Python."))
```

### Zur Laufzeit neu laden

```python
# Presets nach Änderung an config.json neu einlesen — kein Neustart nötig
mapping_reload("config.json")
```

## API-Keys und Standard-Modelle setzen

API-Keys und Standard-Modelle können direkt per CLI oder per Python-Funktion in die `config.json` geschrieben werden — ohne sie manuell im Editor zu öffnen.

```bash
# API-Key für einen Provider setzen
python LLM_Client/llm_client.py --config LLM_Client/config.json --set-api-key openai   "sk-..."
python LLM_Client/llm_client.py --config LLM_Client/config.json --set-api-key claude   "sk-ant-..."
python LLM_Client/llm_client.py --config LLM_Client/config.json --set-api-key deepseek "sk-..."

# Standard-Modell für einen Provider setzen
python LLM_Client/llm_client.py --config LLM_Client/config.json --set-default-model openai   "gpt-4o-mini"
python LLM_Client/llm_client.py --config LLM_Client/config.json --set-default-model deepseek "deepseek-reasoner"
```

Alle anderen Felder der Datei (andere Provider, Presets, Prompts) bleiben unverändert. Existiert der Provider-Eintrag noch nicht, wird er angelegt.

```python
from LLM_Client import set_api_key, set_default_model

set_api_key("openai",   "sk-...",            "LLM_Client/config.json")
set_api_key("claude",   "sk-ant-...",        "LLM_Client/config.json")

set_default_model("openai",   "gpt-4o-mini",         "LLM_Client/config.json")
set_default_model("deepseek", "deepseek-reasoner",    "LLM_Client/config.json")
```

---

## Als importierbare Bibliothek

```python
from LLM_Client import GrokProvider, build_provider, load_config

# Provider direkt instanziieren
provider = GrokProvider(api_key="xai-...", model="grok-3")
antwort = provider.send(
    system="Du bist ein hilfreicher Assistent.",
    context="",
    task="Erkläre Quantencomputing in drei Sätzen.",
)
print(antwort)

# Oder über die Factory (liest config.json)
config = load_config("LLM_Client/config.json")
provider = build_provider("deepseek", config)
print(provider.send("System", "", "Was ist 2+2?"))
```

---

## Unterstützte Anbieter

| Anbieter | Klasse | Standard-Modell | API-Konsole |
|---|---|---|---|
| `openai` | `OpenAIProvider` | `gpt-4o` | platform.openai.com |
| `claude` | `ClaudeProvider` | `claude-sonnet-4-6` | console.anthropic.com |
| `gemini` | `GeminiProvider` | `gemini-2.0-flash` | aistudio.google.com |
| `grok` | `GrokProvider` | `grok-3` | console.x.ai |
| `kimi` | `KimiProvider` | `kimi-k2` | platform.moonshot.cn |
| `deepseek` | `DeepSeekProvider` | `deepseek-chat` | platform.deepseek.com |
| `groq` | `GroqProvider` | `llama-3.3-70b-versatile` | console.groq.com |
| `mistral` | `MistralProvider` | `mistral-large-latest` | console.mistral.ai |

Grok, Kimi, DeepSeek, Groq und Mistral implementieren alle die OpenAI-kompatible Chat Completions API — sie benötigen **kein eigenes SDK**, nur das `openai`-Package.

---

## Installation

### Option A — Paket installieren (empfohlen)

```bash
# Vom Repo-Root:
pip install .                  # Basis (openai SDK, deckt 6 Provider ab)
pip install ".[claude]"        # + anthropic
pip install ".[gemini]"        # + google-generativeai
pip install ".[all]"           # alle SDKs
```

Nach der Installation steht der CLI-Befehl `llm-client` überall zur Verfügung.

### Option B — Direkt verwenden (kein Install)

```bash
pip install openai             # Mindestinstallation
pip install anthropic          # für Claude
pip install google-generativeai  # für Gemini
```

---

## Voraussetzungen

Python 3.10 oder neuer.

```bash
# Mindestinstallation (deckt OpenAI, Grok, Kimi, DeepSeek, Groq, Mistral ab)
pip install openai

# Für Anthropic Claude zusätzlich
pip install anthropic

# Für Google Gemini zusätzlich
pip install google-generativeai

# Alles auf einmal
pip install openai anthropic google-generativeai
```

---

## Einrichtung

**1. Config-Datei anlegen**

```bash
cp config.template.json config.json
```

**2. API-Keys eintragen**

`config.json` öffnen und die Platzhalter der gewünschten Anbieter ersetzen. Nicht benötigte Anbieter können einfach entfernt werden.

```json
{
  "default_provider": "openai",
  "providers": {
    "openai":   { "api_key": "sk-...",    "model": "gpt-4o" },
    "claude":   { "api_key": "sk-ant-..","model": "claude-sonnet-4-6" },
    "gemini":   { "api_key": "AIza...",  "model": "gemini-2.0-flash" },
    "grok":     { "api_key": "xai-...",  "model": "grok-3" },
    "kimi":     { "api_key": "sk-...",   "model": "kimi-k2" },
    "deepseek": { "api_key": "sk-...",   "model": "deepseek-chat" },
    "groq":     { "api_key": "gsk_...",  "model": "llama-3.3-70b-versatile" },
    "mistral":  { "api_key": "...",      "model": "mistral-large-latest" }
  },
  "prompts": {
    "system":  "Du bist ein hilfreicher Assistent.",
    "context": "Hier steht optionaler Kontext.",
    "task":    "Beantworte die folgende Frage: ..."
  }
}
```

> `config.json` ist in `.gitignore` eingetragen und wird **nie** ins Repository committet.

---

## Verwendung

### Standard-Anbieter aus der Config nutzen

```bash
python llm_client.py --config config.json
```

### Anbieter zur Laufzeit überschreiben

```bash
python llm_client.py --config config.json --provider openai
python llm_client.py --config config.json --provider claude
python llm_client.py --config config.json --provider gemini
python llm_client.py --config config.json --provider grok
python llm_client.py --config config.json --provider kimi
python llm_client.py --config config.json --provider deepseek
python llm_client.py --config config.json --provider groq
python llm_client.py --config config.json --provider mistral
```

### Anbieter und Modell überschreiben

```bash
python llm_client.py --config config.json --provider openai    --model gpt-4o-mini
python llm_client.py --config config.json --provider claude    --model claude-opus-4-6
python llm_client.py --config config.json --provider gemini    --model gemini-2.0-pro
python llm_client.py --config config.json --provider grok      --model grok-3-mini
python llm_client.py --config config.json --provider kimi      --model moonshot-v1-128k
python llm_client.py --config config.json --provider deepseek  --model deepseek-reasoner
python llm_client.py --config config.json --provider groq      --model gemma2-9b-it
python llm_client.py --config config.json --provider mistral   --model codestral-latest
```

### Alle CLI-Optionen

```
usage: llm_client.py [-h] --config CONFIG [--provider PROVIDER] [--model MODEL]

  --config CONFIG     Pfad zur JSON-Konfigurationsdatei  (Pflichtfeld)
  --provider          Anbieter überschreiben (siehe Tabelle oben)
  --model             Modell überschreiben (optional)
```

---

## Verfügbare Modelle

### OpenAI
| Modell | Beschreibung |
|---|---|
| `gpt-4o` | Flagship-Modell, Bild + Text |
| `gpt-4o-mini` | Schnell und günstig |
| `o3` | Reasoning-Modell |
| `o4-mini` | Schnelles Reasoning |

### Anthropic Claude
| Modell | Beschreibung |
|---|---|
| `claude-sonnet-4-6` | Standard — ausgewogen |
| `claude-opus-4-6` | Stärkste Variante |
| `claude-haiku-4-5-20251001` | Schnell und kostengünstig |

### Google Gemini
| Modell | Beschreibung |
|---|---|
| `gemini-2.0-flash` | Schnell, Standard |
| `gemini-2.0-pro` | Maximale Leistung |
| `gemini-1.5-pro` | Sehr großes Kontextfenster |

### xAI Grok
| Modell | Beschreibung |
|---|---|
| `grok-3` | Flagship-Modell |
| `grok-3-mini` | Schnell und kompakt |
| `grok-3-fast` | Optimiert für Geschwindigkeit |
| `grok-2-1212` | Vorherige Generation |

### Moonshot AI Kimi
| Modell | Beschreibung |
|---|---|
| `kimi-k2` | Neuestes Flaggschiff (MoE, 1T Parameter) |
| `moonshot-v1-8k` | 8k Kontextfenster |
| `moonshot-v1-32k` | 32k Kontextfenster |
| `moonshot-v1-128k` | 128k Kontextfenster |

### DeepSeek
| Modell | Beschreibung |
|---|---|
| `deepseek-chat` | DeepSeek V3 — Allgemein |
| `deepseek-reasoner` | DeepSeek R1 — Chain-of-Thought Reasoning |

### Groq (schnelle Inferenz)
| Modell | Beschreibung |
|---|---|
| `llama-3.3-70b-versatile` | Meta LLaMA 3.3 70B |
| `llama-3.1-8b-instant` | Sehr schnell, leichtgewichtig |
| `gemma2-9b-it` | Google Gemma 2 9B |
| `mixtral-8x7b-32768` | Mistral MoE, 32k Kontext |

### Mistral AI
| Modell | Beschreibung |
|---|---|
| `mistral-large-latest` | Stärkstes Modell |
| `mistral-small-latest` | Schnell und günstig |
| `codestral-latest` | Spezialisiert auf Code |
| `open-mixtral-8x22b` | Open-Weight MoE |

---

## Die drei Prompt-Felder

| Feld | Bedeutung | Kann leer sein? |
|---|---|---|
| `system` | Rollenanweisung / Persönlichkeit des Assistenten | Nein (Fallback: „Du bist ein hilfreicher Assistent.") |
| `context` | Optionaler Hintergrundtext, z.B. ein Dokument, E-Mail, Code | Ja — wird dann übersprungen |
| `task` | Die eigentliche Aufgabe oder Frage | Nein — Pflichtfeld |

### Wie die Prompts an die APIs übermittelt werden

```
┌─────────────┬──────────────────────┬──────────────────────┬──────────────────────┐
│ Prompt      │ OpenAI / Grok /      │ Claude               │ Gemini               │
│             │ Kimi / DeepSeek /    │                      │                      │
│             │ Groq / Mistral       │                      │                      │
├─────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
│ system      │ role: "system"       │ system= Parameter    │ system_instruction=  │
│ context     │ role: "user" + ack   │ role: "user" + ack   │ vor task eingefügt   │
│ task        │ role: "user" (final) │ role: "user" (final) │ nach context         │
└─────────────┴──────────────────────┴──────────────────────┴──────────────────────┘
```

Wenn `context` leer ist, wird dieser Schritt vollständig übersprungen.

---

## Beispiel-Ausgabe

```
Provider : kimi
Model    : kimi-k2
System   : Du bist ein Experte für Softwarearchitektur.
Context  : Das folgende Dokument beschreibt ein Microservices-System: [...]
Task     : Welche Schwachstellen siehst du in dieser Architektur?
------------------------------------------------------------
Response:
[Antwort des Modells erscheint hier]
```

---

## Architektur

```
llm_client.py
│
├── load_config(path)                  Liest die JSON-Konfiguration
├── get_nested(data, "a.b.c")         Dot-Path-Zugriff auf verschachtelte Dicts
│
├── OpenAIProvider                     Natives OpenAI SDK
├── ClaudeProvider                     Natives Anthropic SDK (system= Parameter)
├── GeminiProvider                     Natives Google Generative AI SDK
│
├── _OpenAICompatibleProvider          Basisklasse für OpenAI-kompatible APIs
│   ├── GrokProvider                   base_url: api.x.ai/v1
│   ├── KimiProvider                   base_url: api.moonshot.cn/v1
│   ├── DeepSeekProvider               base_url: api.deepseek.com
│   ├── GroqProvider                   base_url: api.groq.com/openai/v1
│   └── MistralProvider                base_url: api.mistral.ai/v1
│
├── PROVIDERS { name → Klasse }        Registry aller Provider
├── build_provider(name, config, ...)  Factory-Funktion
└── main()                             CLI-Einstiegspunkt (argparse)
```

### Neuen Provider hinzufügen

Für jeden Anbieter mit OpenAI-kompatibler API reichen 5 Zeilen:

```python
class MeinProviderProvider(_OpenAICompatibleProvider):
    """Mein Anbieter — https://example.com/docs"""
    BASE_URL = "https://api.example.com/v1"
    DEFAULT_MODEL = "mein-modell-v1"

# In PROVIDERS eintragen:
PROVIDERS["meinprovider"] = MeinProviderProvider
```

---

## Tests ausführen

Die Tests liegen in `unittest/` und benötigen keine echten API-Keys (alle SDKs werden gemockt).

```bash
# Alle Tests (kurz)
python LLM_Client/unittest/run_all_tests.py

# Alle Tests (ausführlich)
python LLM_Client/unittest/run_all_tests.py -v

# Einzelnen Provider testen
python -m pytest LLM_Client/unittest/test_grok.py -v

# Über standard unittest discovery
python -m unittest discover -s LLM_Client/unittest -p "test_*.py" -v
```

### Test-Dateien

| Datei | Beschreibung |
|---|---|
| `test_openai.py` | OpenAIProvider — 6 Tests |
| `test_claude.py` | ClaudeProvider — 7 Tests (inkl. system= Parameter) |
| `test_gemini.py` | GeminiProvider — 6 Tests (inkl. context+task-Verkettung) |
| `test_grok.py` | GrokProvider — 6 Tests (inkl. base_url-Prüfung) |
| `test_kimi.py` | KimiProvider — 7 Tests (inkl. Moonshot-Modelle) |
| `test_deepseek.py` | DeepSeekProvider — 7 Tests (inkl. deepseek-reasoner) |
| `test_groq.py` | GroqProvider — 7 Tests (inkl. verschiedene Modelle) |
| `test_mistral.py` | MistralProvider — 7 Tests (inkl. codestral) |
| `test_utils.py` | load_config, get_nested, build_provider — 13 Tests |
| `run_all_tests.py` | Runner-Skript für alle Tests zusammen |

---

## Beispiel-Aufrufe (PowerShell)

Im Ordner `examples/` liegt für jeden Provider ein PowerShell-Skript mit vordefinierten Variablen:

```
examples/
├── run_openai.ps1
├── run_claude.ps1
├── run_gemini.ps1
├── run_grok.ps1
├── run_kimi.ps1
├── run_deepseek.ps1
├── run_groq.ps1
└── run_mistral.ps1
```

Jedes Skript definiert `$Config`, `$Provider` und `$Model` als Variablen und zeigt alle drei Aufrufmöglichkeiten (Script / Modul / CLI). Einfach das passende Skript öffnen, Variablen anpassen und ausführen.

```powershell
# Ausführen (PowerShell):
.\LLM_Client\examples\run_grok.ps1
```

---

## Dateien

| Datei | Beschreibung |
|---|---|
| `__init__.py` | Package-Init — re-exportiert public API |
| `__main__.py` | Einstiegspunkt für `python -m LLM_Client` |
| `llm_client.py` | Kernlogik: Provider-Klassen, Factory, CLI (`main()`) |
| `config.template.json` | Konfigurationsvorlage — in `config.json` kopieren und befüllen |
| `config.json` | Echte Konfiguration mit API-Keys (nicht im Repository, via `.gitignore` ausgeschlossen) |
| `examples/` | PowerShell-Beispielskripte für jeden Provider |
| `unittest/` | Unit-Tests für alle Provider (keine echten API-Calls erforderlich) |

---

## Sicherheitshinweise

- `config.json` **niemals** ins Repository committen
- Die Datei ist in `../.gitignore` eingetragen und wird automatisch ignoriert
- API-Keys nur in `config.json` speichern — niemals direkt im Script oder in Notebooks
- Für Produktionsumgebungen Umgebungsvariablen oder einen Secrets-Manager bevorzugen
