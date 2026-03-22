# CLAUDE.md — AI Assistant Guide for This Repository

## Repository Overview

This repository (`AI_Tools`) is a comprehensive knowledge base and tool collection for **Artificial Intelligence** — covering LLMs, image generation, video generation, programmatic API access, and AI agents. The project is documented in German with some English identifiers.

**Repository description (README):** _"Werkzeugsammlung rund um Künstliche Intelligenz — LLMs, Bildgenerierung, Videogenerierung, programmatischer Zugriff und KI-Agenten."_

---

## Structure

```
<<<<<<< HEAD
AI_Tools/
├── README.md                          # Main overview (LLMs, Image, Video, Agents)
├── CLAUDE.md                          # This file
├── .gitignore                         # Excludes real config.json and secrets
├── pyproject.toml                     # Python package definition
│
├── ai_openai.md                       # Detail page: OpenAI
├── ai_claude.md                       # Detail page: Anthropic Claude
├── ai_google.md                       # Detail page: Google Gemini / Gemma
├── ai_xai.md                          # Detail page: xAI Grok
├── ai_mistral.md                      # Detail page: Mistral AI
├── ai_deepseek.md                     # Detail page: DeepSeek
├── ai_moonshot.md                     # Detail page: Moonshot AI / Kimi
├── ai_meta.md                         # Detail page: Meta LLaMA
├── ai_microsoft.md                    # Detail page: Microsoft Phi
├── ai_alibaba.md                      # Detail page: Alibaba Qwen
├── ai_cohere.md                       # Detail page: Cohere
├── ai_zhipu.md                        # Detail page: Zhipu AI / GLM
├── ai_groq.md                         # Detail page: Groq
├── ai_together.md                     # Detail page: Together AI
├── ai_fireworks.md                    # Detail page: Fireworks AI
│
├── ai_image_dalle.md                  # Detail page: DALL-E
├── ai_image_midjourney.md             # Detail page: Midjourney
├── ai_image_stablediffusion.md        # Detail page: Stable Diffusion
├── ai_image_flux.md                   # Detail page: Flux
├── ai_image_firefly.md                # Detail page: Adobe Firefly
├── ai_image_imagen.md                 # Detail page: Google Imagen
├── ai_image_ideogram.md               # Detail page: Ideogram
├── ai_image_leonardo.md               # Detail page: Leonardo AI
├── ai_image_recraft.md                # Detail page: Recraft
│
├── ai_video_sora.md                   # Detail page: Sora
├── ai_video_veo.md                    # Detail page: Veo
├── ai_video_runway.md                 # Detail page: Runway
├── ai_video_kling.md                  # Detail page: Kling
├── ai_video_pika.md                   # Detail page: Pika
├── ai_video_luma.md                   # Detail page: Luma Dream Machine
├── ai_video_minimax.md                # Detail page: MiniMax / Hailuo
├── ai_video_svd.md                    # Detail page: Stable Video Diffusion
│
├── Assistant_AI/
│   └── Assistant_AI.ipynb             # Assistants API notebook (47 cells)
│
└── LLM_Client/
    ├── llm_client.py                  # Multi-provider LLM client script
    ├── config.template.json           # Config template (copy → config.json)
    ├── examples/                      # PowerShell example scripts
    └── unittest/                      # Unit tests
=======
OpenAI/
├── README.md                          # Repository-Übersicht
├── CLAUDE.md                          # This file
├── .gitignore                         # Excludes real config.json and secrets
├── pyproject.toml                     # Package build config (pip install .)
├── Assistant_AI/
│   └── Assistant_AI.ipynb             # Assistants API notebook (47 cells)
├── LLM_Client/                        # Text → Text (8 Provider)
│   ├── llm_client.py
│   └── config.template.json
├── ImageGen/                          # Text → Bild (4 Provider)
│   ├── image_gen.py
│   └── config.template.json
└── llm-api/                           # FastAPI: /chat + /image
    ├── api.py
    ├── Dockerfile
    ├── docker-compose.yml
    ├── requirements.txt
    ├── examples/
    │   └── requests.ps1
    └── tests/
        └── test_api.py
>>>>>>> origin/claude/add-claude-documentation-h4UFb
```

---

## The Main Notebook: `Assistant_AI/Assistant_AI.ipynb`

This notebook is a comprehensive reference implementation for the **OpenAI Assistants API** (beta). It is structured as a sequential workflow:

### Section 0 — Setup
- Dependency imports: `pprint`, `json`, `time`, `openai`, `os`, `pandas`
- Guards with `try/except ImportError` with descriptive error messages
- Uses a `get_value_from_json_file(json_file_path, key_path)` utility to read config (e.g. API key) from a JSON file using dot-separated key paths
- The OpenAI `client` is initialized from config stored in a JSON file (not hardcoded)

### Section 1 — File Upload (Knowledgebase)
Manages files uploaded to OpenAI for use as a retrieval knowledge base.

| Function | Description |
|---|---|
| `upload_files(directory_path)` | Upload all allowed files from a directory |
| `upload_file(filepath)` | Upload a single file |
| `upload_files_array(filepaths)` | Upload a list of file paths |
| `get_files(purpose_filter, filename_pattern)` | List files, optionally filtered; returns a DataFrame |
| `convert_xlsx_to_csv(xlsx_file_path, csv_file_path, skip_rows)` | Convert Excel to CSV before uploading |
| `delete_unassociated_files()` | Delete files not linked to any assistant |

Allowed file extensions: `.pdf`, `.txt`, `.json`, `.csv`

Upload limits: 512 MB per file, 100 GB total storage.

### Section 2 — Assistant Management
Creates and manages OpenAI Assistants.

| Function | Description |
|---|---|
| `create_assistant(name, instruction, retrieval, code_interpreter, file_ids, model)` | Create a new assistant; model defaults to `gpt-4-1106-preview` |
| `update_assistant(assistant_id, ...)` | Update existing assistant attributes (reads current state first) |
| `add_files_assistant(assistant_id, new_file_ids)` | Add files to an existing assistant |
| `get_assistants(name, dataframe)` | List assistants, optionally filter by name; can return DataFrame |
| `get_assistant_attributes(assistant_id)` | Retrieve attributes dict (id, name, model, created_at, file_ids, tools) |
| `get_file_association(assistant_name)` | Map files to their associated assistants |
| `delete_assistant_by_name(name)` | Delete all assistants matching a given name |

### Section 3 — Conversation (Threads)
Implements a full conversation loop using OpenAI threads.

| Step | API Call |
|---|---|
| Create thread | `client.beta.threads.create()` |
| Add user message | `client.beta.threads.messages.create(thread_id, role='user', content=...)` |
| Run assistant | `client.beta.threads.runs.create(thread_id, assistant_id, instructions=...)` |
| Poll status | `client.beta.threads.runs.retrieve(thread_id, run_id)` in a `while` loop with `time.sleep(10)` |
| Read response | `client.beta.threads.messages.list(thread_id)` |

The run polling pattern waits until `run.status` is `"completed"` or `"failed"`.

---

## Key Conventions

### Language
- **Code**: Python, with English function/variable names
- **Comments and markdown cells**: German
- **Mixed**: Some docstrings are in English

### Configuration
- API keys and config values are read from an external JSON file using `get_value_from_json_file()` — never hardcoded in the notebook
- The OpenAI client is created as `client = openai.OpenAI(api_key=...)`

### Coding patterns
- Functions always check current state before modifying (e.g. `update_assistant` reads existing attributes first)
- File operations return two lists: `uploaded_files` and `not_uploaded_files`
- DataFrames (pandas) are used for structured listing of files and assistants
- Error handling uses `try/except` with descriptive `ImportError` messages for missing dependencies

### OpenAI API version
- Uses the **beta Assistants API** (`client.beta.assistants`, `client.beta.threads`)
- Default model: `gpt-4-1106-preview`
- Tool types used: `retrieval` and `code_interpreter`

---

---

## LLM_Client — Multi-Provider Package

`LLM_Client/` is an installable Python package. It sends a **system prompt**, **context prompt**, and **task prompt** to one of eight LLM providers. Usable as a script, module, installed CLI, or importable library. All keys and settings come from a JSON config file.

### Package structure

```
LLM_Client/
├── __init__.py          # re-exports public API (OpenAIProvider, build_provider, ...)
├── __main__.py          # enables: python -m LLM_Client
├── llm_client.py        # core: provider classes, factory, main()
├── config.template.json
├── examples/            # PowerShell example scripts, one per provider
└── unittest/            # unit tests, no real API calls needed
```

### Three invocation modes

```bash
python LLM_Client/llm_client.py --config LLM_Client/config.json --provider grok  # script
python -m LLM_Client            --config LLM_Client/config.json --provider grok  # module
llm-client                      --config LLM_Client/config.json --provider grok  # CLI (after pip install .)
```

### Installation

```bash
pip install .           # openai only (covers 6 providers)
pip install ".[claude]" # + anthropic
pip install ".[gemini]" # + google-generativeai
pip install ".[all]"    # all SDKs
```

### Supported Providers

| Provider | Standard-Modell | SDK / Abhängigkeit |
|---|---|---|
| `openai` | `gpt-4o` | `pip install openai` |
| `claude` | `claude-sonnet-4-6` | `pip install anthropic` |
| `gemini` | `gemini-2.0-flash` | `pip install google-generativeai` |
| `grok` | `grok-3` | `pip install openai` (OpenAI-kompatibel) |
| `kimi` | `kimi-k2` | `pip install openai` (OpenAI-kompatibel) |
| `deepseek` | `deepseek-chat` | `pip install openai` (OpenAI-kompatibel) |
| `groq` | `llama-3.3-70b-versatile` | `pip install openai` (OpenAI-kompatibel) |
| `mistral` | `mistral-large-latest` | `pip install openai` (OpenAI-kompatibel) |

Grok, Kimi, DeepSeek, Groq und Mistral verwenden intern `_OpenAICompatibleProvider` — sie setzen nur `BASE_URL` und `DEFAULT_MODEL` und benötigen kein eigenes SDK.

### Setup

```bash
cp LLM_Client/config.template.json LLM_Client/config.json
# Edit config.json and fill in your API keys
```

`config.json` is excluded from git via `.gitignore`.

### Config file structure

```json
{
  "default_provider": "openai",
  "providers": {
    "openai":  { "api_key": "sk-...",     "model": "gpt-4o" },
    "claude":  { "api_key": "sk-ant-...", "model": "claude-sonnet-4-6" },
    "gemini":  { "api_key": "AIza...",    "model": "gemini-2.0-flash" }
  },
  "prompts": {
    "system":  "You are a helpful assistant.",
    "context": "Optional background information or document content.",
    "task":    "Summarize the context in three bullet points."
  }
}
```

### Running

```bash
# Use the default_provider from config
python LLM_Client/llm_client.py --config LLM_Client/config.json

# Override provider at runtime
python LLM_Client/llm_client.py --config LLM_Client/config.json --provider grok
python LLM_Client/llm_client.py --config LLM_Client/config.json --provider kimi
python LLM_Client/llm_client.py --config LLM_Client/config.json --provider deepseek

# Override provider and model
python LLM_Client/llm_client.py --config LLM_Client/config.json --provider deepseek --model deepseek-reasoner
python LLM_Client/llm_client.py --config LLM_Client/config.json --provider groq     --model gemma2-9b-it
python LLM_Client/llm_client.py --config LLM_Client/config.json --provider mistral  --model codestral-latest
```

### Prompt flow

The three prompts are mapped to API roles as follows:

| Prompt | OpenAI role | Claude param | Gemini |
|---|---|---|---|
| `system` | `system` message | `system=` parameter | `system_instruction=` |
| `context` | `user` turn (followed by a brief assistant ack) | same | prepended to user content |
| `task` | final `user` turn | final `user` turn | appended to user content |

If `context` is empty, it is skipped entirely.

### Architecture

- `load_config(path)` — reads JSON config
- `get_nested(data, "a.b.c")` — dot-path accessor
- `set_api_key(provider, api_key, config_path)` — writes `providers.<provider>.api_key` into config.json; preserves all other fields
- `set_default_model(provider, model, config_path)` — writes `providers.<provider>.model` into config.json; preserves all other fields
- `_write_config(config_path, data)` — internal helper; writes dict as indented JSON
- `extract_json(text)` — extracts the first valid JSON block from text; tries markdown code fences first, then raw `{...}`/`[...]`; raises `ValueError` if none found
- `format_output(response, header_lines, fmt)` — formats output for file writing; `fmt` is `"header"` (full header + response), `"plain"` (response only), or `"json"` (extracted JSON only); raises `ValueError` for unknown format or missing JSON
- `fetch_context_urls(text)` — detects HTTP(S)-URLs in text via regex and replaces each with the fetched content; supports PDF (via `pypdf`), HTML (via `beautifulsoup4`, with tag-strip fallback), and plain text; unreachable URLs are replaced with an error message; optional deps: `requests`, `pypdf`, `beautifulsoup4` (`pip install ".[url-fetch]"`)
- `load_prompts_file(path, name?)` — loads a `{system, context, task}` dict from an external JSON file; supports two formats:
  - **Variante a** (single set): `{"system": ..., "context": ..., "task": ...}`
  - **Variante b** (named sets): `{"summarize": {"system": ..., ...}, "translate": {...}}` — select via `name`; falls back to `"default"` or the only entry if `name` omitted
- `PRESET_REGISTRY` — module-level dict: alias → `{"provider": ..., "model": ...}`
- `mapping_reload(source)` — loads/reloads preset mapping from a JSON file path or dict; mutates `PRESET_REGISTRY` in-place so all references stay valid
- `resolve_preset(name)` — returns `(provider, model)` tuple for an alias; raises `KeyError` if unknown
- `OpenAIProvider`, `ClaudeProvider`, `GeminiProvider` — native SDKs, each with `.send(system, context, task) → str`
- `_OpenAICompatibleProvider` — base class for OpenAI-compatible APIs; subclasses set `BASE_URL` + `DEFAULT_MODEL`
  - `GrokProvider` (api.x.ai/v1), `KimiProvider` (api.moonshot.cn/v1), `DeepSeekProvider` (api.deepseek.com), `GroqProvider` (api.groq.com/openai/v1), `MistralProvider` (api.mistral.ai/v1)
- `PROVIDERS` dict — registry mapping provider name → class
- `build_provider(name, config, model_override)` — factory that instantiates the right class
- `main()` — CLI entry point with `argparse`; supports `--preset` (auto-loads from config, overridable by `--provider`/`--model`); `--output PATH` writes output to file; `--output-format {header,plain,json}` controls file content

---

## Development Workflow

### Prerequisites
```bash
pip install openai pandas openpyxl pprint
```

### Running the notebook
```bash
jupyter notebook Assistant_AI/Assistant_AI.ipynb
```
or
```bash
jupyter lab
```

### Typical workflow
1. Configure your OpenAI API key in a JSON config file
2. Run **Section 0** to initialize the client
3. Run **Section 1** to upload knowledge base files
4. Run **Section 2** to create/configure an assistant
5. Run **Section 3** to start a conversation thread

### Git branches
- `master` / `main` — stable branch
- `claude/...` — AI-generated feature/documentation branches

### README-Pflege
Jede `README.md` im Repository muss aktuell gehalten werden. Bei jeder Änderung an Code, Konfiguration, Schnittstellen oder Verzeichnisstruktur ist die zugehörige `README.md` im selben Verzeichnis **im gleichen Commit** zu aktualisieren. Das gilt für alle Ebenen:
- `/README.md` — bei strukturellen Änderungen am Repository
- `LLM_Client/README.md` — bei Änderungen an `llm_client.py` oder `config.template.json`
- `llm-api/README.md` — bei Änderungen an `llm-api/api.py`, `Dockerfile` oder `docker-compose.yml`

### Pflichtbestandteile jeder Erweiterung

Jede neue Funktion, jeder neue Provider oder jedes neue Feature **muss** im selben Commit folgende zwei Artefakte enthalten:

#### 1. Unit-Test in `LLM_Client/unittest/test_<feature>.py`

- Keine echten API-Calls — alle externen Abhängigkeiten werden mit `unittest.mock` gemockt
- Testklassen nach Feature gruppieren (z. B. `TestMappingReloadFromDict`, `TestResolvePreset`)
- Abdeckung: Happy Path, Fehlerfälle (`ValueError`, `KeyError`, `FileNotFoundError`), Randfälle (leere Eingaben, fehlende optionale Felder)
- Neue Testdatei im Runner `LLM_Client/unittest/run_all_tests.py` registrieren, damit sie automatisch ausgeführt wird
- Vor jedem Commit ausführen: `python LLM_Client/unittest/run_all_tests.py` — alle Tests müssen grün sein

#### 2. PowerShell-Wrapper in `LLM_Client/examples/run_<feature>.ps1`

- Zeigt alle sinnvollen Aufrufvarianten des neuen Features (Script, Modul, CLI, ggf. programmatisch)
- Kommentare auf Deutsch, die erklären was der jeweilige Aufruf macht
- Nicht verwendete/optionale Varianten als auskommentierte Zeilen (`#`) mit Erklärung
- Referenziert die Config relativ zum Skript: `$Config = "$PSScriptRoot\..\config.json"`

**Checkliste vor jedem Commit:**
- [ ] Unit-Tests geschrieben und alle grün (`python LLM_Client/unittest/run_all_tests.py`)
- [ ] PowerShell-Wrapper angelegt unter `LLM_Client/examples/run_<feature>.ps1`
- [ ] `README.md` und `CLAUDE.md` aktualisiert
- [ ] Kein Secret / API-Key im Code oder in Templates hardcodiert

---

## ImageGen — Multi-Provider Bildgenerierung

`ImageGen/` ist ein installierbares Python-Paket für Bildgenerierung (Text → Bild). Gleiche Architektur wie `LLM_Client`.

### Unterstützte Provider

| Provider | Klasse | Standard-Modell | SDK |
|---|---|---|---|
| `openai` | `OpenAIImageProvider` | `dall-e-3` | `pip install openai` |
| `google` | `GoogleImageProvider` | `imagen-4.0-generate-001` | `pip install google-genai` — Imagen 4 via `generate_images()`, Gemini Flash Image via `generate_content()` |
| `stability` | `StabilityProvider` | `core` | `pip install requests` — core, ultra, sd3/sd3.5 Varianten |
| `fal` | `FalProvider` | `fal-ai/flux/dev` | `pip install requests` (REST API) |
| `ideogram` | `IdeogramProvider` | `V_3` | `pip install requests` — V_3, V_2A, V_2; `Api-Key` Header |
| `leonardo` | `LeonardoProvider` | Phoenix 1.0 UUID | `pip install requests` — async Job-System mit Polling |
| `firefly` | `FireflyProvider` | `firefly-image-model-3` | `pip install requests` — OAuth2 Client Credentials (`client_id` + `client_secret`) |
| `auto1111` | `Auto1111Provider` | _(aktuell geladen)_ | `pip install requests` — lokale A1111-Instanz, kein API-Key |
| `ollamadiffuser` | `OllamaDiffuserProvider` | `flux.1-schnell` | `pip install requests` — lokaler ollamadiffuser-Server, kein API-Key |

### Installation

```bash
pip install ".[imagegen]"   # requests + google-genai
pip install openai           # zusätzlich für DALL-E
```

### Architecture

- `ImageData` — einzelnes Bild: `url`, `b64_json`, `save(path)`
- `ImageResult` — Ergebnis: `provider`, `model`, `images[]`, `revised_prompt`, `save_all(pattern)`
- `OpenAIImageProvider` — DALL-E 3/2; `.generate(prompt, size, quality, n, response_format)`
- `GoogleImageProvider` — Imagen 4/3 (`generate_images`) + Gemini Flash Image (`generate_content`); Modellerkennung via Prefix
- `StabilityProvider` — Core/Ultra/SD3/SD3.5 via REST; `.generate(prompt, aspect_ratio, negative_prompt, n)`
- `FalProvider` — FLUX via REST; `.generate(prompt, image_size, n)`
- `IdeogramProvider` — V3/V2A/V2 via REST; `Api-Key` Header; URLs werden sofort heruntergeladen
- `LeonardoProvider` — async: Job anlegen → pollen bis `COMPLETE`; `.generate(prompt, n, width, height)`
- `FireflyProvider` — OAuth2 Client Credentials; Token wird gecacht; `.generate(prompt, n, size)`
- `Auto1111Provider` — lokale A1111-Instanz; optionaler Checkpoint-Wechsel via `/sdapi/v1/options`
- `OllamaDiffuserProvider` — lokaler ollamadiffuser-Server; `.generate(prompt, n)` → rohe Bild-Bytes
- `PROVIDERS` dict — Registry `name → Klasse`
- `build_provider(name, config, model_override)` — Factory; Sonderbehandlung für `firefly` (OAuth2) und lokale Provider (kein api_key nötig)
- `mapping_reload(source)` / `resolve_preset(name)` — Preset-System (identisch zu LLM_Client)
- `main()` — CLI mit `--prompt`, `--provider`, `--preset`, `--model`, `--output`, `--n`, `--size`, `--quality`, `--aspect-ratio`

### Tests

```bash
python ImageGen/unittest/run_all_tests.py
```

---

## LLM API — FastAPI-Wrapper

`llm-api/` stellt alle LLM_Client-Provider als REST-API bereit, deploybar als Docker-Container.

### Endpunkte

| Methode | Pfad | Beschreibung |
|---|---|---|
| `GET` | `/health` | Liveness-Check |
| `GET` | `/providers` | Registrierte Provider + Presets |
| `POST` | `/chat` | Prompt senden, Antwort empfangen |
| `GET` | `/docs` | Swagger-UI (automatisch generiert) |

### Starten

```bash
# Lokal
pip install ".[all]" fastapi uvicorn
cd llm-api && uvicorn api:app --reload

# Docker Compose (empfohlen)
docker compose -f llm-api/docker-compose.yml up --build
```

### Konfiguration

| Env-Variable | Standard | Beschreibung |
|---|---|---|
| `LLM_CONFIG` | `../LLM_Client/config.json` | Pfad zur config.json |
| `API_KEY` | (leer) | HTTP-Auth-Key; leer = keine Authentifizierung |

### Architektur `llm-api/api.py`

- `ChatRequest` / `ChatResponse` — Pydantic-Modelle
- `_verify_api_key()` — optionale HTTP-Auth via `X-API-Key`-Header
- `GET /health` — immer offen, kein Auth
- `GET /providers` — listet Text- und Bild-Provider sowie Presets
- `POST /chat` — löst Provider/Preset auf → `build_provider()` → `provider.send()` → optional `extract_json()`
- `POST /image` — löst Bild-Provider/Preset auf → `image_build_provider()` → `provider.generate()` → `ImageResponse`

### Tests

```bash
pip install httpx
python -m pytest llm-api/tests/ -v
```

---

## Things to Watch Out For

- The `retrieval` tool type used in this notebook corresponds to the older Assistants API v1. In newer versions of the OpenAI API, `retrieval` was renamed to `file_search`. If upgrading, update the tool type string in `create_assistant()`.
- `client.beta.assistants.list(limit="20")` — the `limit` is passed as a string; newer SDK versions may require an integer.
- The polling loop in Section 3.4 uses `time.sleep(10)` which can be slow. Consider using exponential backoff or the SDK's built-in `poll()` methods in newer versions.
- No authentication or secrets should be committed — always store the API key in a config file excluded from git (add to `.gitignore` if not already).
