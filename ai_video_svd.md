# Stable Video Diffusion — Stability AI

[Zurück zur Übersicht](README.md)

**Anbieter:** Stability AI (London, UK)
**GitHub:** github.com/Stability-AI/generative-models
**Modell-Downloads:** Hugging Face (`stabilityai/stable-video-diffusion-*`)

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2024-11 | SVD 1.1 — verbesserte Bewegungsqualität |
| 2024-03 | Stable Video Diffusion XT (25 Frames) veröffentlicht |
| 2023-11 | Stable Video Diffusion angekündigt — erstes Open-Weight-Video-Modell |

---

## Aktuelle Modelle

| Modell | Frames | Auflösung | Lizenz | Besonderheiten |
|---|---|---|---|---|
| **SVD XT 1.1** | 25 Frames | 576×1024 | Stability Community | Verbesserte Qualität |
| **SVD XT** | 25 Frames | 576×1024 | Stability Community | Mehr Frames |
| **SVD** | 14 Frames | 576×1024 | Stability Community | Basis-Modell |

---

## Besonderheiten

- **Open-Weight:** Frei herunterladbar und lokal ausführbar
- **Image-to-Video:** Generiert Video aus einem Standbild
- **Lokal ausführbar:** Auf Consumer-GPUs (ab 12 GB VRAM)
- **ComfyUI-kompatibel:** Direkt in bestehende Workflows integrierbar
- **Forschungs-Basis:** Grundlage für viele Community-Erweiterungen
- **Kein Text-to-Video:** Nur Image-to-Video (Bild → kurzes Video)

## Lokale Ausführung

### ComfyUI (empfohlen)

```bash
# 1. ComfyUI installieren (siehe ai_image_stablediffusion.md)
# 2. SVD-Modell herunterladen von Hugging Face
# 3. In models/checkpoints/ ablegen
# 4. SVD-Workflow in ComfyUI laden
```

### Python (diffusers)

```python
import torch
from diffusers import StableVideoDiffusionPipeline
from PIL import Image

pipe = StableVideoDiffusionPipeline.from_pretrained(
    "stabilityai/stable-video-diffusion-img2vid-xt",
    torch_dtype=torch.float16,
)
pipe.to("cuda")

image = Image.open("input.png").resize((1024, 576))
frames = pipe(image, num_frames=25).frames[0]

# Frames als Video speichern
from diffusers.utils import export_to_video
export_to_video(frames, "output.mp4", fps=8)
```

## Hardware-Anforderungen

| Modell | Min. VRAM | Empfohlen |
|---|---|---|
| SVD (14 Frames) | 12 GB | 16 GB |
| SVD XT (25 Frames) | 16 GB | 24 GB |

## Einschränkungen

- Nur Image-to-Video (kein Text-to-Video)
- Kurze Videos (3-4 Sekunden)
- Niedrigere Auflösung als kommerzielle Alternativen
- Bewegungskonsistenz bei komplexen Szenen begrenzt
