# Ideogram

[Zurück zur Übersicht](README.md)

**Anbieter:** Ideogram (Toronto, Kanada)
**Gegründet:** 2022 (von ehemaligen Google Brain-Mitarbeitern)
**Web-Interface:** ideogram.ai
**API-Konsole:** developer.ideogram.ai
**Dokumentation:** developer.ideogram.ai/docs

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2025-01 | Ideogram 2.0 Turbo — schneller, gleiche Qualität |
| 2024-11 | Ideogram 2.0 veröffentlicht — großer Qualitätssprung |
| 2024-08 | Ideogram 1.0 veröffentlicht |
| 2023-08 | Ideogram Beta — fokussiert auf Text in Bildern |

---

## Aktuelle Modelle

| Modell | Auflösung | Besonderheiten |
|---|---|---|
| **Ideogram 2.0** | bis 1024×1024 | Beste Textdarstellung, photorealistisch |
| **Ideogram 2.0 Turbo** | bis 1024×1024 | Schneller, leicht geringere Qualität |

---

## Besonderheiten

- **Bestes Textrendering:** Marktführer bei korrekter Textdarstellung in Bildern
- **Logo/Typografie:** Ideal für Logos, Poster, Visitenkarten mit Text
- **Magic Prompt:** Automatische Prompt-Verbesserung
- **Style-Kontrolle:** Realistisch, Design, 3D, Anime
- **Negative Prompts:** Unerwünschte Elemente ausschließen
- **API-Zugang:** REST-API für programmatische Nutzung

## Preise

| Plan | Preis/Monat | Bilder |
|---|---|---|
| Free | $0 | 10 Bilder/Tag |
| Basic | $8 | 400 Bilder/Monat |
| Plus | $20 | 1000 Bilder/Monat |
| Pro | $60 | Unbegrenzt (Fair Use) |

## API-Aufruf

```python
import requests

response = requests.post(
    "https://api.ideogram.ai/generate",
    headers={"Api-Key": "..."},
    json={
        "image_request": {
            "prompt": "Ein Schild mit dem Text 'Willkommen in den Alpen'",
            "model": "V_2",
            "magic_prompt_option": "AUTO"
        }
    },
)
```
