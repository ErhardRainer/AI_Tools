# Moonshot AI — Kimi

[Zurück zur Übersicht](README.md)

**Unternehmen:** Moonshot AI (Beijing, China)
**Gegründet:** 2023
**API-Konsole:** platform.moonshot.ai
**Dokumentation:** platform.moonshot.ai/docs
**API-Basis-URL:** `https://api.moonshot.cn/v1` (OpenAI-kompatibel)

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2026-01-27 | **Kimi K2.5** veröffentlicht — multimodal, Agent Swarm (100 parallele Agenten), 50.2% auf HLE |
| 2025-07 | **Kimi K2** veröffentlicht — MoE mit 1T Parametern, 32B aktiv, SOTA in Math/Code |
| 2024-10 | Kimi 1.5 mit verbessertem Reasoning |
| 2024-03 | Moonshot v1-128k — 128k Kontext-Token |

---

## Aktuelle Modelle (März 2026)

| Modell | Typ | Architektur | Kontext | Besonderheiten |
|---|---|---|---|---|
| `kimi-k2.5` | Flaggschiff (multimodal) | 1T MoE (32B aktiv) | 128k | Vision + Text, Agent Swarm, Thinking/Instant Modus |
| `kimi-k2` | Chat/Code | 1T MoE (32B aktiv) | 128k | SOTA in Math/Code unter Non-Thinking-Modellen |
| `moonshot-v1-128k` | Lang-Kontext | — | 128k | Für sehr lange Dokumente |
| `moonshot-v1-32k` | Standard | — | 32k | Ausgewogene Variante |
| `moonshot-v1-8k` | Schnell | — | 8k | Kürzester Kontext, schnellste Antworten |

---

## Besonderheiten

- **Agent Swarm:** Bis zu 100 spezialisierte Agenten arbeiten parallel — 4.5× schneller, 76% günstiger als Claude Opus 4.5
- **Multimodal (K2.5):** Nativ Vision + Text, trainiert auf 15T gemischten Token
- **MoE-Architektur:** 1T Parameter gesamt, nur 32B aktiv pro Anfrage
- **Thinking/Instant:** K2.5 kann zwischen Denkprozess und sofortiger Antwort wechseln
- **OpenAI-kompatible API:** Standard `openai`-Package funktioniert
- **Open-Weight:** K2.5 auf Hugging Face verfügbar

## Typischer API-Aufruf

```python
from openai import OpenAI

client = OpenAI(api_key="sk-...", base_url="https://api.moonshot.cn/v1")

response = client.chat.completions.create(
    model="kimi-k2.5",
    messages=[
        {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
        {"role": "user", "content": "Erkläre Quantencomputing in drei Sätzen."}
    ]
)
print(response.choices[0].message.content)
```
