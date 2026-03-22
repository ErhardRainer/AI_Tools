# Leonardo AI

[Zurück zur Übersicht](README.md)

**Anbieter:** Leonardo AI (Sydney, Australien)
**Gegründet:** 2022
**Web-Interface:** app.leonardo.ai
**API-Konsole:** docs.leonardo.ai
**Dokumentation:** docs.leonardo.ai

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2025-01 | Leonardo Phoenix 1.0 — eigenes Foundation Model |
| 2024-10 | Leonardo Motion — Bild-zu-Video |
| 2024-07 | Leonardo Phoenix angekündigt |
| 2024-01 | Realtime Canvas — Echtzeit-Bildgenerierung |

---

## Aktuelle Modelle

| Modell | Typ | Besonderheiten |
|---|---|---|
| **Leonardo Phoenix** | Eigenes Modell | Bestes Leonardo-Modell, vielseitig |
| **Leonardo Diffusion XL** | SDXL-basiert | Photorealistisch |
| **Leonardo Anime XL** | SDXL-basiert | Anime-Spezialist |
| **Leonardo Kino XL** | SDXL-basiert | Filmische Ästhetik |

---

## Besonderheiten

- **Gaming/Concept-Art-Fokus:** Besonders beliebt bei Game-Entwicklern und Concept Artists
- **Eigene Modelle + SD-basiert:** Sowohl proprietäre als auch Stable-Diffusion-Modelle
- **Realtime Canvas:** Bilder in Echtzeit generieren während man zeichnet
- **AI Canvas:** Inpainting und Outpainting
- **Texture Generation:** 3D-Texturen für Game Assets
- **Leonardo Motion:** Bilder in kurze Videos verwandeln
- **Community-Modelle:** Nutzer können eigene Fine-Tunes teilen
- **Prompt Generation:** KI-gestützte Prompt-Erstellung

## Preise

| Plan | Preis/Monat | Token |
|---|---|---|
| Free | $0 | 150 Token/Tag |
| Apprentice | $12 | 8500 Token/Monat |
| Artisan | $30 | 25000 Token/Monat |
| Maestro | $60 | 60000 Token/Monat |

## API-Aufruf

```python
import requests

response = requests.post(
    "https://cloud.leonardo.ai/api/rest/v1/generations",
    headers={"Authorization": "Bearer ..."},
    json={
        "prompt": "Ein Fantasy-Schloss auf einem Berggipfel, Concept Art",
        "modelId": "...",  # Leonardo Phoenix Model ID
        "width": 1024,
        "height": 768,
        "num_images": 1,
    },
)
```
