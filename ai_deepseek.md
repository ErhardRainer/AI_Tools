# DeepSeek

[Zurück zur Übersicht](README.md)

**Unternehmen:** DeepSeek (Hangzhou, China)
**Gegründet:** 2023 (Tochter von High-Flyer Capital)
**API-Konsole:** platform.deepseek.com
**Preisübersicht:** api-docs.deepseek.com/quick_start/pricing
**Dokumentation:** api-docs.deepseek.com
**API-Basis-URL:** `https://api.deepseek.com` (OpenAI-kompatibel)

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2026-04 (geplant) | **DeepSeek V4** erwartet — nativ multimodal, 1M+ Kontext, Bild/Video/Text |
| 2026-03 | DeepSeek V4 Veröffentlichung bestätigt, ursprünglich für März geplant, auf April verschoben |
| 2025-08-21 | **DeepSeek V3.1** veröffentlicht — Hybrid-Reasoning (Thinking + Non-Thinking Modus), MIT-Lizenz |
| 2025-06 | **DeepSeek V3.2** als API-Modell (`deepseek-chat`) — 128k Kontext |
| 2025-01-20 | **DeepSeek R1** als Open-Weight veröffentlicht — Chain-of-Thought sichtbar, geht viral |
| 2025-01 | **DeepSeek V3** (671B MoE) veröffentlicht — konkurriert mit GPT-4o zu Bruchteilen der Kosten |
| 2024-11 | DeepSeek-V2.5 mit verbessertem Chat und Coding |
| 2024-05 | **DeepSeek-V2** (MoE, 236B Parameter) veröffentlicht |

---

## Aktuelle Modelle (März 2026)

| Modell-ID | Echtes Modell | Kontext | Input-Preis | Output-Preis | Besonderheiten |
|---|---|---|---|---|---|
| `deepseek-chat` | DeepSeek V3.2 | 128k | ~$0.15/1M | ~$0.75/1M | Standard-Chat-Modell, extrem günstig |
| `deepseek-reasoner` | DeepSeek V3.2 | 128k | ~$0.55/1M | ~$2.19/1M | Reasoning mit sichtbarem Denkprozess |

### Open-Weight (lokal)

| Modell | Parameter | Kontext | Lizenz | Besonderheiten |
|---|---|---|---|---|
| DeepSeek V3.1 | 671B MoE (37B aktiv) | 128k | MIT | Hybrid Thinking/Non-Thinking, FP8-Inferenz |
| DeepSeek R1 | 671B MoE (37B aktiv) | 128k | MIT | Chain-of-Thought sichtbar |
| DeepSeek R1 Distill (LLaMA 70B) | 70B | 128k | MIT | Destilliertes R1 auf LLaMA-Basis |

### In Vorbereitung

| Modell | Status | Besonderheiten |
|---|---|---|
| **DeepSeek V4** | April 2026 erwartet | Nativ multimodal (Bild, Video, Text), 1M+ Kontext, 1T+ Parameter |
| **DeepSeek R2** | Verzögert | Reasoning-Nachfolger, noch nicht zufriedenstellend für Gründer |

---

## API-Besonderheiten

- **Extrem günstig:** Einer der günstigsten API-Anbieter am Markt
- **OpenAI-kompatible API:** Drop-in-Ersatz
- **Open-Weight (MIT):** Alle Modelle unter MIT-Lizenz frei verfügbar
- **Hybrid-Reasoning (V3.1):** Wechselt automatisch zwischen Denk- und Schnell-Modus
- **MoE-Architektur:** 671B Parameter gesamt, nur ~37B aktiv pro Anfrage
- **FIM (Fill-in-the-Middle):** Code-Vervollständigung
- **Prefix Caching:** Wiederkehrende Kontexte automatisch gecacht

## Typischer API-Aufruf

```python
from openai import OpenAI

client = OpenAI(api_key="sk-...", base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
        {"role": "user", "content": "Erkläre Quantencomputing in drei Sätzen."}
    ]
)
print(response.choices[0].message.content)
```

---

## Hinweis

DeepSeek-Server stehen in China. Für datensensible Anwendungen kann das Modell lokal betrieben werden (Open-Weight unter MIT-Lizenz). DeepSeek V4 (April 2026) wird das erste nativ multimodale DeepSeek-Modell.
