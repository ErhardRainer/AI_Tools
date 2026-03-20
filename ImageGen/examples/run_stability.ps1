# run_stability.ps1 — Bildgenerierung mit Stability AI
#
# Voraussetzung:
#   pip install requests
#   cp ImageGen/config.template.json ImageGen/config.json
#   # stability.api_key in config.json setzen (https://platform.stability.ai/account/keys)
#
# Modelle:
#   core         — Stable Image Core (schnell, günstig)
#   sd3-large    — Stable Diffusion 3 Large (höchste Qualität, 6.5B)
#   sd3-large-turbo  — SD3 Large Turbo (schneller, etwas weniger Qualität)
#   sd3-medium   — SD3 Medium (2B Parameter, ausgewogen)
#   ultra        — Stable Image Ultra (SDXL-Basis, sehr detailliert)

$Config = "$PSScriptRoot\..\config.json"

# ---------------------------------------------------------------------------
# a) Core-Modell — Standard (schnell und kostengünstig)
# ---------------------------------------------------------------------------

python -m ImageGen `
    --config $Config `
    --provider stability `
    --model core `
    --prompt "A tranquil forest path in autumn, golden light through trees" `
    --output "stability_core.png"

# ---------------------------------------------------------------------------
# b) SD3 Large — Höchste Qualität
# ---------------------------------------------------------------------------

python -m ImageGen `
    --config $Config `
    --preset sd3 `
    --prompt "Portrait of a noble warrior in ancient armor, dramatic lighting" `
    --aspect-ratio 3:4 `
    --output "sd3_portrait.png"

# ---------------------------------------------------------------------------
# c) Ultra — Sehr detailliert, Querformat
# ---------------------------------------------------------------------------

# python -m ImageGen `
#     --config $Config `
#     --preset ultra `
#     --prompt "Aerial view of a tropical island at sunrise" `
#     --aspect-ratio 16:9 `
#     --output "ultra_landscape.png"

# ---------------------------------------------------------------------------
# d) Mehrere Varianten eines Prompts (n=3 macht 3 API-Calls)
# ---------------------------------------------------------------------------

# python -m ImageGen `
#     --config $Config `
#     --provider stability `
#     --prompt "Concept art of a futuristic space station" `
#     --n 3 `
#     --output "space_{n}.png"

# ---------------------------------------------------------------------------
# e) Programmatisch mit Negativprompt
# ---------------------------------------------------------------------------

# python -c "
# from ImageGen import build_provider, load_config
# config   = load_config('$Config')
# provider = build_provider('stability', config, model_override='sd3-large')
# result   = provider.generate(
#     prompt='A beautiful sunset over the ocean',
#     negative_prompt='people, buildings, cars',
#     aspect_ratio='16:9',
# )
# result.save_all('sunset_{n}.png')
# "
