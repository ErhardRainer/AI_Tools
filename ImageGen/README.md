# ImageGen

Einheitlicher Bildgenerierungs-Client für mehrere KI-Provider. Verwendbar als **Script**, **Python-Modul**, **CLI** oder **importierbare Bibliothek**. Alle API-Keys kommen aus einer JSON-Konfigurationsdatei.

---

## Unterstützte Provider

| Provider | Klasse | Standard-Modell | Modelle |
|---|---|---|---|
| `openai` | `OpenAIImageProvider` | `dall-e-3` | dall-e-3, dall-e-2 |
| `google` | `GoogleImageProvider` | `imagen-3.0-generate-002` | imagen-3.0-generate-002, imagen-3.0-fast-generate-001 |
| `stability` | `StabilityProvider` | `core` | core, sd3-large, sd3-large-turbo, sd3-medium, ultra |
| `fal` | `FalProvider` | `fal-ai/flux/dev` | flux/dev, flux/schnell, flux-pro, flux-realism, … |

---

## Schnellstart

```bash
# Abhängigkeiten
pip install ".[imagegen]"       # requests + google-genai
pip install openai               # für DALL-E

# Konfiguration
cp ImageGen/config.template.json ImageGen/config.json
# API-Keys in config.json eintragen

# Bild generieren
python ImageGen/image_gen.py --config ImageGen/config.json \
    --prompt "A serene mountain lake at golden hour" \
    --output mountain.png
```

---

## Drei Aufrufmöglichkeiten

```bash
# 1. Direktes Script
python ImageGen/image_gen.py --config ImageGen/config.json --prompt "..."

# 2. Als Python-Modul
python -m ImageGen --config ImageGen/config.json --prompt "..."

# 3. Installiertes CLI (nach: pip install ".[imagegen]")
image-gen --config ImageGen/config.json --prompt "..."
```

---

## CLI-Referenz

```bash
image-gen --config ImageGen/config.json \
    --prompt      "A sunset over mountains"  \  # Pflicht (oder in config)
    --provider    openai                     \  # openai | google | stability | fal
    --preset      flux                       \  # Preset-Alias aus config.json
    --model       dall-e-3                   \  # Modell überschreiben
    --output      image_{n}.png              \  # {n} = Bildindex (ab 1)
    --n           1                          \  # Anzahl Bilder
    --size        1024x1024                  \  # Größe (nur DALL-E)
    --quality     hd                         \  # standard|hd (nur DALL-E 3)
    --aspect-ratio 16:9                      \  # Seitenverhältnis (Stability/Google/fal)
    --no-save                                   # Nur Info ausgeben, nicht speichern
```

---

## Presets (Standard aus config.template.json)

| Alias | Provider | Modell |
|---|---|---|
| `quality` | openai | dall-e-3 |
| `fast` | fal | fal-ai/flux/schnell |
| `flux` | fal | fal-ai/flux/dev |
| `flux-pro` | fal | fal-ai/flux-pro |
| `sd3` | stability | sd3-large |
| `ultra` | stability | ultra |
| `imagen` | google | imagen-3.0-generate-002 |
| `imagen-fast` | google | imagen-3.0-fast-generate-001 |

```bash
image-gen --config config.json --preset flux --prompt "..."
image-gen --config config.json --preset sd3  --prompt "..." --aspect-ratio 16:9
```

---

## Programmatisch

```python
from ImageGen import build_provider, load_config, ImageResult

config   = load_config("ImageGen/config.json")
provider = build_provider("openai", config)

result: ImageResult = provider.generate(
    "A majestic eagle soaring above clouds",
    size="1024x1024",
    quality="hd",
)

# Alle Bilder speichern
paths = result.save_all("eagle_{n}.png")

# Einzelnes Bild
result.images[0].save("eagle.png")

# Überarbeiteter Prompt (DALL-E 3)
print(result.revised_prompt)
```

### Stability AI mit Negativprompt

```python
from ImageGen import build_provider, load_config

config   = load_config("ImageGen/config.json")
provider = build_provider("stability", config, model_override="sd3-large")

result = provider.generate(
    prompt="A beautiful sunset over the ocean",
    negative_prompt="people, buildings, cars",
    aspect_ratio="16:9",
)
result.save_all("sunset_{n}.png")
```

### fal.ai FLUX

```python
from ImageGen import build_provider, load_config

config   = load_config("ImageGen/config.json")
provider = build_provider("fal", config, model_override="fal-ai/flux-pro")

result = provider.generate(
    "A photorealistic portrait of a Viking warrior",
    image_size="portrait_4_3",
    n=2,
)
result.save_all("viking_{n}.png")
```

---

## Über die REST-API

```bash
# Bild generieren (DALL-E 3)
curl -X POST http://localhost:8000/image \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "prompt":   "A serene mountain lake at golden hour",
    "quality":  "hd"
  }'

# FLUX via Preset
curl -X POST http://localhost:8000/image \
  -H "Content-Type: application/json" \
  -d '{"preset": "flux", "prompt": "A cyberpunk street at night"}'

# Stability AI, Querformat
curl -X POST http://localhost:8000/image \
  -H "Content-Type: application/json" \
  -d '{
    "provider":     "stability",
    "model":        "sd3-large",
    "prompt":       "Epic mountain landscape",
    "aspect_ratio": "16:9"
  }'
```

---

## Konfiguration

```json
{
  "default_provider": "openai",
  "providers": {
    "openai":    { "api_key": "sk-...",     "model": "dall-e-3" },
    "google":    { "api_key": "AIza...",    "model": "imagen-3.0-generate-002" },
    "stability": { "api_key": "sk-...",     "model": "core" },
    "fal":       { "api_key": "...",        "model": "fal-ai/flux/dev" }
  },
  "presets": {
    "flux":  { "provider": "fal",       "model": "fal-ai/flux/dev" },
    "sd3":   { "provider": "stability", "model": "sd3-large" }
  }
}
```

---

## Installation

```bash
pip install ".[imagegen]"    # requests + google-genai (Stability, fal, Google)
pip install openai            # zusätzlich für DALL-E
pip install ".[all]"          # alle SDKs
```

---

## Tests

```bash
python ImageGen/unittest/run_all_tests.py
python ImageGen/unittest/run_all_tests.py -v
```

---

## Dateistruktur

```
ImageGen/
├── __init__.py              # Public API
├── __main__.py              # python -m ImageGen
├── image_gen.py             # Provider-Klassen, Factory, CLI
├── config.template.json     # Konfigurationsvorlage
├── examples/
│   ├── run_dalle.ps1        # OpenAI DALL-E Beispiele
│   ├── run_flux.ps1         # fal.ai FLUX Beispiele
│   ├── run_stability.ps1    # Stability AI Beispiele
│   └── run_google_imagen.ps1 # Google Imagen Beispiele
├── unittest/
│   ├── test_image_gen.py    # Unit-Tests (kein echter API-Call)
│   └── run_all_tests.py     # Test-Runner
└── README.md
```
