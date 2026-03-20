# run_google_imagen.ps1 — Bildgenerierung mit Google Imagen 3
#
# Voraussetzung:
#   pip install google-genai
#   cp ImageGen/config.template.json ImageGen/config.json
#   # google.api_key in config.json setzen (https://aistudio.google.com/apikey)
#
# Modelle:
#   imagen-3.0-generate-002      — Imagen 3 (Standard, höchste Qualität)
#   imagen-3.0-fast-generate-001 — Imagen 3 Fast (schneller, kostengünstiger)
#
# Seitenverhältnisse: 1:1, 3:4, 4:3, 9:16, 16:9

$Config = "$PSScriptRoot\..\config.json"

# ---------------------------------------------------------------------------
# a) Imagen 3 Standard — Quadratisch
# ---------------------------------------------------------------------------

python -m ImageGen `
    --config $Config `
    --preset imagen `
    --prompt "A vibrant coral reef teeming with colorful tropical fish" `
    --output "imagen_output.png"

# ---------------------------------------------------------------------------
# b) Imagen 3 Fast — Querformat
# ---------------------------------------------------------------------------

python -m ImageGen `
    --config $Config `
    --preset imagen-fast `
    --prompt "Rolling green hills with wildflowers under a blue sky" `
    --aspect-ratio 16:9 `
    --output "imagen_fast_landscape.png"

# ---------------------------------------------------------------------------
# c) Hochformat (Porträt)
# ---------------------------------------------------------------------------

# python -m ImageGen `
#     --config $Config `
#     --provider google `
#     --prompt "An elegant dancer on a stage with dramatic spotlighting" `
#     --aspect-ratio 9:16 `
#     --output "imagen_portrait.png"

# ---------------------------------------------------------------------------
# d) Programmatisch
# ---------------------------------------------------------------------------

# python -c "
# from ImageGen import build_provider, load_config
# config   = load_config('$Config')
# provider = build_provider('google', config)
# result   = provider.generate(
#     'A majestic snow-capped mountain at sunrise',
#     aspect_ratio='4:3',
# )
# result.save_all('mountain_{n}.png')
# "
