# Google — Gemini & Gemma

[Zurück zur Übersicht](README.md)

**Unternehmen:** Google DeepMind (Mountain View, USA)
**API-Konsole:** aistudio.google.com (kostenloser Einstieg) / cloud.google.com/vertex-ai (Enterprise)
**Preisübersicht:** ai.google.dev/pricing
**Dokumentation:** ai.google.dev/docs
**Status:** status.cloud.google.com

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2026-03-03 | **Gemini 3.1 Flash Lite** für Entwickler über Google API veröffentlicht |
| 2026-02-19 | **Gemini 3.1 Pro** veröffentlicht — 77.1% auf ARC-AGI-2, Frontier-Reasoning |
| 2026-01 | **Imagen 4** für Bildgenerierung, **Veo 3.1** für Video veröffentlicht |
| 2025-11-20 | **Gemini 3.0** offiziell gestartet — Flash wird Standard in Gemini-App |
| 2025-06-17 | **Gemini 2.5 Pro/Flash** allgemein verfügbar, **Gemini 2.5 Flash-Lite** neu |
| 2025-03-25 | **Gemini 2.5 Pro** experimentell veröffentlicht |
| 2024-12 | Gemini 2.0 Flash experimentell |
| 2024-09 | Gemini 1.5 Pro mit 2M Kontext (experimentell) |
| 2024-05 | **Gemini 1.5 Flash** veröffentlicht |
| 2024-02 | **Gemini 1.5 Pro** mit 1M Kontext-Token |
| 2023-12 | **Gemini 1.0** veröffentlicht (Ultra, Pro, Nano) |

---

## Aktuelle Modelle (März 2026)

### Gemini 3.1 (aktuell)

| Modell | Typ | Kontext | Besonderheiten |
|---|---|---|---|
| `gemini-3.1-pro` | Flaggschiff/Reasoning | 2M | Stärkstes Gemini, 77.1% ARC-AGI-2, komplexe Aufgaben |
| `gemini-3.1-flash` | Schnell | 2M | Neuer Standard in Gemini-App, Frontier-Leistung |
| `gemini-3.1-flash-lite` | Ultra-günstig | 2M | Günstigstes Modell, High-Volume, Low-Latency |

### Gemini 2.5 (Produktion, stabil)

| Modell | Typ | Kontext | Input-Preis | Output-Preis | Besonderheiten |
|---|---|---|---|---|---|
| `gemini-2.5-pro` | Erweitert | 2M | $1.25/1M | $10.00/1M | Komplexe Aufgaben, stabiles Produktionsmodell |
| `gemini-2.5-flash` | Schnell | 1M | ~$0.10/1M | ~$0.40/1M | Bestes Preis-Leistungs-Verhältnis |
| `gemini-2.5-flash-lite` | Budget | 1M | ~$0.02/1M | ~$0.10/1M | Günstigstes am Markt |

### Spezialisierte Modelle

| Modell | Typ | Beschreibung |
|---|---|---|
| `imagen-4` | Bildgenerierung | Text-to-Image, Nano Banana Pro |
| `veo-3.1` | Videogenerierung | Kinematisch, synchronisiertes Audio, 4K |
| `gemini-embedding-2` | Embedding | Multimodal (Text + Bild) |

### Gemma (Open-Weight, lokal)

| Modell | Parameter | Lizenz | Besonderheiten |
|---|---|---|---|
| `gemma-2-27b` | 27B | Gemma License | Stärkstes offenes Google-Modell |
| `gemma-2-9b` | 9B | Gemma License | Guter Kompromiss |
| `gemma-2-2b` | 2B | Gemma License | Für Edge-Geräte |

---

## API-Besonderheiten

- **2M-Kontextfenster:** Das größte am Markt — ganze Bücher in einer Anfrage
- **Multimodal nativ:** Text, Bild, Audio, Video in einem Modell
- **Grounding mit Google Search:** Antworten mit aktuellen Web-Ergebnissen anreichern
- **Code Execution:** Serverseitiges Python-Ausführen in der API
- **Deep Research Agent:** Autonomer Recherche-Agent über die API
- **Computer Use:** Gemini kann Desktop-Interaktionen steuern
- **Google AI Studio:** Kostenloses Playground-Interface mit großzügigem Free Tier
- **Vertex AI:** Enterprise-Version mit SLAs, VPC, IAM

## Typischer API-Aufruf

```python
import google.generativeai as genai

genai.configure(api_key="AIza...")

model = genai.GenerativeModel(
    model_name="gemini-3.1-flash",
    system_instruction="Du bist ein hilfreicher Assistent."
)

response = model.generate_content("Erkläre Quantencomputing in drei Sätzen.")
print(response.text)
```

---

## Preisrechner-Tipp

Google AI Studio bietet eine großzügige kostenlose Stufe. Für Produktion: ai.google.dev/pricing
