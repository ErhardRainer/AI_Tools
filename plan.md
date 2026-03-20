# Implementierungsplan: LLM_Client als installierbares Modul

## Ziel
`LLM_Client` soll auf drei Arten verwendbar sein — mit **minimalen Änderungen** am bestehenden Code:

| Modus | Befehl |
|---|---|
| Direktes Script (wie heute) | `python LLM_Client/llm_client.py --config ...` |
| Python-Modul | `python -m LLM_Client --config ...` |
| Installiertes CLI | `llm-client --config ...` (nach `pip install .`) |
| Import in Code | `from LLM_Client import OpenAIProvider, build_provider` |

---

## Änderungsübersicht

| Datei | Aktion | Umfang |
|---|---|---|
| `LLM_Client/llm_client.py` | **unverändert** | 0 Zeilen |
| `LLM_Client/__init__.py` | **NEU** — re-exportiert public API | ~15 Zeilen |
| `LLM_Client/__main__.py` | **NEU** — `python -m LLM_Client` | 3 Zeilen |
| `pyproject.toml` | **NEU** — `pip install .` + CLI-Eintrag | ~25 Zeilen |
| `LLM_Client/unittest/test_*.py` | **unverändert** — `sys.path.insert` Trick funktioniert weiter | 0 Zeilen |
| `LLM_Client/examples/run_*.ps1` | **NEU** — 8 PowerShell-Beispiele | je ~25 Zeilen |
| `LLM_Client/README.md` | **Update** — neue Aufrufmöglichkeiten dokumentieren | ~30 Zeilen |
| `CLAUDE.md` | **Update** — Paketstruktur aktualisieren | ~10 Zeilen |

**Gesamtänderungen am bestehenden Code: 0 Zeilen** (nur neue Dateien + README-Ergänzung)

---

## Neue Dateien im Detail

### `LLM_Client/__init__.py`
Macht `LLM_Client` zum Python-Package und re-exportiert die öffentliche API:
```python
from .llm_client import (
    load_config, get_nested,
    OpenAIProvider, ClaudeProvider, GeminiProvider,
    GrokProvider, KimiProvider, DeepSeekProvider, GroqProvider, MistralProvider,
    PROVIDERS, build_provider,
)
__all__ = ["load_config", "get_nested", "OpenAIProvider", ...]
```
→ Ermöglicht: `from LLM_Client import OpenAIProvider`

### `LLM_Client/__main__.py`
Einstiegspunkt für `python -m LLM_Client`:
```python
from .llm_client import main
main()
```

### `pyproject.toml` (im Repo-Root)
Paket-Metadaten + CLI-Eintrag:
```toml
[project]
name = "llm-client"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["openai"]

[project.optional-dependencies]
claude  = ["anthropic"]
gemini  = ["google-generativeai"]
all     = ["anthropic", "google-generativeai"]

[project.scripts]
llm-client = "LLM_Client.llm_client:main"
```
→ `pip install .` installiert das Paket + den `llm-client` CLI-Befehl
→ `pip install ".[all]"` installiert alle SDK-Abhängigkeiten

### `LLM_Client/examples/run_<provider>.ps1` (8 Dateien)
Je ein PowerShell-Skript pro Provider. Beispiel `run_grok.ps1`:
```powershell
# Konfiguration (hier anpassen)
$Config   = "$PSScriptRoot\..\config.json"
$Provider = "grok"
$Model    = "grok-3"

# Aufruf 1: direktes Script
python "$PSScriptRoot\..\llm_client.py" --config $Config --provider $Provider --model $Model

# Aufruf 2: als installiertes CLI (nach pip install .)
# llm-client --config $Config --provider $Provider --model $Model

# Aufruf 3: als Python-Modul
# python -m LLM_Client --config $Config --provider $Provider --model $Model
```

---

## Finale Verzeichnisstruktur

```
OpenAI/
├── pyproject.toml                     ← NEU
├── README.md
├── CLAUDE.md
├── .gitignore
├── Assistant_AI/
└── LLM_Client/
    ├── __init__.py                    ← NEU
    ├── __main__.py                    ← NEU
    ├── llm_client.py                  ← UNVERÄNDERT
    ├── config.template.json
    ├── README.md                      ← Update
    ├── examples/
    │   ├── run_openai.ps1             ← NEU
    │   ├── run_claude.ps1             ← NEU
    │   ├── run_gemini.ps1             ← NEU
    │   ├── run_grok.ps1               ← NEU
    │   ├── run_kimi.ps1               ← NEU
    │   ├── run_deepseek.ps1           ← NEU
    │   ├── run_groq.ps1               ← NEU
    │   └── run_mistral.ps1            ← NEU
    └── unittest/
        └── ... (unverändert)
```

---

## Unit Tests — keine Änderungen nötig

Die Tests verwenden `sys.path.insert(0, LLM_Client/)` + `from llm_client import ...`.
Da `llm_client.py` am selben Ort bleibt, funktioniert das weiterhin.
Optional (nicht nötig): Tests könnten auf `from LLM_Client import ...` umgestellt werden.

---

## Installations- und Nutzungsbeispiele nach der Änderung

```bash
# Paket editierbar installieren (Development)
pip install -e .

# Paket mit allen SDK-Abhängigkeiten installieren
pip install -e ".[all]"

# Alle drei Aufrufarten
python LLM_Client/llm_client.py --config LLM_Client/config.json --provider grok
python -m LLM_Client           --config LLM_Client/config.json --provider grok
llm-client                     --config LLM_Client/config.json --provider grok

# Als Modul importieren
python -c "from LLM_Client import GrokProvider; print('OK')"
```
