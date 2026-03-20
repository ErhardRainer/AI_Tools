# ==============================================================================
# run_mistral.ps1 — Beispielaufruf: Mistral AI (console.mistral.ai)
# ==============================================================================
# Voraussetzung: pip install openai  (OpenAI-kompatible API)
# API-Key:       ...  (console.mistral.ai → API Keys)
# Konfiguration hier anpassen:

$Config   = "$PSScriptRoot\..\config.json"
$Provider = "mistral"
$Model    = "mistral-large-latest"    # mistral-large-latest | mistral-small-latest | codestral-latest | open-mixtral-8x22b

# ------------------------------------------------------------------------------
# Aufruf 1: direktes Python-Script (kein Install nötig)
python "$PSScriptRoot\..\llm_client.py" --config $Config --provider $Provider --model $Model

# Aufruf 2: als Python-Modul (vom Repo-Root aus)
# python -m LLM_Client --config $Config --provider $Provider --model $Model

# Aufruf 3: installiertes CLI (nach: pip install .)
# llm-client --config $Config --provider $Provider --model $Model
