# Adobe Firefly

[Zurück zur Übersicht](README.md)

**Anbieter:** Adobe (San Jose, USA)
**Web-Interface:** firefly.adobe.com
**API-Konsole:** developer.adobe.com/firefly-services
**Dokumentation:** developer.adobe.com/firefly-services/docs

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2025-02 | Firefly Image Model 3 — verbesserte Qualität, schneller |
| 2024-10 | Firefly Vector Model — SVG-Generierung |
| 2024-09 | Firefly Video Model angekündigt |
| 2024-04 | Firefly Image Model 2 veröffentlicht |
| 2023-09 | Firefly in Photoshop, Illustrator und Express integriert |
| 2023-03 | Adobe Firefly Beta gestartet |

---

## Aktuelle Modelle

| Modell | Typ | Besonderheiten |
|---|---|---|
| **Firefly Image 3** | Bildgenerierung | Photorealistisch, Komposition |
| **Firefly Vector** | Vektorgrafiken | SVG-Ausgabe, editierbar |
| **Firefly Design** | Design | Templates, Layouts |

---

## Besonderheiten

- **Kommerziell sicher:** Ausschließlich auf lizenzierten Daten trainiert (Adobe Stock, Public Domain)
- **Adobe-Integration:** Direkt in Photoshop, Illustrator, Premiere Pro, Express
- **Generative Fill:** Teile eines Bildes intelligent ersetzen (Photoshop)
- **Generative Expand:** Bilder über den Rand hinaus erweitern
- **Text Effects:** Stilisierte Texteffekte generieren
- **Vektorgrafiken:** Einziger Anbieter mit nativer SVG-Generierung
- **Content Credentials:** Automatische Metadaten-Kennzeichnung als KI-generiert
- **Enterprise:** Abgesichert für kommerzielle Nutzung (IP-Haftungsschutz)

## Preise

| Plan | Preis | Generative Credits |
|---|---|---|
| Free | $0 | 25 Credits/Monat |
| Creative Cloud | ab $55/Monat | 1000 Credits/Monat |
| Firefly Premium | $10/Monat | 100 Credits/Monat |

## API-Aufruf

```python
import requests

response = requests.post(
    "https://firefly-api.adobe.io/v3/images/generate",
    headers={
        "Authorization": "Bearer ...",
        "x-api-key": "...",
        "Content-Type": "application/json"
    },
    json={
        "prompt": "Ein Sonnenuntergang über den Alpen, Ölgemälde-Stil",
        "n": 1,
        "size": {"width": 2048, "height": 2048}
    },
)
```

## Wann Adobe Firefly?

- **Kommerzielles Projekt:** Keine Urheberrechtsprobleme
- **Adobe-Workflow:** Nahtlose Integration in Creative Cloud
- **Enterprise:** IP-Haftungsschutz inklusive
