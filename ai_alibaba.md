# Alibaba — Qwen

[Zurück zur Übersicht](README.md)

**Unternehmen:** Alibaba Cloud (Hangzhou, China)
**Modell-Downloads:** Hugging Face (`Qwen/*`) / ModelScope
**API-Konsole:** dashscope.aliyun.com / Alibaba Cloud Model Studio
**Dokumentation:** qwen.readthedocs.io
**GitHub:** github.com/QwenLM

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2026-03-02 | **Qwen 3.5 Small Series** (0.8B–9B) veröffentlicht — nativ multimodal für Edge |
| 2026-02-24 | **Qwen 3.5-122B-A10B**, **Qwen 3.5-35B-A3B**, **Qwen 3.5-27B** veröffentlicht |
| 2026-02-16 | **Qwen 3.5-397B-A17B** MoE Flaggschiff veröffentlicht — 201 Sprachen |
| 2025-09 | **Qwen 2.5** Serie (0.5B bis 72B) veröffentlicht |
| 2025-06 | **Qwen 3** mit Hybrid-Reasoning veröffentlicht |
| 2024-12 | **Qwen 2.5 Coder 32B** — schlägt GPT-4o in Code-Benchmarks |
| 2024-09 | QwQ-32B Reasoning-Modell |
| 2024-06 | Qwen 2 veröffentlicht |

---

## Aktuelle Modelle (März 2026)

### Qwen 3.5 (neueste Generation)

| Modell | Parameter | Architektur | Kontext | Lizenz | Besonderheiten |
|---|---|---|---|---|---|
| `qwen3.5-397b-a17b` | 397B (17B aktiv) | MoE | 128k | Apache 2.0 | Flaggschiff, 201 Sprachen, nativ multimodal |
| `qwen3.5-122b-a10b` | 122B (10B aktiv) | MoE | 128k | Apache 2.0 | Großes MoE-Modell |
| `qwen3.5-35b-a3b` | 35B (3B aktiv) | MoE | 128k | Apache 2.0 | Kompaktes MoE |
| `qwen3.5-27b` | 27B | Dense | 128k | Apache 2.0 | Stärkstes dichtes Modell |
| `qwen3.5-9b` | 9B | Dense | 128k | Apache 2.0 | Für lokale Nutzung |
| `qwen3.5-4b` | 4B | Dense | 128k | Apache 2.0 | Edge/Laptop |
| `qwen3.5-2b` | 2B | Dense | 128k | Apache 2.0 | Mobilgeräte |
| `qwen3.5-0.8b` | 0.8B | Dense | 128k | Apache 2.0 | IoT/Embedded |

### API-Modelle (Alibaba Cloud)

| Modell | Besonderheiten |
|---|---|
| `qwen-3.5-plus` | Hosted-Variante über Model Studio |
| `qwen-max` | Stärkstes API-Modell |
| `qwen-turbo` | Schnell und günstig |

---

## Besonderheiten

- **201 Sprachen:** Qwen 3.5 unterstützt 201 Sprachen und Dialekte (zuvor 82)
- **Nativ multimodal:** Text, Bild und Video in einem Modell (Qwen 3.5 Small Serie)
- **Apache 2.0 Lizenz:** Vollständig offen, kommerziell nutzbar
- **Von 0.8B bis 397B:** Für jeden Einsatz die passende Größe
- **Über Drittanbieter:** Groq, Together AI, Fireworks, Ollama

## Lokale Ausführung

```bash
ollama pull qwen3.5:27b
ollama run qwen3.5:27b "Erkläre Quantencomputing in drei Sätzen."
```
