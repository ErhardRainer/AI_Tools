# LLM Client

Ein Python-Script, das einen **System-Prompt**, **Kontext-Prompt** und **Aufgaben-Prompt** an verschiedene KI-Anbieter sendet. Alle API-Keys und Einstellungen werden aus einer JSON-Konfigurationsdatei gelesen — kein Hardcoding von Secrets.

---

## Unterstützte Anbieter

| Anbieter | Klasse | Standard-Modell |
|---|---|---|
| `openai` | `OpenAIProvider` | `gpt-4o` |
| `claude` | `ClaudeProvider` | `claude-sonnet-4-6` |
| `gemini` | `GeminiProvider` | `gemini-2.0-flash` |

---

## Voraussetzungen

Python 3.10 oder neuer. Je nach verwendetem Anbieter das entsprechende Package installieren:

```bash
pip install openai                  # für OpenAI
pip install anthropic               # für Anthropic Claude
pip install google-generativeai     # für Google Gemini
```

Alle drei auf einmal:

```bash
pip install openai anthropic google-generativeai
```

---

## Einrichtung

**1. Config-Datei anlegen**

```bash
cp config.template.json config.json
```

**2. API-Keys eintragen**

`config.json` öffnen und die Platzhalter ersetzen:

```json
{
  "default_provider": "openai",

  "providers": {
    "openai": {
      "api_key": "sk-...",
      "model": "gpt-4o"
    },
    "claude": {
      "api_key": "sk-ant-...",
      "model": "claude-sonnet-4-6"
    },
    "gemini": {
      "api_key": "AIza...",
      "model": "gemini-2.0-flash"
    }
  },

  "prompts": {
    "system":  "Du bist ein hilfreicher Assistent.",
    "context": "Hier steht optionaler Kontext, z.B. ein Dokument.",
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
python llm_client.py --config config.json --provider claude
python llm_client.py --config config.json --provider gemini
python llm_client.py --config config.json --provider openai
```

### Anbieter und Modell überschreiben

```bash
python llm_client.py --config config.json --provider openai  --model gpt-4o-mini
python llm_client.py --config config.json --provider claude  --model claude-opus-4-6
python llm_client.py --config config.json --provider gemini  --model gemini-2.0-pro
```

### Alle Optionen

```
usage: llm_client.py [-h] --config CONFIG [--provider {openai,claude,gemini}] [--model MODEL]

Argumente:
  --config CONFIG     Pfad zur JSON-Konfigurationsdatei  (Pflichtfeld)
  --provider          Anbieter überschreiben: openai | claude | gemini
  --model             Modell überschreiben (optional)
```

---

## Die drei Prompt-Felder

| Feld | Bedeutung | Kann leer sein? |
|---|---|---|
| `system` | Rollenanweisung / Persönlichkeit des Assistenten | Nein (Fallback: „Du bist ein hilfreicher Assistent.") |
| `context` | Optionaler Hintergrundtext, z.B. ein Dokument, eine E-Mail, Code | Ja — wird dann übersprungen |
| `task` | Die eigentliche Aufgabe oder Frage | Nein — Pflichtfeld |

### Wie die Prompts an die API übermittelt werden

```
┌─────────────┬──────────────────────┬───────────────────────┬──────────────────────────┐
│ Prompt      │ OpenAI               │ Claude                │ Gemini                   │
├─────────────┼──────────────────────┼───────────────────────┼──────────────────────────┤
│ system      │ role: "system"       │ system= Parameter     │ system_instruction=      │
│ context     │ role: "user" + ack   │ role: "user" + ack    │ vor task eingefügt       │
│ task        │ role: "user" (final) │ role: "user" (final)  │ nach context eingefügt   │
└─────────────┴──────────────────────┴───────────────────────┴──────────────────────────┘
```

Wenn `context` leer ist, wird dieser Schritt vollständig übersprungen.

---

## Beispiel-Ausgabe

```
Provider : claude
Model    : claude-sonnet-4-6
System   : Du bist ein Experte für deutsche Grammatik.
Context  : Der folgende Text ist ein Entwurf für eine Pressemitteilung: [...]
Task     : Korrigiere alle Grammatikfehler und verbessere den Stil.
------------------------------------------------------------
Response:
[Antwort des Modells erscheint hier]
```

---

## Konfigurationsstruktur (vollständige Referenz)

```json
{
  "default_provider": "openai",         // Welcher Anbieter standardmäßig verwendet wird

  "providers": {
    "openai": {
      "api_key": "sk-...",              // OpenAI API Key (platform.openai.com)
      "model":   "gpt-4o"              // Modell-ID (z.B. gpt-4o, gpt-4o-mini, gpt-3.5-turbo)
    },
    "claude": {
      "api_key": "sk-ant-...",          // Anthropic API Key (console.anthropic.com)
      "model":   "claude-sonnet-4-6"   // Modell-ID (z.B. claude-opus-4-6, claude-haiku-4-5-20251001)
    },
    "gemini": {
      "api_key": "AIza...",             // Google AI Studio API Key (aistudio.google.com)
      "model":   "gemini-2.0-flash"    // Modell-ID (z.B. gemini-2.0-pro, gemini-1.5-pro)
    }
  },

  "prompts": {
    "system":  "...",                   // Rollenanweisung
    "context": "...",                   // Optionaler Hintergrundtext (kann leer bleiben)
    "task":    "..."                    // Aufgabe / Frage (Pflichtfeld)
  }
}
```

---

## Architektur

```
llm_client.py
│
├── load_config(path)              Liest die JSON-Konfiguration
├── get_nested(data, "a.b.c")     Dot-Path-Zugriff auf verschachtelte Dicts
│
├── OpenAIProvider                 Implementierung für OpenAI Chat Completions API
│   └── send(system, context, task) → str
├── ClaudeProvider                 Implementierung für Anthropic Messages API
│   └── send(system, context, task) → str
├── GeminiProvider                 Implementierung für Google Generative AI
│   └── send(system, context, task) → str
│
├── build_provider(name, config, model_override)   Factory-Funktion
└── main()                         CLI-Einstiegspunkt (argparse)
```

---

## Dateien

| Datei | Beschreibung |
|---|---|
| `llm_client.py` | Hauptscript |
| `config.template.json` | Konfigurationsvorlage — in `config.json` kopieren und befüllen |
| `config.json` | Echte Konfiguration mit API-Keys (nicht im Repository, via `.gitignore` ausgeschlossen) |

---

## Sicherheitshinweise

- `config.json` **niemals** ins Repository committen
- Die Datei ist in `../.gitignore` eingetragen und wird automatisch ignoriert
- API-Keys nur in `config.json` speichern — niemals direkt im Script oder in Notebooks hardcoden
- Für Produktionsumgebungen Umgebungsvariablen oder einen Secrets-Manager bevorzugen
