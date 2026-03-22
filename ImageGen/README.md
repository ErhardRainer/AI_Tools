# ImageGen

Einheitlicher Bildgenerierungs-Client für mehrere KI-Provider. Verwendbar als **Script**, **Python-Modul**, **CLI** oder **importierbare Bibliothek**. Alle API-Keys kommen aus einer JSON-Konfigurationsdatei.

---

## Unterstützte Provider

| Provider | Klasse | Standard-Modell | Modelle / Besonderheit |
|---|---|---|---|
| `openai` | `OpenAIImageProvider` | `dall-e-3` | dall-e-3, dall-e-2 |
| `google` | `GoogleImageProvider` | `imagen-4.0-generate-001` | Imagen 4/3 (`generate_images`), Gemini 2.5 Flash Image (`generate_content`) |
| `stability` | `StabilityProvider` | `core` | core, ultra, sd3-large/turbo/medium, sd3.5-large/turbo/medium |
| `fal` | `FalProvider` | `fal-ai/flux/dev` | flux/dev, flux/schnell, flux-pro, flux-realism, … |
| `ideogram` | `IdeogramProvider` | `V_3` | V_3, V_2A, V_2 |
| `leonardo` | `LeonardoProvider` | Phoenix 1.0 UUID | beliebige Modell-UUID, asynchrones Job-System |
| `firefly` | `FireflyProvider` | `firefly-image-model-3` | OAuth2 (client_id + client_secret, kein api_key!) |
| `auto1111` | `Auto1111Provider` | _(aktuell geladenes Modell)_ | lokale A1111-Instanz, kein API-Key nötig |
| `ollamadiffuser` | `OllamaDiffuserProvider` | `flux.1-schnell` | lokaler ollamadiffuser-Server, kein API-Key nötig |

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
    --prompt       "A sunset over mountains"   \  # Pflicht (oder in config)
    --provider     openai                      \  # Provider-Name
    --preset       flux                        \  # Preset-Alias aus config.json
    --model        dall-e-3                    \  # Modell überschreiben
    --output       image_{n}.png               \  # {n} = Bildindex (ab 1)
    --n            1                           \  # Anzahl Bilder
    --size         1024x1024                   \  # Größe in WxH (DALL-E, Firefly, A1111)
    --quality      hd                          \  # standard|hd (nur DALL-E 3)
    --aspect-ratio 16:9                        \  # Seitenverhältnis (Stability/Google/Ideogram)
    --no-save                                     # Nur Info ausgeben, nicht speichern
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
| `sd3.5` | stability | sd3.5-large |
| `sd3.5-turbo` | stability | sd3.5-large-turbo |
| `ultra` | stability | ultra |
| `imagen4` | google | imagen-4.0-generate-001 |
| `imagen4-fast` | google | imagen-4.0-fast-generate-001 |
| `imagen4-ultra` | google | imagen-4.0-ultra-generate-001 |
| `imagen3` | google | imagen-3.0-generate-002 |
| `gemini-flash` | google | gemini-2.5-flash-image-preview |
| `gemini-flash-exp` | google | gemini-2.0-flash-exp |
| `ideogram` | ideogram | V_3 |
| `ideogram-v2` | ideogram | V_2A |
| `leonardo` | leonardo | Phoenix 1.0 |
| `firefly` | firefly | firefly-image-model-3 |
| `local-flux` | ollamadiffuser | flux.1-schnell |
| `local-sdxl` | ollamadiffuser | sdxl |
| `local-a1111` | auto1111 | _(aktuell geladen)_ |

```bash
image-gen --config config.json --preset ideogram   --prompt "..."
image-gen --config config.json --preset local-flux --prompt "..."
image-gen --config config.json --preset firefly    --prompt "..." --size 2048x1152
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
paths = result.save_all("eagle_{n}.png")
```

### Ideogram mit Stil

```python
provider = build_provider("ideogram", config)
result = provider.generate(
    "A cinematic shot of a futuristic city at night",
    aspect_ratio="16:9",
    style_type="REALISTIC",
    negative_prompt="blurry, low quality",
)
result.save_all("ideogram_{n}.png")
```

### Adobe Firefly (OAuth2)

```python
# Konfiguration: providers.firefly.client_id + client_secret (kein api_key!)
provider = build_provider("firefly", config)
result = provider.generate("A Venetian canal at sunset", size="2048x1152")
result.save_all("firefly_{n}.png")
```

### Lokal — AUTOMATIC1111

```python
# Lokal starten: python launch.py --api  (http://127.0.0.1:7860)
provider = build_provider("auto1111", config, model_override="juggernautXL_v9")
result = provider.generate(
    "A photorealistic portrait",
    size="1024x1024",
    steps=30,
)
result.save_all("a1111_{n}.png")
```

### Lokal — ollamadiffuser (FLUX)

```python
# Lokal starten: ollamadiffuser run flux.1-schnell  (http://localhost:8000)
provider = build_provider("ollamadiffuser", config)
result = provider.generate("A cozy cabin in the snow", n=2)
result.save_all("local_{n}.png")
```

---

## Konfiguration

```json
{
  "default_provider": "openai",
  "providers": {
    "openai":          { "api_key": "sk-...",        "model": "dall-e-3" },
    "google":          { "api_key": "AIza...",       "model": "imagen-4.0-generate-001" },
    "stability":       { "api_key": "sk-...",        "model": "core" },
    "fal":             { "api_key": "...",           "model": "fal-ai/flux/dev" },
    "ideogram":        { "api_key": "...",           "model": "V_3" },
    "leonardo":        { "api_key": "uuid-...",      "model": "de7d3faf-..." },
    "firefly":         { "client_id": "...", "client_secret": "...", "model": "firefly-image-model-3" },
    "auto1111":        { "base_url": "http://127.0.0.1:7860", "model": "" },
    "ollamadiffuser":  { "base_url": "http://localhost:8000",  "model": "flux.1-schnell" }
  },
  "presets": {
    "flux":        { "provider": "fal",      "model": "fal-ai/flux/dev" },
    "local-flux":  { "provider": "ollamadiffuser", "model": "flux.1-schnell" }
  }
}
```

---

## Lokale Modelle — Top 5

| Modell | Typ | Lizenz | VRAM | Setup |
|---|---|---|---|---|
| FLUX.1 schnell | DiT 12B | Apache 2.0 ✅ | 12 GB | ollamadiffuser / A1111 |
| FLUX.1 dev | DiT 12B | non-commercial | 12 GB | ollamadiffuser / A1111 |
| Stable Diffusion 3.5 Large | MMDiT 8B | open-weights | 12 GB | A1111 / Diffusers |
| Juggernaut XL | SDXL | CivitAI | 8 GB | A1111 |
| DreamShaper XL Turbo | SDXL | CivitAI | 8 GB | A1111 |

---

## Installation

```bash
pip install ".[imagegen]"    # requests + google-genai (Stability, fal, Google, Ideogram, Leonardo, Firefly, lokal)
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
│   ├── run_dalle.ps1          # OpenAI DALL-E Beispiele
│   ├── run_flux.ps1           # fal.ai FLUX Beispiele
│   ├── run_stability.ps1      # Stability AI Beispiele
│   ├── run_google_imagen.ps1  # Google Imagen + Gemini Flash Image
│   ├── run_ideogram.ps1       # Ideogram V3
│   ├── run_leonardo.ps1       # Leonardo AI
│   ├── run_firefly.ps1        # Adobe Firefly (OAuth2)
│   └── run_local.ps1          # Lokal: AUTOMATIC1111 + ollamadiffuser
├── unittest/
│   ├── test_image_gen.py    # Unit-Tests (kein echter API-Call)
│   └── run_all_tests.py     # Test-Runner
└── README.md
```
