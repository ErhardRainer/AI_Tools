# ==============================================================================
# run_gemini.ps1 — Beispielaufruf: Google Gemini (aistudio.google.com)
# ==============================================================================
# Voraussetzung: pip install google-generativeai
# Konfiguration hier anpassen:

$Config   = "$PSScriptRoot\..\config.json"
$Provider = "gemini"
$Model    = "gemini-2.0-flash"    # gemini-2.0-flash | gemini-2.0-pro | gemini-1.5-pro

# ------------------------------------------------------------------------------
# Aufruf 1: direktes Python-Script (kein Install nötig)
python "$PSScriptRoot\..\llm_client.py" --config $Config --provider $Provider --model $Model

# Aufruf 2: als Python-Modul (vom Repo-Root aus)
# python -m LLM_Client --config $Config --provider $Provider --model $Model

# Aufruf 3: installiertes CLI (nach: pip install ".[gemini]")
# llm-client --config $Config --provider $Provider --model $Model
