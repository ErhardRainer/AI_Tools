# Fireworks AI

[Zurück zur Übersicht](README.md)

**Unternehmen:** Fireworks AI (San Francisco, USA)
**Gegründet:** 2022
**API-Konsole:** fireworks.ai
**Preisübersicht:** fireworks.ai/pricing
**Dokumentation:** docs.fireworks.ai
**API-Basis-URL:** `https://api.fireworks.ai/inference/v1` (OpenAI-kompatibel)

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2026-02 | LLaMA 4, Qwen 3.5, DeepSeek R1 auf Fireworks verfügbar |
| 2025-10 | **FireFunction V2** — eigenes Function-Calling-Modell |
| 2025-06 | Fireworks Compound AI — Multi-Modell-Workflows |

---

## Verfügbare Modelle (Auswahl)

| Modell | Entwickler | Parameter | Besonderheiten |
|---|---|---|---|
| LLaMA 4 Maverick | Meta | 400B MoE | Nativ multimodal |
| LLaMA 4 Scout | Meta | 109B MoE | 10M Kontext |
| Qwen 3.5 | Alibaba | Verschiedene | 201 Sprachen |
| DeepSeek R1 | DeepSeek | 671B MoE | Reasoning |
| FireFunction V2 | Fireworks | 70B | Optimiert für Function Calling |

---

## Besonderheiten

- **Optimierte Inferenz:** Eigene Infrastruktur für schnelle, günstige Inferenz
- **OpenAI-kompatible API:** Standard `openai`-Package funktioniert
- **FireFunction:** Spezialisiertes Tool-Use-Modell
- **Structured Output:** JSON-Schema-konforme Ausgaben
- **Custom Model Deployment:** Eigene Fine-tuned Modelle hosten

## Typischer API-Aufruf

```python
from openai import OpenAI

client = OpenAI(api_key="...", base_url="https://api.fireworks.ai/inference/v1")

response = client.chat.completions.create(
    model="accounts/fireworks/models/llama-v4-maverick",
    messages=[
        {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
        {"role": "user", "content": "Erkläre Quantencomputing in drei Sätzen."}
    ]
)
print(response.choices[0].message.content)
```
