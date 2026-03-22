<<<<<<< HEAD
# AI Tools

Werkzeugsammlung rund um Künstliche Intelligenz — Large Language Models (LLMs), Bildgenerierung, Videogenerierung, programmatischer Zugriff und KI-Agenten.

---

## Inhaltsverzeichnis

1. [Übersicht der LLMs (Large Language Models)](#1--übersicht-der-llms)
2. [Übersicht der bildgenerierenden Modelle](#2--übersicht-der-bildgenerierenden-modelle)
3. [Übersicht der videogenerierenden Modelle](#3--übersicht-der-videogenerierenden-modelle)
4. [Programmierung](#4--programmierung)
5. [KI-Agenten](#5--ki-agenten)

---

## 1 — Übersicht der LLMs

### Große kommerzielle Modelle

| Anbieter | Flaggschiff-Modell | Kontext | API | Besonderheiten | Details |
|---|---|---|---|---|---|
| **OpenAI** | GPT-5.4 Thinking, GPT-5.3 Instant | 200k | ✅ | Marktführer, GPT-5-Familie mit Thinking/Instant/Pro-Varianten | [ai_openai.md](ai_openai.md) |
| **Anthropic** | Claude Opus 4.6, Sonnet 4.6, Haiku 4.5 | 1M | ✅ | 1M-Kontext (Opus/Sonnet), Constitutional AI, Extended Thinking | [ai_claude.md](ai_claude.md) |
| **Google** | Gemini 3.1 Pro, 3.1 Flash | 2M | ✅ | Riesiges Kontextfenster, multimodal, Gemini 3-Familie | [ai_google.md](ai_google.md) |
| **xAI** | Grok 4.20, Grok 4.1 Fast | 2M | ✅ | Echtzeit-Webzugriff, Multi-Agent, X/Twitter-Integration | [ai_xai.md](ai_xai.md) |
| **Mistral AI** | Mistral Small 4, Mistral Large 3, Devstral 2 | 128k–256k | ✅ | EU-basiert, Open-Weight Apache 2.0, Magistral Reasoning | [ai_mistral.md](ai_mistral.md) |
| **Cohere** | Command A, Command A Reasoning/Vision | 256k | ✅ | RAG-optimiert, Enterprise-Fokus, Embed/Rerank | [ai_cohere.md](ai_cohere.md) |

### Chinesische Anbieter

| Anbieter | Flaggschiff-Modell | Kontext | API | Besonderheiten | Details |
|---|---|---|---|---|---|
| **DeepSeek** | DeepSeek V3.2 (Chat), V3.1 (Reasoning) | 128k | ✅ | Extrem günstig, Open-Weight MIT, V4 in Vorbereitung (Apr 2026) | [ai_deepseek.md](ai_deepseek.md) |
| **Moonshot AI** | Kimi K2.5 | 128k | ✅ | MoE 1T Parameter, multimodal, Agent Swarm (100 parallele Agenten) | [ai_moonshot.md](ai_moonshot.md) |
| **Alibaba** | Qwen 3.5 (0.8B–397B MoE) | 128k | ✅ | 201 Sprachen, nativ multimodal, Apache 2.0 | [ai_alibaba.md](ai_alibaba.md) |
| **Zhipu AI** | GLM-4-Plus | 128k | ✅ | ChatGLM-Nachfolger, Vision-fähig | [ai_zhipu.md](ai_zhipu.md) |

### Schnelle Inferenz-Plattformen

| Plattform | Verfügbare Modelle | Besonderheit | Details |
|---|---|---|---|
| **Groq** | GPT-OSS 120B, LLaMA 3.3, Kimi K2, Qwen3 | Hardware-beschleunigte Inferenz (LPU), extrem schnell | [ai_groq.md](ai_groq.md) |
| **Together AI** | LLaMA 4, Qwen 3.5, DeepSeek R1 u. v. m. | Serverless Inferenz für 200+ Open-Source-Modelle | [ai_together.md](ai_together.md) |
| **Fireworks AI** | LLaMA 4, Qwen 3.5, DeepSeek R1 u. v. m. | Optimierte Inferenz, FireFunction für Tool-Use | [ai_fireworks.md](ai_fireworks.md) |

### Open-Weight-Modelle (lokal ausführbar)

| Modell | Entwickler | Parameter | Lizenz | Besonderheiten | Details |
|---|---|---|---|---|---|
| **LLaMA 4 Maverick** | Meta | 400B MoE (17B aktiv) | Llama 4 Community | Nativ multimodal, schlägt GPT-4o und Gemini 2.0 Flash | [ai_meta.md](ai_meta.md) |
| **LLaMA 4 Scout** | Meta | 109B MoE (17B aktiv) | Llama 4 Community | 10M-Kontext, passt auf eine H100-GPU | [ai_meta.md](ai_meta.md) |
| **Qwen 3.5** | Alibaba | 0.8B–397B MoE | Apache 2.0 | 201 Sprachen, nativ multimodal | [ai_alibaba.md](ai_alibaba.md) |
| **Mistral Small 4** | Mistral | 119B MoE (6B aktiv) | Apache 2.0 | Reasoning + Vision + Code in einem Modell | [ai_mistral.md](ai_mistral.md) |
| **Phi-4-reasoning** | Microsoft | 14B–15B | MIT | Reasoning-Vision, wählt automatisch Thinking-Modus | [ai_microsoft.md](ai_microsoft.md) |
| **DeepSeek V3.1** | DeepSeek | 671B MoE (37B aktiv) | MIT | Hybrid Thinking/Non-Thinking, extrem günstig | [ai_deepseek.md](ai_deepseek.md) |

### Lokale Ausführung

| Tool | Beschreibung |
|---|---|
| **Ollama** | CLI-Tool zum lokalen Ausführen von LLMs — einfachste Methode |
| **LM Studio** | Desktop-App mit GUI für lokale Modelle, GGUF-Support |
| **llama.cpp** | C/C++-Inferenz-Engine, Basis vieler lokaler Tools |
| **vLLM** | Hochperformante Inferenz-Engine für Produktion |
| **LocalAI** | OpenAI-kompatible lokale API für beliebige Modelle |

---

## 2 — Übersicht der bildgenerierenden Modelle

| Modell | Anbieter | API | Besonderheiten | Details |
|---|---|---|---|---|
| **GPT Image 1.5** | OpenAI | ✅ | Nativ in GPT-5 integriert, ersetzt DALL-E 3, #1 auf LM Arena | [ai_image_dalle.md](ai_image_dalle.md) |
| **Midjourney V7** | Midjourney Inc. | ✅ | Höchste ästhetische Qualität, Personalisierung, Web+Discord | [ai_image_midjourney.md](ai_image_midjourney.md) |
| **FLUX.2** | Black Forest Labs | ✅ | SOTA-Qualität, [max]/[pro]/[klein], Sub-Sekunde möglich | [ai_image_flux.md](ai_image_flux.md) |
| **Stable Diffusion 3.5** | Stability AI | ✅ | Open-Weight, lokal ausführbar, riesige Community | [ai_image_stablediffusion.md](ai_image_stablediffusion.md) |
| **Adobe Firefly 3** | Adobe | ✅ | Kommerziell sicher (nur auf lizenzierten Daten trainiert) | [ai_image_firefly.md](ai_image_firefly.md) |
| **Google Imagen 4** | Google | ✅ | In Gemini integriert, Nano Banana Pro | [ai_image_imagen.md](ai_image_imagen.md) |
| **Ideogram 2.0** | Ideogram | ✅ | Bestes Textrendering in Bildern | [ai_image_ideogram.md](ai_image_ideogram.md) |
| **Leonardo Phoenix** | Leonardo | ✅ | Gaming/Concept-Art-Fokus, Realtime Canvas | [ai_image_leonardo.md](ai_image_leonardo.md) |
| **Recraft V3** | Recraft | ✅ | Vektorgrafiken und Designs, Brand-Konsistenz | [ai_image_recraft.md](ai_image_recraft.md) |

---

## 3 — Übersicht der videogenerierenden Modelle

| Modell | Anbieter | API | Max. Länge | Besonderheiten | Details |
|---|---|---|---|---|---|
| **Sora 2** | OpenAI | ✅ | 20s+ | Kinematische Qualität, synchronisiertes Audio, 4K | [ai_video_sora.md](ai_video_sora.md) |
| **Veo 3.1** | Google DeepMind | ✅ | 2min+ | Nativer Audio-Output, Dialoge, 4K, ab $0.15/s | [ai_video_veo.md](ai_video_veo.md) |
| **Runway Gen-4.5** | Runway | ✅ | 20s+ | #1 Benchmark, Motion Brush, Szenen-Konsistenz | [ai_video_runway.md](ai_video_runway.md) |
| **Kling 3.0** | Kuaishou | ✅ | 3min | Multi-Shot, Multi-Charakter Audio, günstig | [ai_video_kling.md](ai_video_kling.md) |
| **Seedance 2.0** | ByteDance | ✅ | 20s+ | Regisseur-Kontrolle, nativer Audio, Kurzfilm-fähig | [ai_video_seedance.md](ai_video_seedance.md) |
| **Pika 2.0** | Pika Labs | ✅ | 10s | Einfache Bedienung, Pikaffects, Szenen-Erweiterung | [ai_video_pika.md](ai_video_pika.md) |
| **Luma Dream Machine** | Luma AI | ✅ | 5s | Schnelle Generierung, gute Kamerabewegungen | [ai_video_luma.md](ai_video_luma.md) |
| **Minimax (Hailuo)** | MiniMax | ✅ | 2min | Audio-visuell synchron, realistische Gesichter | [ai_video_minimax.md](ai_video_minimax.md) |

---

## 4 — Programmierung

### LLM_Client — Programmatischer Zugriff auf LLMs

Das Paket [LLM_Client/](LLM_Client/) ermöglicht den einheitlichen Zugriff auf **8 LLM-Anbieter** über eine gemeinsame Python-Schnittstelle. Verwendbar als Script, Modul, CLI oder importierbare Bibliothek.

**Unterstützte Anbieter:** OpenAI, Claude, Gemini, Grok, Kimi, DeepSeek, Groq, Mistral

```bash
# Schnellstart
pip install .
llm-client --config LLM_Client/config.json --provider openai
```

Ausführliche Dokumentation: [LLM_Client/README.md](LLM_Client/README.md)

### Assistant_AI — OpenAI Assistants API

Das Notebook [Assistant_AI/Assistant_AI.ipynb](Assistant_AI/Assistant_AI.ipynb) ist eine Referenzimplementierung für die **OpenAI Assistants API** (Beta). Es deckt den gesamten Workflow ab: Datei-Upload, Assistant-Erstellung, Thread-basierte Konversation.

Ausführliche Dokumentation: [Assistant_AI/README.md](Assistant_AI/README.md) *(sofern vorhanden)*

---

## 5 — KI-Agenten

### Was sind KI-Agenten?

KI-Agenten sind autonome Systeme, die auf LLMs basieren und **eigenständig Aufgaben planen, Werkzeuge nutzen und iterativ Probleme lösen** können. Im Gegensatz zu einfachen Chatbots können Agenten:

- **Planen:** Komplexe Aufgaben in Teilschritte zerlegen
- **Werkzeuge nutzen:** APIs aufrufen, Code ausführen, Dateien lesen/schreiben, im Web suchen
- **Iterieren:** Ergebnisse prüfen, Fehler erkennen und Vorgehensweise anpassen
- **Zusammenarbeiten:** Mehrere Agenten arbeiten an verschiedenen Teilproblemen (Multi-Agent-Systeme)

### Übersicht aktueller KI-Agenten

| Agent | Anbieter | Typ | Besonderheiten |
|---|---|---|---|
| **Claude Code** | Anthropic | Coding-Agent (CLI) | 80.9% SWE-bench, ~4% aller GitHub-Commits, Multi-File-Edits, teuerster aber fähigster Agent |
| **Claude Agent SDK** | Anthropic | Agent-Framework | Python SDK zum Bau eigener Agenten mit Claude als Backbone |
| **Codex CLI** | OpenAI | Coding-Agent (CLI) | Open-Source (Rust), 77.3% Terminal-Bench, 240+ Token/s, 1M+ Entwickler im ersten Monat |
| **Gemini CLI** | Google | Coding-Agent (CLI) | Open-Source, Gemini-basiert, Multi-File-Edits |
| **OpenAI Agents SDK** | OpenAI | Agent-Framework | Python SDK, Tracing, Guardrails, Handoffs zwischen Agenten |
| **Cursor / Windsurf** | Cursor Inc. / Codeium | IDE-Agenten | KI-integrierte Code-Editoren mit autonomen Multi-Agent-Fähigkeiten |
| **Devin** | Cognition | Vollautonomer Coding-Agent | Eigene Sandbox-Umgebung (IDE, Browser, Terminal), ab $20/Monat |
| **CrewAI** | CrewAI | Multi-Agent-Framework | Rollenbasierte Agenten-Teams, stärkstes Multi-Agent-Framework |
| **LangGraph** | LangChain | Agent-Graph-Framework | Zustandsbasierte Agent-Workflows als Graphen |
| **Microsoft AutoGen** | Microsoft | Multi-Agent-Framework | Konversationsbasierte Multi-Agent-Systeme |
| **Smolagents** | Hugging Face | Leichtgewichtiges Framework | Minimalistisch, Code-basierte Agenten, Open-Source |
| **OpenClaw** | Community | Agent-Plattform | Modulare Agent-Architektur, erweiterbar |

> Detaillierte Beschreibung der einzelnen Agenten, Architekturvergleiche und Einsatzszenarien: [ai_agents_openclaw.md](ai_agents_openclaw.md) *(kommt in einer zukünftigen Erweiterung)*

---

## Repository-Struktur

```
AI_Tools/
├── README.md                          # Diese Datei
├── CLAUDE.md                          # KI-Assistenten-Konfiguration
├── pyproject.toml                     # Python-Paketdefinition
├── .gitignore
├── LICENSE
│
├── ai_openai.md                       # Detail: OpenAI
├── ai_claude.md                       # Detail: Anthropic Claude
├── ai_google.md                       # Detail: Google Gemini / Gemma
├── ai_xai.md                          # Detail: xAI Grok
├── ai_mistral.md                      # Detail: Mistral AI
├── ai_deepseek.md                     # Detail: DeepSeek
├── ai_moonshot.md                     # Detail: Moonshot AI / Kimi
├── ai_meta.md                         # Detail: Meta LLaMA
├── ai_microsoft.md                    # Detail: Microsoft Phi
├── ai_alibaba.md                      # Detail: Alibaba Qwen
├── ai_cohere.md                       # Detail: Cohere
├── ai_zhipu.md                        # Detail: Zhipu AI / GLM
├── ai_groq.md                         # Detail: Groq
├── ai_together.md                     # Detail: Together AI
├── ai_fireworks.md                    # Detail: Fireworks AI
│
├── ai_image_dalle.md                  # Detail: DALL-E
├── ai_image_midjourney.md             # Detail: Midjourney
├── ai_image_stablediffusion.md        # Detail: Stable Diffusion
├── ai_image_flux.md                   # Detail: Flux
├── ai_image_firefly.md                # Detail: Adobe Firefly
├── ai_image_imagen.md                 # Detail: Google Imagen
├── ai_image_ideogram.md               # Detail: Ideogram
├── ai_image_leonardo.md               # Detail: Leonardo AI
├── ai_image_recraft.md                # Detail: Recraft
│
├── ai_video_sora.md                   # Detail: Sora
├── ai_video_veo.md                    # Detail: Veo
├── ai_video_runway.md                 # Detail: Runway
├── ai_video_kling.md                  # Detail: Kling
├── ai_video_pika.md                   # Detail: Pika
├── ai_video_luma.md                   # Detail: Luma Dream Machine
├── ai_video_minimax.md                # Detail: MiniMax / Hailuo
├── ai_video_seedance.md               # Detail: Seedance (ByteDance)
├── ai_video_svd.md                    # Detail: Stable Video Diffusion
│
├── Assistant_AI/
│   └── Assistant_AI.ipynb             # OpenAI Assistants API Notebook
│
└── LLM_Client/
    ├── llm_client.py                  # Multi-Provider LLM Client
    ├── config.template.json           # Config-Vorlage
    ├── examples/                      # PowerShell-Beispielskripte
    └── unittest/                      # Unit-Tests
```

---

## Lizenz

Siehe [LICENSE](LICENSE).
=======
# OpenAI / Media AI Toolkit

Python-Tools für OpenAI und weitere KI-Provider: Textgenerierung, Bildgenerierung, und mehr.

## Module

| Modul | Beschreibung | Provider |
|---|---|---|
| [`LLM_Client/`](LLM_Client/README.md) | Text → Text | OpenAI, Claude, Gemini, Grok, Kimi, DeepSeek, Groq, Mistral |
| [`ImageGen/`](ImageGen/README.md) | Text → Bild | DALL-E, Google Imagen, Stability AI, fal.ai FLUX |
| [`llm-api/`](llm-api/README.md) | REST-API für alle Module | FastAPI, Docker |
| [`Assistant_AI/`](Assistant_AI/) | OpenAI Assistants API | Notebook-Referenzimplementierung |

## Schnellstart

```bash
# Alles installieren
pip install ".[all]"
pip install openai  # für DALL-E und LLM

# Konfiguration
cp LLM_Client/config.template.json LLM_Client/config.json
cp ImageGen/config.template.json   ImageGen/config.json
# API-Keys eintragen

# Text generieren
llm-client --config LLM_Client/config.json --provider openai

# Bild generieren
image-gen --config ImageGen/config.json --prompt "A sunset over mountains" --output out.png

# REST-API starten
docker compose -f llm-api/docker-compose.yml up --build
```
>>>>>>> origin/claude/add-claude-documentation-h4UFb
