# OpenAI

[Zurück zur Übersicht](README.md)

**Unternehmen:** OpenAI (San Francisco, USA)
**Gegründet:** 2015
**API-Konsole:** platform.openai.com
**Preisübersicht:** openai.com/api/pricing
**Dokumentation:** platform.openai.com/docs
**Status:** status.openai.com

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2026-03-05 | **GPT-5.4 Thinking** und **GPT-5.4 Pro** veröffentlicht — neues Frontier-Modell für professionelle Arbeit |
| 2026-03-03 | **GPT-5.3 Instant** veröffentlicht — ersetzt GPT-5.2 Instant als Standard für alle ChatGPT-Nutzer |
| 2026-03-04 | DALL-E 3 eingestellt — GPT Image 1.5 ist Nachfolger |
| 2026-02-13 | GPT-4o, GPT-4.1, GPT-4.1 mini, o4-mini und GPT-5 (Instant/Thinking) aus ChatGPT entfernt |
| 2026-02-05 | **GPT-5.3-Codex** veröffentlicht — vereint Codex + GPT-5, ~25% schneller |
| 2025-12-11 | **GPT-5.2** veröffentlicht — Instant + Thinking + Pro Varianten, GPT-5.2-Codex |
| 2025-08-07 | **GPT-5** veröffentlicht — erster Release der GPT-5-Familie |
| 2025-04 | **GPT-4.1** und **GPT-4.1 mini** veröffentlicht |
| 2025-02 | **o3** und **o3-mini** Reasoning-Modelle veröffentlicht |
| 2024-12 | **o1** Reasoning-Modell allgemein verfügbar |
| 2024-05 | **GPT-4o** veröffentlicht — multimodal (Text, Bild, Audio) |
| 2024-01 | **GPT-4 Turbo** (128k Kontext) veröffentlicht |
| 2023-11 | **GPT-4 Vision** und **DALL-E 3** veröffentlicht |
| 2023-03 | **GPT-4** veröffentlicht |
| 2022-11 | **ChatGPT** (GPT-3.5) gestartet |

---

## Aktuelle Modelle (März 2026)

### GPT-5-Familie

| Modell | Typ | Kontext | Input-Preis | Output-Preis | Besonderheiten |
|---|---|---|---|---|---|
| `gpt-5.4` (Thinking) | Frontier/Reasoning | 200k | ~$2.00/1M | ~$14.00/1M | Stärkstes Modell, Reasoning + Coding + Agenten |
| `gpt-5.4-pro` | Frontier (erweitert) | 200k | höher | höher | Höchste Kapazität, für härteste Aufgaben, Pro/Enterprise |
| `gpt-5.3-instant` | Chat (Standard) | 200k | ~$1.50/1M | ~$10.00/1M | Standard für alle ChatGPT-Nutzer, schnell |
| `gpt-5.3-codex` | Agentic Coding | 200k | — | — | Bestes Coding-Agent-Modell, vereint Codex + GPT-5 |
| `gpt-5.2` | Chat/Reasoning | 200k | $1.75/1M | $14.00/1M | Instant + Thinking Varianten |
| `gpt-5.2-codex` | Coding | 200k | — | — | Spezialisierter Code-Agent |

### Bild- und Medienmodelle

| Modell | Beschreibung |
|---|---|
| `gpt-image-1.5` | Nativ in GPT-5 integriert, ersetzt DALL-E 3, 4× schneller, #1 auf LM Arena |
| `sora` (Sora 2) | Video-Generierung, bis 20s, kinematische Qualität, synchronisierter Audio |

### Audio-Modelle

| Modell | Beschreibung |
|---|---|
| `whisper-1` | Speech-to-Text |
| `tts-1` / `tts-1-hd` | Text-to-Speech (6 Stimmen) |

### Embedding-Modelle

| Modell | Dimensionen | Beschreibung |
|---|---|---|
| `text-embedding-3-large` | 3072 | Höchste Qualität |
| `text-embedding-3-small` | 1536 | Günstiger, schneller |

### Eingestellte Modelle (nicht mehr verfügbar)

| Modell | Eingestellt am | Nachfolger |
|---|---|---|
| GPT-4o | 2026-02-13 | GPT-5.3 Instant |
| GPT-4.1 / GPT-4.1 mini | 2026-02-13 | GPT-5.3 Instant |
| o3 / o4-mini | 2026-02-13 | GPT-5.4 Thinking |
| GPT-5 (Instant/Thinking) | 2026-02-13 | GPT-5.3 / GPT-5.4 |
| DALL-E 3 | 2026-03-04 | GPT Image 1.5 |

---

## API-Besonderheiten

- **Thinking-Modus:** GPT-5.4 Thinking zeigt erweiterten Denkprozess bei komplexen Aufgaben
- **Prompt Caching:** Gecachte Inputs nur $0.175/1M statt $1.75/1M (90% günstiger)
- **Structured Outputs:** JSON-Schema-konforme Ausgaben mit `response_format`
- **Function Calling:** Natives Tool-Use-System für Agenten
- **Batch API:** Bis zu 50 % günstiger für nicht-zeitkritische Anfragen
- **Assistants API:** Verwaltete Threads, File Search, Code Interpreter
- **Codex:** Agentic Coding — plant, schreibt, testet und iteriert autonom

## Authentifizierung

```python
from openai import OpenAI
client = OpenAI(api_key="sk-...")
```

## Typischer API-Aufruf

```python
from openai import OpenAI
client = OpenAI(api_key="sk-...")

response = client.chat.completions.create(
    model="gpt-5.4",
    messages=[
        {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
        {"role": "user", "content": "Erkläre Quantencomputing in drei Sätzen."}
    ]
)
print(response.choices[0].message.content)
```

---

## Preisrechner-Tipp

Die aktuellen Preise ändern sich regelmäßig. Immer die offizielle Pricing-Seite prüfen:
openai.com/api/pricing
