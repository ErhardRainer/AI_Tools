# run_local.ps1 — Lokale Bildgenerierung mit AUTOMATIC1111 und ollamadiffuser
#
# Kein API-Key erforderlich! Beide Provider laufen lokal auf dem eigenen Rechner.
#
# ══════════════════════════════════════════════════════════════════════════════
# OPTION A: AUTOMATIC1111 Stable Diffusion WebUI
# ══════════════════════════════════════════════════════════════════════════════
#
# Installation:
#   git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui
#   cd stable-diffusion-webui
#   # Modell herunterladen (z.B. von https://civitai.com oder HuggingFace)
#   # Modell-Datei in models/Stable-diffusion/ ablegen
#   python launch.py --api   ← startet WebUI + API auf http://127.0.0.1:7860
#
# Top lokale Modelle (SDXL und schnellere Alternative):
#   SDXL Base:         stabilityai/stable-diffusion-xl-base-1.0
#   Juggernaut XL:     CivitAI-Download, sehr realistische Fotos
#   DreamShaper XL:    CivitAI-Download, kreativ/vielseitig
#   FLUX.1 schnell:    black-forest-labs/FLUX.1-schnell (Apache 2.0)
#   FLUX.1 dev:        black-forest-labs/FLUX.1-dev     (beste Qualität)
#
# ══════════════════════════════════════════════════════════════════════════════
# OPTION B: ollamadiffuser (einfacher lokaler API-Server)
# ══════════════════════════════════════════════════════════════════════════════
#
# Installation:
#   pip install ollamadiffuser
#   ollamadiffuser pull flux.1-schnell   ← Modell herunterladen (~25 GB)
#   ollamadiffuser run flux.1-schnell    ← startet API auf http://localhost:8000
#
# Unterstützte Modelle:
#   flux.1-schnell  — FLUX.1 Schnell (Apache 2.0, 1-4 Steps, empfohlen)
#   flux.1-dev      — FLUX.1 Dev (non-commercial, beste Qualität)
#   sdxl            — Stable Diffusion XL
#   sd3-medium      — SD 3 Medium
#   sd1.5           — SD 1.5 (leichtgewichtig, schnell)

$Config = "$PSScriptRoot\..\config.json"

# ---------------------------------------------------------------------------
# AUTOMATIC1111: Bild mit aktuell geladenem Modell generieren
# ---------------------------------------------------------------------------

python -m ImageGen `
    --config $Config `
    --preset local-a1111 `
    --prompt "A majestic wolf howling at a full moon, dramatic lighting, detailed fur" `
    --size 512x512 `
    --output "a1111_output.png"

# ---------------------------------------------------------------------------
# AUTOMATIC1111: SDXL-Auflösung (1024x1024)
# ---------------------------------------------------------------------------

# python -m ImageGen `
#     --config $Config `
#     --provider auto1111 `
#     --prompt "An epic fantasy battle scene, oil painting style, ultra detailed" `
#     --size 1024x1024 `
#     --output "a1111_sdxl.png"

# ---------------------------------------------------------------------------
# ollamadiffuser: FLUX.1 Schnell (Standard)
# ---------------------------------------------------------------------------

python -m ImageGen `
    --config $Config `
    --preset local-flux `
    --prompt "A cozy log cabin in a snowy forest at night with warm glowing windows" `
    --output "local_flux.png"

# ---------------------------------------------------------------------------
# ollamadiffuser: SDXL lokal
# ---------------------------------------------------------------------------

# python -m ImageGen `
#     --config $Config `
#     --preset local-sdxl `
#     --prompt "A photorealistic sports car on a winding mountain road" `
#     --output "local_sdxl.png"

# ---------------------------------------------------------------------------
# ollamadiffuser: FLUX.1 Dev (höchste Qualität, non-commercial)
# ---------------------------------------------------------------------------

# python -m ImageGen `
#     --config $Config `
#     --provider ollamadiffuser `
#     --model "flux.1-dev" `
#     --prompt "A hyperrealistic macro photo of a dewdrop on a spider web at sunrise" `
#     --output "local_flux_dev.png"

# ---------------------------------------------------------------------------
# Programmatisch — AUTOMATIC1111 mit spezifischem Modell laden
# ---------------------------------------------------------------------------

# python -c "
# from ImageGen import build_provider, load_config
# config   = load_config('$Config')
# # model-Parameter setzt den Checkpoint in A1111 (muss installiert sein)
# provider = build_provider('auto1111', config, model_override='juggernautXL_v9')
# result   = provider.generate(
#     'A photorealistic portrait of a woman with freckles in soft morning light',
#     size='1024x1024',
#     steps=30,
#     cfg_scale=7.0,
# )
# result.save_all('a1111_{n}.png')
# "

# ---------------------------------------------------------------------------
# Programmatisch — ollamadiffuser mit SD 1.5 (schnell, leichtgewichtig)
# ---------------------------------------------------------------------------

# python -c "
# from ImageGen import build_provider, load_config
# config   = load_config('$Config')
# provider = build_provider('ollamadiffuser', config, model_override='sd1.5')
# result   = provider.generate(
#     'A cartoon fox reading a book under a tree',
#     n=2,
# )
# result.save_all('local_{n}.png')
# print(f'{len(result.images)} Bilder generiert')
# "
