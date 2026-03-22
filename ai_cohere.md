# Cohere

[Zurück zur Übersicht](README.md)

**Unternehmen:** Cohere (Toronto, Kanada)
**Gegründet:** 2019
**API-Konsole:** dashboard.cohere.com
**Preisübersicht:** cohere.com/pricing
**Dokumentation:** docs.cohere.com

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2025-10 | **Command A Vision** veröffentlicht — erstes multimodales Command-Modell |
| 2025-08 | **Command A Reasoning** (111B) veröffentlicht — Hybrid-Reasoning, 256k Kontext, 23 Sprachen |
| 2025-03 | **Command A** veröffentlicht — 150% Durchsatz des Vorgängers auf nur 2 GPUs |
| 2024-08 | Command R+ 08-2024 mit besserem Tool-Use |
| 2024-04 | **Command R+** — Enterprise-fokussiertes LLM |
| 2024-03 | **Command R** mit 128k Kontext |

---

## Aktuelle Modelle (März 2026)

### Command-Familie

| Modell | Typ | Kontext | Besonderheiten |
|---|---|---|---|
| `command-a` | Flaggschiff | 256k | 150% Throughput, nur 2 GPUs, empfohlen für die meisten Anwendungen |
| `command-a-reasoning` | Reasoning | 256k | 111B Parameter, Hybrid-Reasoning, 23 Sprachen |
| `command-a-vision` | Multimodal | 256k | Text + Bild Verständnis |
| `command-a-translate` | Übersetzung | 256k | Spezialisiert auf Übersetzungsaufgaben |
| `command-r+` | RAG-optimiert | 128k | Für komplexe RAG und Multi-Step Tool-Use |
| `command-r` | Standard | 128k | Schneller, günstiger |
| `command-r7b` | Kompakt | 128k | Kleine, schnelle Variante |

### Spezialisierte Modelle

| Modell | Typ | Beschreibung |
|---|---|---|
| `embed-v4` | Embedding | Multilinguale Texteinbettungen, SOTA-Qualität |
| `rerank-v3.5` | Reranking | Ergebnisse nach Relevanz neu sortieren |

---

## Besonderheiten

- **Command A:** Neue Hauptlinie, ersetzt Command R+ für die meisten Anwendungen
- **RAG-optimiert:** Retrieval Augmented Generation ist Kernkompetenz
- **Embed + Rerank:** Eigene Embedding- und Reranking-Modelle
- **Enterprise-Fokus:** Deployment on-premise, eigene Cloud oder Cohere API
- **Grounded Generation:** Antworten mit Quellenangaben
- **Tool Use:** Natives Function Calling

## Typischer API-Aufruf

```python
import cohere

co = cohere.ClientV2(api_key="...")

response = co.chat(
    model="command-a",
    messages=[
        {"role": "user", "content": "Erkläre Quantencomputing in drei Sätzen."}
    ]
)
print(response.message.content[0].text)
```
