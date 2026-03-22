# Microsoft — Phi

[Zurück zur Übersicht](README.md)

**Unternehmen:** Microsoft Research
**Modell-Downloads:** Hugging Face (`microsoft/phi-*`)
**Dokumentation:** azure.microsoft.com/products/phi
**Verfügbar über:** Azure AI Foundry, Hugging Face, Ollama, GitHub Models

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2026-03-04 | **Phi-4-reasoning-vision-15B** veröffentlicht — multimodal Reasoning, wählt automatisch Thinking-Modus |
| 2026-02 | **Phi-4-reasoning**, **Phi-4-reasoning-plus**, **Phi-4-mini-reasoning** veröffentlicht — RL-basiertes Reasoning |
| 2025-03 | **Phi-4-mini** (3.8B) und **Phi-4-multimodal** veröffentlicht — Audio + Vision + Text |
| 2024-12 | **Phi-4** veröffentlicht — 14B Parameter, übertrifft größere Modelle in Math/Code |
| 2024-04 | **Phi-3** Familie (Mini 3.8B, Small 7B, Medium 14B) |

---

## Aktuelle Modelle (März 2026)

### Reasoning-Modelle (neueste)

| Modell | Parameter | Kontext | Lizenz | Besonderheiten |
|---|---|---|---|---|
| `phi-4-reasoning-vision-15b` | 15B | 128k | MIT | Multimodal Reasoning (Text + Bild), automatischer Thinking-Modus |
| `phi-4-reasoning-plus` | 14B | 16k | MIT | Mehr Inference-Compute (1.5× Token), höchste Genauigkeit |
| `phi-4-reasoning` | 14B | 16k | MIT | Basis-Reasoning, RL-trainiert |
| `phi-4-mini-reasoning` | 3.8B | 128k | MIT | Kompaktes Reasoning für Edge |

### Multimodale Modelle

| Modell | Parameter | Fähigkeiten | Lizenz | Besonderheiten |
|---|---|---|---|---|
| `phi-4-multimodal` | 4.2B | Text + Audio + Vision | MIT | 20+ Sprachen, OCR, Charts, Audio-Verständnis |
| `phi-3.5-vision` | 4.2B | Text + Vision | MIT | Bildanalyse, 128k Kontext |

### Basis-Modelle

| Modell | Parameter | Kontext | Lizenz | Besonderheiten |
|---|---|---|---|---|
| `phi-4` | 14B | 16k | MIT | Stärkstes Phi-Basis, Math/Code-Spezialist |
| `phi-4-mini` | 3.8B | 128k | MIT | 128k Kontext, 200k Vokabular, Function Calling |

---

## Besonderheiten

- **„Small Language Models":** Fokus auf maximale Qualität bei minimaler Größe
- **Automatischer Thinking-Modus:** Phi-4-reasoning-vision entscheidet selbst, wann es „denken" soll
- **MIT-Lizenz:** Vollständig offen, kommerziell nutzbar
- **Multimodal:** Text + Audio + Vision in einem 4.2B-Modell
- **Edge-optimiert:** Für Mobilgeräte, Laptops, IoT
- **ONNX Runtime:** Optimiert für Microsofts Inferenz-Engine

## Lokale Ausführung

```bash
ollama pull phi4
ollama run phi4 "Erkläre Quantencomputing in drei Sätzen."

# Reasoning-Variante
ollama pull phi4-reasoning
```
