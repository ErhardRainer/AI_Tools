# Groq

[Zurück zur Übersicht](README.md)

**Unternehmen:** Groq Inc. (Mountain View, USA)
**Gegründet:** 2016
**API-Konsole:** console.groq.com
**Preisübersicht:** groq.com/pricing
**Dokumentation:** console.groq.com/docs
**API-Basis-URL:** `https://api.groq.com/openai/v1` (OpenAI-kompatibel)

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2026-03-16 | **Groq LPU 3** — neuer Inferenz-Chip von NVIDIA, $20 Mrd. Deal, Samsung 4nm |
| 2026-02 | **GPT-OSS 120B** auf Groq verfügbar — Reasoning mit Groq-Geschwindigkeit |
| 2026-01 | **Kimi K2** auf Groq, 256k Kontext |
| 2025-12 | **Groq Compound** — System mit eingebauter Web-Suche und Code-Ausführung |
| 2025-09 | LLaMA 3.1 Modelle auf Groq |
| 2025-04 | Groq API öffentlich verfügbar — „schnellste AI-Inferenz der Welt" |

---

## Verfügbare Modelle (März 2026)

### Reasoning-Modelle

| Modell | Entwickler | Parameter | Kontext | Besonderheiten |
|---|---|---|---|---|
| `gpt-oss-120b` | OpenAI (Open) | 120B | 128k | Reasoning mit Groq-Geschwindigkeit |
| `gpt-oss-safeguard-20b` | OpenAI (Open) | 20B | 128k | Trust & Safety Reasoning |
| `qwen-qwq-32b` | Alibaba | 32B | 128k | Reasoning/Chain-of-Thought |
| `deepseek-r1-distill-llama-70b` | DeepSeek | 70B | 128k | R1-Destillat auf LLaMA-Basis |

### Chat-Modelle

| Modell | Entwickler | Parameter | Kontext | Besonderheiten |
|---|---|---|---|---|
| `llama-3.3-70b-versatile` | Meta | 70B | 128k | Stärkstes LLaMA auf Groq, Tool-Use |
| `kimi-k2-0905` | Moonshot | 32B aktiv | 256k | Neuestes Kimi, agentic Coding |
| `llama-3.1-8b-instant` | Meta | 8B | 128k | Extrem schnell (~1200 tok/s) |
| `gemma2-9b-it` | Google | 9B | 8k | Gute Qualität bei kleiner Größe |
| `mixtral-8x7b-32768` | Mistral | 46B (MoE) | 32k | MoE-Architektur |

### Groq Compound

Groq Compound nutzt offen verfügbare Modelle mit eingebauter **Web-Suche** und **Code-Ausführung** — das Modell entscheidet intelligent, wann welches Tool genutzt wird.

---

## Besonderheiten

- **LPU (Language Processing Unit):** Eigene Hardware — keine GPUs, SRAM-basiert
- **Extrem schnell:** 10-20× schneller als GPU-basierte Anbieter
- **Groq LPU 3:** Neuer Chip (2026, NVIDIA-Partnerschaft, Samsung 4nm)
- **OpenAI-kompatible API:** Standard `openai`-Package funktioniert
- **Kein eigenes Modell:** Groq hostet Open-Source-Modelle auf eigener Hardware
- **Kostenlose Stufe:** Großzügiges Free Tier mit Rate Limits

## Typischer API-Aufruf

```python
from openai import OpenAI

client = OpenAI(api_key="gsk_...", base_url="https://api.groq.com/openai/v1")

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
        {"role": "user", "content": "Erkläre Quantencomputing in drei Sätzen."}
    ]
)
print(response.choices[0].message.content)
```
