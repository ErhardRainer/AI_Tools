# n8n Custom Nodes — Media API

Zwei n8n Custom Nodes, die den **llm-api FastAPI-Service** als Backend nutzen:

| Node | Icon | Beschreibung |
|---|---|---|
| **LLM Client** | 💬 | Text-Prompt → LLM-Antwort (OpenAI, Claude, Gemini, Grok, …) |
| **Image Generator** | 🖼️ | Text-Prompt → Bild(er) (DALL-E, Imagen, FLUX, Ideogram, …) |

Die Nodes rufen ausschließlich den lokalen `llm-api`-Service auf — alle Provider-Logik bleibt in Python.

---

## Architektur

```
n8n Workflow
    │
    ▼
[LLM Client] oder [Image Generator]  ← n8n Custom Node (TypeScript)
    │
    ▼  POST /chat  oder  POST /image
[llm-api FastAPI Service]             ← Python, Port 8000
    │
    ▼
[Provider]  OpenAI / Claude / Gemini / Stability / Ideogram / …
```

---

## Voraussetzungen

### 1. Media API starten

```bash
# Im Repo-Root
pip install ".[all]" fastapi uvicorn
cd llm-api
uvicorn api:app --reload
# Läuft auf http://localhost:8000
# Swagger-Doku: http://localhost:8000/docs
```

### 2. n8n starten (Docker empfohlen)

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  -v $(pwd)/n8n:/home/node/.n8n/custom \
  docker.n8n.io/n8nio/n8n
```

Oder lokal:
```bash
npm install -g n8n
n8n start
```

---

## Installation der Custom Nodes

### Option A: Direkt in n8n Custom-Nodes-Ordner

```bash
# n8n Custom-Nodes-Verzeichnis (Standard: ~/.n8n/custom/)
cd ~/.n8n/custom
npm install /pfad/zum/repo/n8n
```

### Option B: Als npm-Paket verlinken (Entwicklung)

```bash
cd /pfad/zum/repo/n8n
npm run build          # TypeScript kompilieren
npm link               # Paket global verlinken

# Im n8n-Verzeichnis
cd ~/.n8n/custom
npm link @openai-tools/n8n-nodes-media-api
```

### Option C: Manuell in n8n-Einstellungen

In der n8n-Oberfläche: **Settings → Community Nodes → Install** → Pfad zum Paket angeben.

---

## Build

```bash
cd n8n
npm install
npm run build    # TypeScript → dist/
npm run dev      # Watch-Mode für Entwicklung
```

---

## Nodes

### LLM Client

Sendet System-, Kontext- und Aufgaben-Prompt an einen LLM-Provider.

**Parameter:**

| Feld | Typ | Beschreibung |
|---|---|---|
| Provider | Dropdown | openai, claude, gemini, grok, kimi, deepseek, groq, mistral |
| Preset | String | Optionaler Preset-Alias aus LLM_Client/config.json |
| Modell | String | Modell überschreiben (leer = Provider-Standard) |
| System-Prompt | Text | Rollenanweisung / Systemnachricht |
| Kontext | Text | Optionaler Hintergrundtext (URLs werden automatisch abgerufen) |
| Aufgabe / Nachricht | Text | Die eigentliche Frage oder Aufgabe |
| Ausgabeformat | Dropdown | plain (Text) oder json (extrahierter JSON-Block) |

**Ausgabe (JSON-Objekt):**

```json
{
  "provider": "openai",
  "model": "gpt-4o",
  "response": "Die Antwort des Modells...",
  "_raw": { ... }
}
```

### Image Generator

Generiert Bilder aus einem Text-Prompt.

**Parameter:**

| Feld | Typ | Beschreibung |
|---|---|---|
| Provider | Dropdown | openai, google, stability, fal, ideogram, leonardo, firefly, auto1111, ollamadiffuser |
| Preset | String | Optionaler Preset-Alias aus ImageGen/config.json |
| Modell | String | Modell überschreiben |
| Prompt | Text | Bild-Beschreibung |
| Anzahl Bilder | Zahl | 1–10 |
| Seitenverhältnis | Dropdown | 1:1, 16:9, 9:16, 4:3, 3:4, 21:9 |
| Bildgröße (WxH) | Dropdown | 1024x1024, 1792x1024, … (für DALL-E/Firefly/A1111) |
| Qualität | Dropdown | standard / hd (nur DALL-E 3) |
| Bild-Ausgabe | Dropdown | URL und Base64 / Nur URL / Nur Base64 |

**Ausgabe (JSON-Objekt):**

```json
{
  "provider": "fal",
  "model": "fal-ai/flux/dev",
  "revised_prompt": null,
  "images": [{ "url": "https://...", "b64_json": null }],
  "image_count": 1,
  "first_url": "https://...",
  "first_b64": null
}
```

---

## Credentials: Media API

In n8n unter **Credentials → New → Media API (llm-api Service)**:

| Feld | Wert | Beschreibung |
|---|---|---|
| Base URL | `http://localhost:8000` | URL des laufenden llm-api Services |
| API Key | _(leer)_ | Optional — nur wenn Service mit `API_KEY` Env-Var gestartet |

---

## Beispiel-Workflows

### Text → LLM → Weiterverarbeitung

```
[Manual Trigger]
  → [LLM Client]
      Provider: claude
      System: "Du bist ein JSON-Generator."
      Task: "Liste 5 Hauptstädte als JSON-Array."
      Ausgabeformat: json
  → [Code Node] (JSON parsen)
  → [HTTP Request] (weiter senden)
```

### Prompt → Bild → S3-Upload

```
[Webhook]  (empfängt "prompt")
  → [Image Generator]
      Provider: fal
      Preset: flux
      Prompt: {{$json.prompt}}
      Bild-Ausgabe: Nur URL
  → [HTTP Request]  (S3-Upload mit first_url)
```

### Dokument zusammenfassen

```
[HTTP Request]  (lädt PDF-URL)
  → [LLM Client]
      Provider: openai
      Context: {{$json.body}}   ← oder direkt URL als Context (wird automatisch abgerufen)
      Task: "Fasse dieses Dokument in 5 Stichpunkten zusammen."
  → [Slack]  (sendet response)
```

---

## Tests

```bash
cd n8n
node tests/test_nodes.js
```

25 Tests — prüfen Node-Metadaten, Property-Struktur und Credentials ohne echte API-Calls.

---

## Dateistruktur

```
n8n/
├── package.json                   # npm-Paket-Definition mit n8n-Metadata
├── tsconfig.json                  # TypeScript-Konfiguration
├── README.md
├── credentials/
│   └── MediaApiCredentials.ts     # Credential-Typ: baseUrl + apiKey
├── nodes/
│   ├── LlmClient/
│   │   ├── LlmClient.node.ts      # LLM Client Node
│   │   └── llm-client.svg         # Icon
│   └── ImageGen/
│       ├── ImageGen.node.ts       # Image Generator Node
│       └── image-gen.svg          # Icon
├── dist/                          # Kompilierter Output (nach npm run build)
└── tests/
    └── test_nodes.js              # Node-Struktur-Tests (kein API-Call)
```
