# run_dalle.ps1 — Bildgenerierung mit OpenAI DALL-E 3
#
# Voraussetzung:
#   pip install openai
#   cp ImageGen/config.template.json ImageGen/config.json
#   # openai.api_key in config.json setzen

$Config = "$PSScriptRoot\..\config.json"

# ---------------------------------------------------------------------------
# a) Standard: DALL-E 3, 1024x1024, Qualität "standard"
# ---------------------------------------------------------------------------

python -m ImageGen `
    --config $Config `
    --provider openai `
    --prompt "A serene mountain lake at golden hour, photorealistic" `
    --output "dalle_output.png"

# ---------------------------------------------------------------------------
# b) HD-Qualität, Querformat
# ---------------------------------------------------------------------------

python -m ImageGen `
    --config $Config `
    --provider openai `
    --model dall-e-3 `
    --prompt "Futuristic city skyline at night, cyberpunk style" `
    --size 1792x1024 `
    --quality hd `
    --output "dalle_hd.png"

# ---------------------------------------------------------------------------
# c) Hochformat
# ---------------------------------------------------------------------------

# python -m ImageGen `
#     --config $Config `
#     --provider openai `
#     --prompt "Portrait of an astronaut in a lush jungle" `
#     --size 1024x1792 `
#     --output "dalle_portrait.png"

# ---------------------------------------------------------------------------
# d) Preset verwenden (aus config.json)
# ---------------------------------------------------------------------------

# python -m ImageGen `
#     --config $Config `
#     --preset quality `
#     --prompt "A golden retriever playing in autumn leaves" `
#     --output "preset_output.png"

# ---------------------------------------------------------------------------
# e) Kein Speichern — nur URL ausgeben
# ---------------------------------------------------------------------------

# python -m ImageGen `
#     --config $Config `
#     --provider openai `
#     --prompt "Abstract watercolor painting" `
#     --no-save

# ---------------------------------------------------------------------------
# f) Programmatisch (Python)
# ---------------------------------------------------------------------------

# python -c "
# from ImageGen import build_provider, load_config
# config   = load_config('$Config')
# provider = build_provider('openai', config)
# result   = provider.generate(
#     'A majestic eagle soaring above clouds',
#     size='1024x1024', quality='hd',
# )
# result.save_all('eagle_{n}.png')
# print(f'Überarbeiteter Prompt: {result.revised_prompt}')
# "
