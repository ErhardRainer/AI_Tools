# ==============================================================================
# run_grok.ps1 — Beispielaufruf: xAI Grok (console.x.ai)
# ==============================================================================
# Voraussetzung: pip install openai  (OpenAI-kompatible API)
# API-Key:       xai-...  (console.x.ai → API Keys)
# Konfiguration hier anpassen:

$Config   = "$PSScriptRoot\..\config.json"
$Provider = "grok"
$Model    = "grok-3"    # grok-3 | grok-3-mini | grok-3-fast | grok-2-1212

# ------------------------------------------------------------------------------
# Aufruf 1: direktes Python-Script (kein Install nötig)
python "$PSScriptRoot\..\llm_client.py" --config $Config --provider $Provider --model $Model

# Aufruf 2: als Python-Modul (vom Repo-Root aus)
# python -m LLM_Client --config $Config --provider $Provider --model $Model

# Aufruf 3: installiertes CLI (nach: pip install .)
# llm-client --config $Config --provider $Provider --model $Model
