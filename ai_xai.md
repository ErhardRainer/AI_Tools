# xAI — Grok

[Zurück zur Übersicht](README.md)

**Unternehmen:** xAI (gegründet von Elon Musk)
**API-Konsole:** console.x.ai
**Preisübersicht:** docs.x.ai/developers/models
**Dokumentation:** docs.x.ai
**API-Basis-URL:** `https://api.x.ai/v1` (OpenAI-kompatibel)

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2026-03 | **Grok 4.20** (0309) veröffentlicht — Reasoning + Non-Reasoning + Multi-Agent Varianten |
| 2026-02 | **Grok Imagine** Video-Generierung öffentlich via API (10s, 720p) |
| 2026-01 | **Grok 5** angekündigt — 6T Parameter, in Training |
| 2025-12 | **Grok 4.2** angekündigt, Grok Business ($30/Seat) und Enterprise Tiers |
| 2025-11 | **Grok 4.1 Fast** veröffentlicht — 2M Kontext, sehr günstig ($0.20/$0.50 pro 1M) |
| 2025-07 | **Grok 4** gelauncht — „intelliegentestes Modell der Welt", SuperGrok Heavy ($300/Monat) |
| 2025-02 | **Grok 3** und **Grok 3 Mini** veröffentlicht — großer Leistungssprung |
| 2024-12 | Grok-2-1212 als API verfügbar |
| 2024-08 | Grok-2 veröffentlicht mit Vision-Fähigkeiten |

---

## Aktuelle Modelle (März 2026)

| Modell-ID | Typ | Kontext | Input-Preis | Output-Preis | Besonderheiten |
|---|---|---|---|---|---|
| `grok-4.20-0309-reasoning` | Frontier/Reasoning | 2M | $2.00/1M | $6.00/1M | Stärkstes Modell mit Denkprozess |
| `grok-4.20-0309-non-reasoning` | Frontier/Chat | 2M | $2.00/1M | $6.00/1M | Schnelle Antworten ohne Chain-of-Thought |
| `grok-4.20-multi-agent-0309` | Multi-Agent | 2M | $2.00/1M | $6.00/1M | Für Multi-Agent-Workflows optimiert |
| `grok-4-1-fast-reasoning` | Schnell/Reasoning | 2M | $0.20/1M | $0.50/1M | Extrem günstig, schnell |
| `grok-4-1-fast-non-reasoning` | Schnell/Chat | 2M | $0.20/1M | $0.50/1M | Günstigste Grok-Variante |

### Bild- und Video-Generierung

| Modell | Preis | Beschreibung |
|---|---|---|
| `grok-imagine-image-pro` | $0.07/Bild | Hochwertige Bildgenerierung |
| `grok-imagine-image` | $0.02/Bild | Schnelle Bildgenerierung |
| `grok-imagine-video` | $0.05/Sekunde | Videogenerierung (10s, 720p) |

---

## API-Besonderheiten

- **OpenAI-kompatible API:** Drop-in-Ersatz — nur Base-URL und API-Key ändern
- **2M-Kontextfenster:** Eines der größten am Markt
- **Multi-Agent-Modell:** Eigenes Modell für Multi-Agent-Orchestrierung
- **Echtzeit-Webzugriff:** Grok hat Zugang zu X/Twitter-Daten
- **Grok Voice:** Sprach-Agent für Tesla-Fahrzeuge und mobile Apps
- **Cached Input:** Nur 10% des Standard-Input-Preises
- **Kein eigenes SDK nötig:** Standard `openai`-Python-Package funktioniert

## Authentifizierung

```python
from openai import OpenAI

client = OpenAI(
    api_key="xai-...",
    base_url="https://api.x.ai/v1"
)
```

## Typischer API-Aufruf

```python
from openai import OpenAI

client = OpenAI(api_key="xai-...", base_url="https://api.x.ai/v1")

response = client.chat.completions.create(
    model="grok-4-1-fast-reasoning",
    messages=[
        {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
        {"role": "user", "content": "Erkläre Quantencomputing in drei Sätzen."}
    ]
)
print(response.choices[0].message.content)
```
