# run_leonardo.ps1 — Bildgenerierung mit Leonardo AI (asynchrones Job-System)
#
# Voraussetzung:
#   pip install requests
#   cp ImageGen/config.template.json ImageGen/config.json
#   # leonardo.api_key in config.json setzen (https://app.leonardo.ai/ → API)
#   # API-Key ist eine UUID, KEIN sk-... Format
#
# Modell-IDs werden als UUID angegeben. Bekannte Modelle:
#   de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3 — Phoenix 1.0 (Standard)
#   aa77f04e-3eec-4034-9c07-d0f619684628 — Leonardo Kino XL
# Alle Modelle abrufen: GET https://cloud.leonardo.ai/api/rest/v1/platformModels
#
# HINWEIS: Leonardo nutzt ein asynchrones System (Job erstellen → pollen).
# Der Aufruf wartet automatisch bis zu 5 Minuten auf die Fertigstellung.

$Config = "$PSScriptRoot\..\config.json"

# ---------------------------------------------------------------------------
# a) Phoenix 1.0 — Standard (Querformat)
# ---------------------------------------------------------------------------

python -m ImageGen `
    --config $Config `
    --preset leonardo `
    --prompt "A dramatic medieval castle on a cliffside at golden hour, photorealistic" `
    --output "leonardo_phoenix.png"

# ---------------------------------------------------------------------------
# b) Kino XL — Kinematografischer Stil
# ---------------------------------------------------------------------------

# python -m ImageGen `
#     --config $Config `
#     --provider leonardo `
#     --model "aa77f04e-3eec-4034-9c07-d0f619684628" `
#     --prompt "A cinematic wide shot of a neon-lit cyberpunk alley in the rain" `
#     --output "leonardo_kino.png"

# ---------------------------------------------------------------------------
# c) Mehrere Bilder generieren
# ---------------------------------------------------------------------------

# python -m ImageGen `
#     --config $Config `
#     --preset leonardo `
#     --prompt "A serene Japanese zen garden with cherry blossoms" `
#     --n 2 `
#     --output "leonardo_{n}.png"

# ---------------------------------------------------------------------------
# d) Programmatisch — mit width/height und negative_prompt
# ---------------------------------------------------------------------------

# python -c "
# from ImageGen import build_provider, load_config
# config   = load_config('$Config')
# provider = build_provider('leonardo', config)
# result   = provider.generate(
#     'A hyperrealistic portrait of an elderly sailor with weathered skin',
#     n=1,
#     width=832,
#     height=1472,
#     negative_prompt='cartoon, anime, painting',
# )
# result.save_all('leonardo_{n}.png')
# "
