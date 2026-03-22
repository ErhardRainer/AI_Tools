# Veo 3.1 — Google DeepMind

[Zurück zur Übersicht](README.md)

**Anbieter:** Google DeepMind
**Web-Interface:** Google AI Studio / VideoFX
**API-Konsole:** cloud.google.com/vertex-ai
**Dokumentation:** cloud.google.com/vertex-ai/generative-ai/docs/video/overview

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2026-01 | **Veo 3.1** über Vertex AI und Google AI Studio verfügbar — natives Audio, Dialoge |
| 2025-10 | **Veo 3** veröffentlicht — synchronisierte Soundeffekte, 4K |
| 2025-02 | Veo 2 über Vertex AI API verfügbar |
| 2024-12 | Veo 2 angekündigt |
| 2024-05 | Veo 1 auf Google I/O vorgestellt |

---

## Technische Details

| Eigenschaft | Veo 3.1 (aktuell) |
|---|---|
| Max. Länge | 2+ Minuten |
| Auflösung | bis 4K |
| Audio | Nativer Audio-Output: Dialoge, Soundeffekte, Ambient |
| Preismodell | Ab $0.15/Sekunde (Fast Mode) |

---

## Besonderheiten

- **Nativer Audio-Output:** Dialoge, Soundeffekte, Ambient-Geräusche, Musik — alles synchron zum Video
- **4K-Auflösung:** Höchste Auflösung unter Video-Generierungsmodellen
- **Über 2 Minuten:** Deutlich längere Videos als die meisten Alternativen
- **Per-Second-Pricing:** Transparentes Preismodell ab $0.15/Sekunde
- **Runway-Integration:** Auch über Runway-Plattform unter einem Abo nutzbar (neben Gen-4.5)

## API-Aufruf

```python
import vertexai
from vertexai.preview.vision_models import VideoGenerationModel

vertexai.init(project="mein-projekt", location="us-central1")
model = VideoGenerationModel.from_pretrained("veo-3.1")

response = model.generate_videos(
    prompt="Ein goldener Retriever spielt am Strand bei Sonnenuntergang",
    aspect_ratio="16:9",
    duration_seconds=8,
)
```
