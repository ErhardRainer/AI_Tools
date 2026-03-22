# run_google_imagen.ps1 — Bildgenerierung mit Google Imagen 4 & Gemini Flash Image
#
# Voraussetzung:
#   pip install google-genai
#   cp ImageGen/config.template.json ImageGen/config.json
#   # google.api_key in config.json setzen (https://aistudio.google.com/apikey)
#
# Imagen 4 Modelle (generate_images):
#   imagen-4.0-generate-001       — Imagen 4 Standard (GA)
#   imagen-4.0-ultra-generate-001 — Imagen 4 Ultra (höchste Qualität)
#   imagen-4.0-fast-generate-001  — Imagen 4 Fast (günstiger/schneller)
#   imagen-3.0-generate-002       — Imagen 3 (ältere Generation)
#
# Gemini Flash Image Modelle (generate_content + response_modalities):
#   gemini-2.5-flash-image-preview — Gemini 2.5 Flash Image (Vorschau)
#   gemini-2.0-flash-exp           — Gemini 2.0 Flash Experimental
#   → Kombinieren Text- und Bildgenerierung in einem Modell
#
# Seitenverhältnisse (nur Imagen): 1:1, 3:4, 4:3, 9:16, 16:9

$Config = "$PSScriptRoot\..\config.json"

# ---------------------------------------------------------------------------
# a) Imagen 4 Standard — Quadratisch
# ---------------------------------------------------------------------------

python -m ImageGen `
    --config $Config `
    --preset imagen4 `
    --prompt "A vibrant coral reef teeming with colorful tropical fish" `
    --output "imagen4_output.png"

# ---------------------------------------------------------------------------
# b) Imagen 4 Ultra — Höchste Qualität, Querformat
# ---------------------------------------------------------------------------

python -m ImageGen `
    --config $Config `
    --preset imagen4-ultra `
    --prompt "Epic mountain range at golden hour, ultra-detailed, photorealistic" `
    --aspect-ratio 16:9 `
    --output "imagen4_ultra_landscape.png"

# ---------------------------------------------------------------------------
# c) Imagen 4 Fast — Günstig und schnell
# ---------------------------------------------------------------------------

# python -m ImageGen `
#     --config $Config `
#     --preset imagen4-fast `
#     --prompt "A cozy coffee shop interior with warm lighting" `
#     --output "imagen4_fast.png"

# ---------------------------------------------------------------------------
# d) Gemini 2.5 Flash Image — Text + Bild kombiniert
# ---------------------------------------------------------------------------

python -m ImageGen `
    --config $Config `
    --preset gemini-flash `
    --prompt "A futuristic city skyline at night with neon lights and flying cars" `
    --output "gemini_flash_output.png"

# ---------------------------------------------------------------------------
# e) Gemini 2.0 Flash Experimental
# ---------------------------------------------------------------------------

# python -m ImageGen `
#     --config $Config `
#     --preset gemini-flash-exp `
#     --prompt "An illustrated fairy-tale forest with glowing mushrooms" `
#     --output "gemini_exp_output.png"

# ---------------------------------------------------------------------------
# f) Imagen 3 (ältere Generation, für Vergleiche)
# ---------------------------------------------------------------------------

# python -m ImageGen `
#     --config $Config `
#     --preset imagen3 `
#     --prompt "A serene Japanese garden in spring" `
#     --aspect-ratio 4:3 `
#     --output "imagen3_output.png"

# ---------------------------------------------------------------------------
# g) Programmatisch — Imagen 4 mit Seitenverhältnis
# ---------------------------------------------------------------------------

# python -c "
# from ImageGen import build_provider, load_config
# config   = load_config('$Config')
# provider = build_provider('google', config, model_override='imagen-4.0-generate-001')
# result   = provider.generate(
#     'A majestic snow-capped mountain at sunrise',
#     aspect_ratio='4:3',
# )
# result.save_all('mountain_{n}.png')
# "

# ---------------------------------------------------------------------------
# h) Programmatisch — Gemini Flash Image
# ---------------------------------------------------------------------------

# python -c "
# from ImageGen import build_provider, load_config
# config   = load_config('$Config')
# provider = build_provider('google', config, model_override='gemini-2.5-flash-image-preview')
# result   = provider.generate(
#     'A photorealistic portrait of a robot reading a book in a library',
# )
# result.save_all('gemini_{n}.png')
# print(f'{len(result.images)} Bild(er) generiert')
# "
