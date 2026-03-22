# GPT Image 1.5 (ehemals DALL-E) — OpenAI

[Zurück zur Übersicht](README.md)

**Anbieter:** OpenAI
**API-Konsole:** platform.openai.com
**Dokumentation:** platform.openai.com/docs/guides/images
**Web-Interface:** In ChatGPT integriert (alle Pläne)

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2026-03-04 | **DALL-E 3 eingestellt** — GPT Image 1.5 ist offizieller Nachfolger |
| 2025-12 | **GPT Image 1.5** veröffentlicht — nativ in GPT-5 integriert, #1 auf LM Arena |
| 2025-03 | GPT-4o erhält native Bildgenerierung — erstes Anzeichen der DALL-E-Ablösung |
| 2023-11 | DALL-E 3 in ChatGPT und API verfügbar |
| 2023-10 | DALL-E 3 veröffentlicht |
| 2023-04 | DALL-E 2 API allgemein verfügbar |

---

## Aktuelles Modell

### GPT Image 1.5 (aktuell)

| Eigenschaft | Wert |
|---|---|
| Modell-ID | `gpt-image-1.5` |
| Architektur | Nativ multimodal (Teil der GPT-5-Architektur) |
| Auflösungen | Bis 4K |
| Geschwindigkeit | 4× schneller als DALL-E 3 |
| Textrendering | Deutlich verbessert gegenüber DALL-E 3 |
| Ranking | #1 auf LM Arena (Image Generation) |

### Eingestellte Modelle

| Modell | Eingestellt | Nachfolger |
|---|---|---|
| DALL-E 3 | 2026-03-04 | GPT Image 1.5 |
| DALL-E 2 | 2025 | GPT Image 1.5 |

---

## Besonderheiten

- **Nativ multimodal:** Bildgenerierung geschieht im selben Netzwerk wie Textverarbeitung (kein separates Diffusionsmodell)
- **Prompt-Adherence:** Deutlich bessere Befolgung komplexer, mehrteiliger Prompts
- **Photorealismus:** Signifikant verbessert gegenüber DALL-E 3
- **Textrendering:** Korrekter Text in Bildern
- **ChatGPT-Integration:** Iteratives Verfeinern im Chat möglich
- **Konsistente Details:** Weniger Halluzinationen bei Händen, Gesichtern, etc.

## API-Aufruf

```python
from openai import OpenAI
client = OpenAI(api_key="sk-...")

response = client.images.generate(
    model="gpt-image-1.5",
    prompt="Ein Sonnenuntergang über den Alpen, Ölgemälde-Stil",
    size="1792x1024",
    quality="hd",
    n=1,
)
print(response.data[0].url)
```

## Einschränkungen

- Strenge Content-Filter (keine realen Personen, keine Gewalt)
- Keine Open-Weight-Variante
