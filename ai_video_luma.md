# Luma Dream Machine

[Zurück zur Übersicht](README.md)

**Anbieter:** Luma AI (San Francisco, USA)
**Gegründet:** 2021
**Web-Interface:** lumalabs.ai/dream-machine
**API-Konsole:** docs.lumalabs.ai
**Dokumentation:** docs.lumalabs.ai

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2025-01 | Dream Machine 1.6 — verbesserte Qualität und Konsistenz |
| 2024-11 | Ray 2 angekündigt — nächste Generation |
| 2024-06 | Dream Machine gelauncht — kostenloser Zugang, viral gegangen |

---

## Technische Details

| Eigenschaft | Wert |
|---|---|
| Max. Länge | 5 Sekunden (erweiterbar) |
| Auflösung | 720p |
| Seitenverhältnisse | 16:9, 9:16, 1:1 |
| Generierungszeit | ~30-60 Sekunden |

---

## Besonderheiten

- **Schnelle Generierung:** Eines der schnellsten Video-Modelle
- **Gute Kamerabewegungen:** Besonders stabile und filmische Kamerafahrten
- **Image-to-Video:** Standbild als Startframe
- **Keyframes:** Start- und Endframe definieren
- **Extend:** Videos verlängern
- **Kostenloses Tier:** Tägliche kostenlose Generierungen
- **API-Zugang:** REST-API für programmatische Nutzung

## Preise

| Plan | Preis/Monat | Generierungen |
|---|---|---|
| Free | $0 | 5 Videos/Tag |
| Standard | $24 | 120 Videos/Monat |
| Pro | $96 | 400 Videos/Monat |

## API-Aufruf

```python
import requests

response = requests.post(
    "https://api.lumalabs.ai/dream-machine/v1/generations",
    headers={"Authorization": "Bearer luma-..."},
    json={
        "prompt": "Ein goldener Retriever spielt am Strand bei Sonnenuntergang",
        "aspect_ratio": "16:9",
    },
)
```
