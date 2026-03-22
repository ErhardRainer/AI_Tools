# run_firefly.ps1 — Bildgenerierung mit Adobe Firefly (OAuth2)
#
# Voraussetzung:
#   pip install requests
#   cp ImageGen/config.template.json ImageGen/config.json
#   # firefly.client_id und firefly.client_secret in config.json setzen
#   # (KEIN api_key — Adobe Firefly nutzt OAuth2 Client Credentials)
#
# Anmeldung:
#   1. Adobe Developer Console: https://developer.adobe.com/console/projects
#   2. Neues Projekt erstellen → "Firefly API" hinzufügen
#   3. "Server-to-Server" Credentials → client_id und client_secret kopieren
#
# Modelle:
#   firefly-image-model-3      — Firefly Image Model 3 (Standard, GA)
#   firefly-image-model-3-fast — Firefly Image Model 3 Fast (schneller)
#   Image Model 4              — Nur Enterprise-Plan
#
# Größen: beliebig als WxH, z.B. 1024x1024, 2048x1152, 1152x2048

$Config = "$PSScriptRoot\..\config.json"

# ---------------------------------------------------------------------------
# a) Firefly Image Model 3 — Querformat (2048x1152)
# ---------------------------------------------------------------------------

python -m ImageGen `
    --config $Config `
    --preset firefly `
    --prompt "A breathtaking view of the Northern Lights over a frozen lake in Lapland" `
    --size 2048x1152 `
    --output "firefly_landscape.png"

# ---------------------------------------------------------------------------
# b) Quadratisch — Standard-Größe
# ---------------------------------------------------------------------------

python -m ImageGen `
    --config $Config `
    --preset firefly `
    --prompt "A vibrant watercolor painting of a Venetian canal at sunset" `
    --output "firefly_square.png"

# ---------------------------------------------------------------------------
# c) Hochformat — Portrait
# ---------------------------------------------------------------------------

# python -m ImageGen `
#     --config $Config `
#     --preset firefly `
#     --prompt "A fashion editorial portrait of a model in avant-garde clothing" `
#     --size 1152x2048 `
#     --output "firefly_portrait.png"

# ---------------------------------------------------------------------------
# d) Programmatisch — Token-Caching nutzen
# ---------------------------------------------------------------------------

# python -c "
# from ImageGen import build_provider, load_config
# config   = load_config('$Config')
# # Token wird pro Instanz gecacht (gültig 24h) — mehrere Aufrufe effizient
# provider = build_provider('firefly', config)
# for i, prompt in enumerate(['A mountain', 'A forest', 'An ocean'], 1):
#     result = provider.generate(prompt, size='1024x1024')
#     result.save_all(f'firefly_{i}_{{}}.png'.replace('{}', '{n}'))
# "
