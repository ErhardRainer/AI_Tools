# Meta — LLaMA

[Zurück zur Übersicht](README.md)

**Unternehmen:** Meta Platforms (Menlo Park, USA)
**Modell-Downloads:** llama.com / huggingface.co/meta-llama
**Dokumentation:** llama.com/docs
**GitHub:** github.com/meta-llama

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2025-04 | **LLaMA 4 Scout** (17B aktiv, 109B MoE, 10M Kontext) und **LLaMA 4 Maverick** (17B aktiv, 400B MoE) veröffentlicht |
| 2025-04 | **LLaMA 4 Behemoth** (288B aktiv, 16 Experts) in Training — übertrifft GPT-4.5 und Claude Sonnet 3.7 in STEM |
| 2024-12 | **LLaMA 3.3 70B** — Performance auf 405B-Niveau bei 70B Parametern |
| 2024-07 | **LLaMA 3.1** mit 8B, 70B und 405B Varianten |
| 2024-04 | **LLaMA 3** veröffentlicht (8B und 70B) |
| 2023-07 | **LLaMA 2** unter offener Lizenz veröffentlicht |
| 2023-02 | **LLaMA 1** veröffentlicht |

---

## Aktuelle Modelle (März 2026)

### LLaMA 4 (aktuell)

| Modell | Aktive Parameter | Gesamt (MoE) | Kontext | Lizenz | Besonderheiten |
|---|---|---|---|---|---|
| **LLaMA 4 Maverick** | 17B | 400B (128 Experts) | 1M | Llama 4 Community | Schlägt GPT-4o und Gemini 2.0 Flash, nativ multimodal |
| **LLaMA 4 Scout** | 17B | 109B (16 Experts) | **10M** | Llama 4 Community | 10M-Kontext, passt auf eine H100-GPU |
| **LLaMA 4 Behemoth** | 288B | ~2T (16 Experts) | — | In Training | Stärkstes offenes Modell (in Vorbereitung) |

### LLaMA 3.3 / 3.1 (noch verfügbar)

| Modell | Parameter | Kontext | Lizenz | Besonderheiten |
|---|---|---|---|---|
| `llama-3.3-70b` | 70B | 128k | Llama 3.3 Community | Performance auf 405B-Niveau |
| `llama-3.1-405b` | 405B | 128k | Llama 3.1 Community | Größtes dichtes offenes Modell |
| `llama-3.1-8b` | 8B | 128k | Llama 3.1 Community | Für lokale Ausführung / Edge |

---

## Besonderheiten

- **Nativ multimodal (LLaMA 4):** „Fusion"-Architektur vereint Text- und Vision-Token früh in der Pipeline
- **MoE-Architektur:** LLaMA 4 nutzt Mixture-of-Experts — nur 17B aktive Parameter bei bis zu 400B gesamt
- **10M-Kontext (Scout):** Größtes Kontextfenster unter offenen Modellen
- **Open-Weight:** Alle Modelle frei herunterladbar (Llama Community License)
- **Kein eigener API-Dienst:** Über Groq, Together AI, Fireworks, AWS Bedrock, Azure
- **Lokale Ausführung:** Über Ollama, llama.cpp, vLLM

## Lokale Ausführung

```bash
# LLaMA 4 Scout (passt auf eine H100)
ollama pull llama4-scout

# LLaMA 3.3 (weiterhin beliebt für lokale Nutzung)
ollama pull llama3.3:70b
ollama run llama3.3:70b "Erkläre Quantencomputing in drei Sätzen."
```

## Über Groq (schnellste Inferenz)

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
