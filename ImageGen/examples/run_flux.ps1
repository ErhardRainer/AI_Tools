# run_flux.ps1 — Bildgenerierung mit fal.ai FLUX-Modellen
#
# Voraussetzung:
#   pip install requests
#   cp ImageGen/config.template.json ImageGen/config.json
#   # fal.api_key in config.json setzen (https://fal.ai/dashboard/keys)
#
# Modelle:
#   fal-ai/flux/schnell      — Sehr schnell (4 Schritte)
#   fal-ai/flux/dev          — Hochwertig (Standard)
#   fal-ai/flux-pro          — Professionell (höchste Qualität)
#   fal-ai/flux-realism      — Realistische Fotos

$Config = "$PSScriptRoot\..\config.json"

# ---------------------------------------------------------------------------
# a) FLUX Dev — Standard
# ---------------------------------------------------------------------------

python -m ImageGen `
    --config $Config `
    --provider fal `
    --prompt "A cozy cabin in a snowy pine forest at dusk, warm light in windows" `
    --output "flux_output.png"

# ---------------------------------------------------------------------------
# b) FLUX Schnell — Schnellste Variante
# ---------------------------------------------------------------------------

python -m ImageGen `
    --config $Config `
    --preset fast `
    --prompt "Abstract digital art, vibrant colors, geometric shapes" `
    --output "flux_schnell.png"

# ---------------------------------------------------------------------------
# c) FLUX Pro — Höchste Qualität, Querformat
# ---------------------------------------------------------------------------

# python -m ImageGen `
#     --config $Config `
#     --preset flux-pro `
#     --prompt "Epic fantasy landscape with ancient ruins" `
#     --aspect-ratio 16:9 `
#     --output "flux_pro_landscape.png"

# ---------------------------------------------------------------------------
# d) Mehrere Bilder generieren
# ---------------------------------------------------------------------------

# python -m ImageGen `
#     --config $Config `
#     --provider fal `
#     --prompt "Minimalist logo design for a tech startup" `
#     --n 4 `
#     --output "logo_{n}.png"

# ---------------------------------------------------------------------------
# e) Über die REST-API
# ---------------------------------------------------------------------------

# curl -X POST http://localhost:8000/image `
#   -H 'Content-Type: application/json' `
#   -d '{
#     "provider": "fal",
#     "model":    "fal-ai/flux/dev",
#     "prompt":   "A serene Japanese garden in spring",
#     "image_size": "landscape_4_3"
#   }'
