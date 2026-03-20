# ==============================================================================
# run_groq.ps1 — Beispielaufruf: Groq (console.groq.com)
# ==============================================================================
# Voraussetzung: pip install openai  (OpenAI-kompatible API)
# API-Key:       gsk_...  (console.groq.com → API Keys)
# Hinweis:       Groq bietet extrem schnelle Inferenz für Open-Weight-Modelle
# Konfiguration hier anpassen:

$Config   = "$PSScriptRoot\..\config.json"
$Provider = "groq"
$Model    = "llama-3.3-70b-versatile"    # llama-3.3-70b-versatile | llama-3.1-8b-instant | gemma2-9b-it | mixtral-8x7b-32768

# ------------------------------------------------------------------------------
# Aufruf 1: direktes Python-Script (kein Install nötig)
python "$PSScriptRoot\..\llm_client.py" --config $Config --provider $Provider --model $Model

# Aufruf 2: als Python-Modul (vom Repo-Root aus)
# python -m LLM_Client --config $Config --provider $Provider --model $Model

# Aufruf 3: installiertes CLI (nach: pip install .)
# llm-client --config $Config --provider $Provider --model $Model
