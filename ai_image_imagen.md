# Google Imagen 4

[Zurück zur Übersicht](README.md)

**Anbieter:** Google DeepMind
**Web-Interface:** In Gemini integriert (gemini.google.com)
**API-Konsole:** aistudio.google.com / cloud.google.com/vertex-ai
**Dokumentation:** cloud.google.com/vertex-ai/generative-ai/docs/image/overview

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2026-01 | **Imagen 4** und **Nano Banana Pro** veröffentlicht — neue Generation |
| 2025-08 | Imagen 3 allgemein verfügbar über Vertex AI |
| 2024-12 | Imagen 3 in Gemini integriert |
| 2024-08 | Imagen 3 angekündigt |

---

## Aktuelle Modelle

| Modell | Beschreibung |
|---|---|
| **Imagen 4** | Neueste Generation, in Google AI Studio verfügbar |
| **Nano Banana Pro** | Schnelle Bildgenerierung, Preview |
| **Nano Banana 2** | Preview-Variante |

---

## Besonderheiten

- **In Gemini integriert:** Direkt im Gemini Chat nutzbar
- **Google AI Studio:** Kostenloser Zugang für Experimente
- **Vertex AI:** Enterprise-API mit SLAs
- **SynthID:** Unsichtbares Wasserzeichen zur Erkennung KI-generierter Bilder

## API-Aufruf (Vertex AI)

```python
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

vertexai.init(project="mein-projekt", location="us-central1")
model = ImageGenerationModel.from_pretrained("imagen-4.0-generate")

response = model.generate_images(
    prompt="Ein Sonnenuntergang über den Alpen, Ölgemälde-Stil",
    number_of_images=1,
    aspect_ratio="16:9",
)
response[0].save("output.png")
```
