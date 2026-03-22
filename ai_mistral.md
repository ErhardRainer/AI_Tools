# Mistral AI

[Zurück zur Übersicht](README.md)

**Unternehmen:** Mistral AI (Paris, Frankreich)
**Gegründet:** 2023
**API-Konsole:** console.mistral.ai
**Preisübersicht:** mistral.ai/pricing
**Dokumentation:** docs.mistral.ai
**API-Basis-URL:** `https://api.mistral.ai/v1` (OpenAI-kompatibel)

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2026-03-17 | **Mistral Small 4** veröffentlicht — 119B MoE (6B aktiv), vereint Reasoning + Vision + Code |
| 2026-02 | **Devstral 2** und **Devstral Small 2** (24B) veröffentlicht — agentic Coding |
| 2026-01 | **Magistral Small** (Open-Source) und **Magistral Medium** — erste Reasoning-Modelle |
| 2025-12-02 | **Mistral 3** Familie veröffentlicht — Mistral Large 3 (675B MoE), Ministral 3 (14B/8B/3B) |
| 2025-07 | **Devstral Small 1.1** veröffentlicht |
| 2025-06 | **Mistral Small 3.2** (24B) veröffentlicht |
| 2025-03 | **Mistral Medium 3** veröffentlicht — „Medium is the new Large" |
| 2025-01 | **Codestral 25.01** — Code-Spezialist mit 256k Kontext |
| 2024-09 | **Pixtral 12B** — erstes Vision-Modell |
| 2024-07 | **Mistral Large 2** (123B Parameter) |
| 2024-02 | **Mistral Large** erstmals veröffentlicht |

---

## Aktuelle Modelle (März 2026)

### Frontier-Modelle (API)

| Modell | Architektur | Kontext | Input-Preis | Output-Preis | Besonderheiten |
|---|---|---|---|---|---|
| `mistral-small-4` | 119B MoE (6B aktiv) | 128k | — | — | Vereint Reasoning + Vision + Code, neuestes Modell |
| `mistral-large-3` | 675B MoE (41B aktiv) | 128k | $0.50/1M | $1.50/1M | Open-Weight Frontier, Apache 2.0 |
| `mistral-medium-3` | — | 128k | $0.40/1M | $2.00/1M | Ausgewogene Variante |
| `mistral-small-3.2` | 24B (dense) | 128k | $0.07/1M | $0.20/1M | Sehr günstig, schnell |

### Spezialisierte Modelle

| Modell | Typ | Besonderheiten |
|---|---|---|
| `magistral-medium` | Reasoning | Chain-of-Thought für komplexe Aufgaben |
| `magistral-small` | Reasoning (Open-Source) | Reasoning unter Apache 2.0 |
| `devstral-2` | Agentic Coding | Agent-fähiger Code-Spezialist |
| `devstral-small-2` | Agentic Coding (24B) | Schlägt Qwen 3 Coder Flash (30B) |
| `pixtral-large` | Vision | Multimodal (Text + Bild) |
| `mistral-embed` | Embedding | Texteinbettungen |

### Ministral 3 (Open-Weight, Apache 2.0)

| Modell | Parameter | Varianten | Besonderheiten |
|---|---|---|---|
| Ministral 3 14B | 14B | Base, Instruct, Reasoning | Stärkstes kleines Modell |
| Ministral 3 8B | 8B | Base, Instruct, Reasoning | Guter Kompromiss |
| Ministral 3 3B | 3B | Base, Instruct, Reasoning | Für Edge-Geräte |

---

## API-Besonderheiten

- **EU-basiert:** Server in Europa — relevant für DSGVO
- **Apache 2.0:** Alle kleinen Modelle und Mistral Large 3 unter Apache 2.0
- **OpenAI-kompatible API:** Standard `openai`-Package funktioniert
- **Magistral Reasoning:** Eigene Reasoning-Modelllinie
- **Devstral Coding:** Spezialisierte agentic Coding-Modelle
- **Function Calling:** Natives Tool-Use-System
- **Le Chat:** Kostenloses Web-Interface

## Typischer API-Aufruf

```python
from openai import OpenAI

client = OpenAI(api_key="...", base_url="https://api.mistral.ai/v1")

response = client.chat.completions.create(
    model="mistral-large-3",
    messages=[
        {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
        {"role": "user", "content": "Erkläre Quantencomputing in drei Sätzen."}
    ]
)
print(response.choices[0].message.content)
```
