# run_ideogram.ps1 — Bildgenerierung mit Ideogram V3 (und älteren Versionen)
#
# Voraussetzung:
#   pip install requests
#   cp ImageGen/config.template.json ImageGen/config.json
#   # ideogram.api_key in config.json setzen (https://developer.ideogram.ai/)
#
# Authentifizierung: Api-Key Header (NICHT Bearer) — darauf achten!
#
# Modelle:  V_3 (Standard), V_2A, V_2
# Stile:    AUTO, REALISTIC, DESIGN, ANIME, RENDER_3D, ILLUSTRATION
# Formate:  ASPECT_1_1, ASPECT_16_9, ASPECT_10_16, ASPECT_4_3, ASPECT_3_4

$Config = "$PSScriptRoot\..\config.json"

# ---------------------------------------------------------------------------
# a) Ideogram V3 — Standard (1:1, AUTO-Stil)
# ---------------------------------------------------------------------------

python -m ImageGen `
    --config $Config `
    --preset ideogram `
    --prompt "A surreal dreamscape with floating islands and bioluminescent waterfalls" `
    --output "ideogram_v3.png"

# ---------------------------------------------------------------------------
# b) Ideogram V3 — Realistisch, Querformat
# ---------------------------------------------------------------------------

python -m ImageGen `
    --config $Config `
    --preset ideogram `
    --prompt "A photorealistic portrait of an astronaut on Mars at sunset" `
    --aspect-ratio 16:9 `
    --output "ideogram_landscape.png"

# ---------------------------------------------------------------------------
# c) Ideogram V2a — ältere Generation
# ---------------------------------------------------------------------------

# python -m ImageGen `
#     --config $Config `
#     --preset ideogram-v2 `
#     --prompt "A minimalist poster of a mountain range in flat design" `
#     --output "ideogram_v2a.png"

# ---------------------------------------------------------------------------
# d) Programmatisch — mit style_type und negative_prompt
# ---------------------------------------------------------------------------

# python -c "
# from ImageGen import build_provider, load_config
# config   = load_config('$Config')
# provider = build_provider('ideogram', config)
# result   = provider.generate(
#     'A cinematic shot of a futuristic city at night',
#     aspect_ratio='16:9',
#     style_type='REALISTIC',
#     negative_prompt='blurry, low quality, cartoon',
# )
# result.save_all('ideogram_{n}.png')
# "
