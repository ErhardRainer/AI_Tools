# Stable Diffusion — Stability AI

[Zurück zur Übersicht](README.md)

**Anbieter:** Stability AI (London, UK)
**Gegründet:** 2019
**API-Konsole:** platform.stability.ai
**Dokumentation:** platform.stability.ai/docs
**GitHub:** github.com/Stability-AI
**Modell-Downloads:** Hugging Face (`stabilityai/*`)

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2025-01 | Stable Diffusion 3.5 Large Turbo — schneller, gleiche Qualität |
| 2024-10 | Stable Diffusion 3.5 (Medium und Large) veröffentlicht |
| 2024-06 | Stable Diffusion 3 veröffentlicht — neue MMDiT-Architektur |
| 2024-02 | Stable Cascade — neues Pipeline-Design |
| 2023-11 | SDXL Turbo — Echtzeit-Generierung in 1 Schritt |
| 2023-07 | SDXL 1.0 veröffentlicht — 1024×1024 nativ |

---

## Aktuelle Modelle

| Modell | Architektur | Auflösung | Lizenz | Besonderheiten |
|---|---|---|---|---|
| **SD 3.5 Large** | MMDiT (8B) | 1024×1024 | Stability Community | Beste Qualität |
| **SD 3.5 Medium** | MMDiT (2.5B) | 1024×1024 | Stability Community | Guter Kompromiss |
| **SD 3.5 Large Turbo** | MMDiT (8B) | 1024×1024 | Stability Community | 4 Schritte statt 40 |
| **SDXL 1.0** | UNet | 1024×1024 | CreativeML Open | Riesiges Ökosystem, tausende LoRAs |
| **SD 1.5** | UNet | 512×512 | CreativeML Open | Legacy, aber riesige Community |

---

## Besonderheiten

- **Open-Weight:** Alle Modelle frei herunterladbar und lokal ausführbar
- **Riesiges Ökosystem:** Tausende LoRAs, ControlNets, Embeddings, Erweiterungen
- **Lokal ausführbar:** Auf Consumer-GPUs (ab 8 GB VRAM)
- **ComfyUI / Automatic1111:** Beliebte Web-UIs für lokale Nutzung
- **ControlNet:** Präzise Steuerung (Pose, Tiefe, Kanten, etc.)
- **Inpainting/Outpainting:** Teile eines Bildes gezielt bearbeiten
- **img2img:** Bestehende Bilder als Basis für neue Generierung
- **LoRA Fine-Tuning:** Eigene Stile/Konzepte in wenigen Minuten trainieren

## Lokale Ausführung

### ComfyUI (empfohlen)

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
python main.py
# → http://localhost:8188
```

### Automatic1111 WebUI

```bash
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
cd stable-diffusion-webui
./webui.sh
# → http://localhost:7860
```

## API-Aufruf (Stability AI API)

```python
import requests

response = requests.post(
    "https://api.stability.ai/v2beta/stable-image/generate/sd3",
    headers={"Authorization": "Bearer sk-..."},
    files={"none": ""},
    data={
        "prompt": "Ein Sonnenuntergang über den Alpen, Ölgemälde-Stil",
        "model": "sd3.5-large",
        "output_format": "png"
    },
)
with open("output.png", "wb") as f:
    f.write(response.content)
```

## Hardware-Anforderungen (lokal)

| Modell | Min. VRAM | Empfohlen |
|---|---|---|
| SD 1.5 | 4 GB | 8 GB |
| SDXL 1.0 | 8 GB | 12 GB |
| SD 3.5 Medium | 8 GB | 12 GB |
| SD 3.5 Large | 12 GB | 16+ GB |
