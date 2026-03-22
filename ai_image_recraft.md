# Recraft V3

[Zurück zur Übersicht](README.md)

**Anbieter:** Recraft (Tel Aviv, Israel)
**Web-Interface:** recraft.ai
**API-Konsole:** recraft.ai/docs
**Dokumentation:** recraft.ai/docs

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2025-01 | Recraft V3 veröffentlicht — #1 auf Text-to-Image-Benchmarks |
| 2024-11 | Recraft V3 auf Hugging Face FLUX-vergleichbar |
| 2024-06 | Recraft V2 mit verbessertem SVG-Export |

---

## Aktuelle Modelle

| Modell | Typ | Besonderheiten |
|---|---|---|
| **Recraft V3** | Bildgenerierung | SOTA-Qualität, #1 Benchmark-Ergebnisse |
| **Recraft V3 SVG** | Vektorgrafiken | Direkte SVG-Ausgabe |

---

## Besonderheiten

- **Vektorgrafiken:** Einziger Anbieter neben Adobe mit nativer SVG-Generierung
- **Brand-Konsistenz:** Farben, Schriften, Stile konsistent halten
- **Design-Fokus:** Optimiert für Design-Workflows (Logos, Icons, Illustrationen)
- **Multi-Layer:** Elemente einzeln editierbar
- **Benchmark-Leader:** #1 auf ELO-basierten Text-to-Image-Rankings
- **Style Library:** Vordefinierte und eigene Stile
- **Mockup-Generierung:** Produktdarstellungen und Mockups

## Preise

| Plan | Preis/Monat | Bilder |
|---|---|---|
| Free | $0 | 50 Bilder/Tag |
| Basic | $25 | 2000 Bilder/Monat |
| Pro | $60 | 5000 Bilder/Monat |

## API-Aufruf

```python
import requests

response = requests.post(
    "https://external.api.recraft.ai/v1/images/generations",
    headers={"Authorization": "Bearer ..."},
    json={
        "prompt": "Ein minimalistisches Logo für ein Tech-Startup",
        "style": "digital_illustration",
        "model": "recraftv3",
    },
)
```

## Wann Recraft?

- **Design-Projekte:** Logos, Icons, Illustrationen
- **Vektorgrafiken:** Wenn SVG-Ausgabe benötigt wird
- **Brand-Arbeit:** Konsistente visuelle Identität
