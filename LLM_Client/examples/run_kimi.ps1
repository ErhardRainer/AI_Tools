# ==============================================================================
# run_kimi.ps1 — Beispielaufruf: Moonshot AI Kimi (platform.moonshot.cn)
# ==============================================================================
# Voraussetzung: pip install openai  (OpenAI-kompatible API)
# API-Key:       sk-...  (platform.moonshot.cn → API Keys)
# Konfiguration hier anpassen:

$Config   = "$PSScriptRoot\..\config.json"
$Provider = "kimi"
$Model    = "kimi-k2"    # kimi-k2 | moonshot-v1-8k | moonshot-v1-32k | moonshot-v1-128k

# ------------------------------------------------------------------------------
# Aufruf 1: direktes Python-Script (kein Install nötig)
python "$PSScriptRoot\..\llm_client.py" --config $Config --provider $Provider --model $Model

# Aufruf 2: als Python-Modul (vom Repo-Root aus)
# python -m LLM_Client --config $Config --provider $Provider --model $Model

# Aufruf 3: installiertes CLI (nach: pip install .)
# llm-client --config $Config --provider $Provider --model $Model
