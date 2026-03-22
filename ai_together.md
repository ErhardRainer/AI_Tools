# Together AI

[Zurück zur Übersicht](README.md)

**Unternehmen:** Together AI (San Francisco, USA)
**Gegründet:** 2022
**API-Konsole:** api.together.xyz
**Preisübersicht:** together.ai/pricing
**Dokumentation:** docs.together.ai
**API-Basis-URL:** `https://api.together.xyz/v1` (OpenAI-kompatibel)

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2026-02 | LLaMA 4 Maverick und Scout, Qwen 3.5, DeepSeek R1 auf Together verfügbar |
| 2025-12 | 200+ Modelle über Serverless Endpoints |
| 2025-06 | Together Inference Engine 2.0 |

---

## Verfügbare Modelle (Auswahl)

| Modell | Entwickler | Parameter | Kontext | Besonderheiten |
|---|---|---|---|---|
| LLaMA 4 Maverick | Meta | 400B MoE (17B aktiv) | 1M | Nativ multimodal |
| LLaMA 4 Scout | Meta | 109B MoE (17B aktiv) | 10M | Größter Kontext |
| Qwen 3.5-397B-A17B | Alibaba | 397B MoE | 128k | 201 Sprachen |
| DeepSeek R1 | DeepSeek | 671B MoE | 128k | Reasoning |
| LLaMA 3.3-70B | Meta | 70B | 128k | Bewährt, schnell |
| Mixtral 8x22B | Mistral | 141B MoE | 64k | MoE-Architektur |

200+ Open-Source-Modelle über eine API verfügbar.

---

## Besonderheiten

- **Größte Modellauswahl:** 200+ Open-Source-Modelle
- **OpenAI-kompatible API:** Standard `openai`-Package funktioniert
- **Serverless + Dedicated:** Flexibilität oder garantierter Throughput
- **Fine-Tuning:** Eigene Modelle trainieren
- **Custom Model Deployment:** Eigene Modelle hochladen und hosten

## Typischer API-Aufruf

```python
from openai import OpenAI

client = OpenAI(api_key="...", base_url="https://api.together.xyz/v1")

response = client.chat.completions.create(
    model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
    messages=[
        {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
        {"role": "user", "content": "Erkläre Quantencomputing in drei Sätzen."}
    ]
)
print(response.choices[0].message.content)
```
