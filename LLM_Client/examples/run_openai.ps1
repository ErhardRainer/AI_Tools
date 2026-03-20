# ==============================================================================
# run_openai.ps1 — Beispielaufruf: OpenAI (platform.openai.com)
# ==============================================================================
# Konfiguration hier anpassen:

$Config   = "$PSScriptRoot\..\config.json"  # Pfad zur config.json
$Provider = "openai"
$Model    = "gpt-4o"                         # gpt-4o | gpt-4o-mini | o3 | o4-mini

# ------------------------------------------------------------------------------
# Aufruf 1: direktes Python-Script (kein Install nötig)
python "$PSScriptRoot\..\llm_client.py" --config $Config --provider $Provider --model $Model

# Aufruf 2: als Python-Modul (vom Repo-Root aus)
# python -m LLM_Client --config $Config --provider $Provider --model $Model

# Aufruf 3: installiertes CLI (nach: pip install .)
# llm-client --config $Config --provider $Provider --model $Model
