# ==============================================================================
# run_deepseek.ps1 — Beispielaufruf: DeepSeek (platform.deepseek.com)
# ==============================================================================
# Voraussetzung: pip install openai  (OpenAI-kompatible API)
# API-Key:       sk-...  (platform.deepseek.com → API Keys)
# Konfiguration hier anpassen:

$Config   = "$PSScriptRoot\..\config.json"
$Provider = "deepseek"
$Model    = "deepseek-chat"    # deepseek-chat (V3, Allgemein) | deepseek-reasoner (R1, Chain-of-Thought)

# ------------------------------------------------------------------------------
# Aufruf 1: direktes Python-Script (kein Install nötig)
python "$PSScriptRoot\..\llm_client.py" --config $Config --provider $Provider --model $Model

# Aufruf 2: als Python-Modul (vom Repo-Root aus)
# python -m LLM_Client --config $Config --provider $Provider --model $Model

# Aufruf 3: installiertes CLI (nach: pip install .)
# llm-client --config $Config --provider $Provider --model $Model

# Aufruf 4: über Preset-Alias (definiert in config.json unter "presets")
# python "$PSScriptRoot\..\llm_client.py" --config $Config --preset cheap
# python "$PSScriptRoot\..\llm_client.py" --config $Config --preset reasoning
