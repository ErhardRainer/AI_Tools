# LLM API

FastAPI-Wrapper für den LLM Client. Stellt alle konfigurierten LLM-Provider als REST-API bereit — lokal oder in einem Docker-Container.

---

## Schnellstart

### Lokal (ohne Docker)

```bash
# Abhängigkeiten installieren (im Repo-Root)
pip install ".[all]"
pip install -r llm-api/requirements.txt

# API starten (im llm-api/-Verzeichnis)
cd llm-api
uvicorn api:app --reload
```

### Docker Compose (empfohlen)

```bash
# config.json muss vorhanden sein
cp LLM_Client/config.template.json LLM_Client/config.json
# API-Keys in config.json eintragen

# Container bauen und starten
docker compose -f llm-api/docker-compose.yml up --build

# Im Hintergrund
docker compose -f llm-api/docker-compose.yml up -d --build
```

### Docker (manuell)

```bash
# Build-Kontext ist der Repo-Root
docker build -f llm-api/Dockerfile -t llm-api .

docker run \
  -v $(pwd)/LLM_Client/config.json:/app/LLM_Client/config.json:ro \
  -p 8000:8000 \
  llm-api
```

---

## Endpunkte

| Methode | Pfad | Beschreibung |
|---|---|---|
| `GET` | `/health` | Liveness-Check |
| `GET` | `/providers` | Verfügbare Provider und Presets |
| `POST` | `/chat` | Prompt an LLM senden |
| `GET` | `/docs` | Interaktive Swagger-UI |
| `GET` | `/redoc` | ReDoc-Dokumentation |

---

## POST /chat

### Request

```json
{
  "provider":      "openai",
  "preset":        null,
  "model":         null,
  "system":        "Du bist ein hilfreicher Assistent.",
  "context":       "",
  "task":          "Erkläre Quantencomputing in zwei Sätzen.",
  "output_format": "plain"
}
```

| Feld | Typ | Pflicht | Beschreibung |
|---|---|---|---|
| `provider` | string | nein | Provider-Name (überschreibt default_provider) |
| `preset` | string | nein | Preset-Alias aus config.json |
| `model` | string | nein | Modell überschreiben |
| `system` | string | **ja** | System-Prompt / Rollenanweisung |
| `context` | string | nein | Hintergrundtext (Dokument, E-Mail, Code …) |
| `task` | string | **ja** | Die Aufgabe oder Frage |
| `output_format` | string | nein | `plain` (Standard) oder `json` |

**Provider-Auflösung (Priorität):**
1. `provider` (explizit)
2. `preset` → löst Provider + Modell auf
3. `default_provider` aus config.json

### Response

```json
{
  "provider": "openai",
  "model":    "gpt-4o",
  "response": "Quantencomputing nutzt quantenmechanische Phänomene …"
}
```

### Ausgabeformat `json`

Wenn das Modell explizit JSON liefern soll, entfernt `output_format=json` allen umgebenden Text (Erklärungen, Markdown-Wrapper) und gibt nur den JSON-Block zurück. Wird kein gültiges JSON gefunden, antwortet die API mit HTTP 422.

### Automatischer URL-Abruf im context-Feld

Enthält `context` eine oder mehrere HTTP(S)-URLs, werden diese **automatisch abgerufen** und durch den Dokumentinhalt ersetzt:

| Format | Erkennung | Verarbeitung |
|---|---|---|
| PDF | `.pdf` / `application/pdf` | Textextraktion via `pypdf` |
| HTML | `.html`/`.htm` / `text/html` | Lesbartext via `beautifulsoup4` |
| Text | alles andere | Rohtext |

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "system":   "Du bist ein Experte für Textzusammenfassungen.",
    "context":  "https://example.com/bericht.pdf",
    "task":     "Fasse den Inhalt in 5 Stichpunkten zusammen."
  }'
```

Für den URL-Abruf müssen im Container `requests`, `pypdf` und `beautifulsoup4` installiert sein — ist in `pip install ".[all]"` enthalten.

---

## Beispiele (curl)

```bash
# Health-Check
curl http://localhost:8000/health

# Provider anzeigen
curl http://localhost:8000/providers

# Einfacher Chat (Standard-Provider)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"system": "Du bist ein Assistent.", "task": "Was ist 2+2?"}'

# Provider explizit wählen
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"provider": "grok", "system": "Du bist ein Experte.", "task": "Erkläre REST-APIs."}'

# Preset verwenden
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"preset": "fast", "system": "S", "task": "Sag Hallo."}'

# JSON-Modus
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "system": "Antworte ausschließlich mit validem JSON.",
    "task": "Gib {name, sprache, version} für Python zurück.",
    "output_format": "json"
  }'

# Mit API-Key-Authentifizierung
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dein-geheimer-schluessel" \
  -d '{"system": "S", "task": "T"}'
```

---

## Authentifizierung

Optional — wird aktiviert indem die Umgebungsvariable `API_KEY` gesetzt wird:

```bash
# docker-compose: in docker-compose.yml oder als Shell-Variable
export API_KEY="dein-geheimer-schluessel"
docker compose -f llm-api/docker-compose.yml up

# direkt
API_KEY="dein-schluessel" uvicorn api:app
```

Ist `API_KEY` gesetzt, muss jeder `/chat`-Request den Header `X-API-Key: <schluessel>` mitschicken. `/health` und `/providers` sind immer offen.

---

## Konfiguration

| Umgebungsvariable | Standard | Beschreibung |
|---|---|---|
| `LLM_CONFIG` | `../LLM_Client/config.json` | Pfad zur config.json |
| `API_KEY` | (leer) | HTTP-API-Key; leer = keine Authentifizierung |

`config.json` ist identisch mit `LLM_Client/config.json` und enthält API-Keys für alle Provider. Sie darf **nie** ins Image eingebaut werden — immer per Volume oder Secret mounten.

---

## Interaktive Dokumentation

Nach dem Start erreichbar unter:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Tests

```bash
# Abhängigkeiten
pip install fastapi uvicorn httpx

# Tests ausführen (kein echter API-Call, Providers werden gemockt)
python -m pytest llm-api/tests/ -v

# oder
python llm-api/tests/test_api.py
```

---

## Dateistruktur

```
llm-api/
├── api.py               # FastAPI-App
├── Dockerfile           # Build-Kontext: Repo-Root
├── docker-compose.yml   # Stack mit Volume-Mount für config.json
├── requirements.txt     # fastapi, uvicorn[standard]
├── examples/
│   └── requests.ps1     # PowerShell curl-Beispiele
├── tests/
│   └── test_api.py      # Unit-Tests (TestClient, keine echten API-Calls)
└── README.md
```
