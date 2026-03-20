# ==============================================================================
# run_claude.ps1 — Beispielaufruf: Anthropic Claude (console.anthropic.com)
# ==============================================================================
# Voraussetzung: pip install anthropic
# Konfiguration hier anpassen:

$Config   = "$PSScriptRoot\..\config.json"
$Provider = "claude"
$Model    = "claude-sonnet-4-6"    # claude-sonnet-4-6 | claude-opus-4-6 | claude-haiku-4-5-20251001

# ------------------------------------------------------------------------------
# Aufruf 1: direktes Python-Script (kein Install nötig)
python "$PSScriptRoot\..\llm_client.py" --config $Config --provider $Provider --model $Model

# Aufruf 2: als Python-Modul (vom Repo-Root aus)
# python -m LLM_Client --config $Config --provider $Provider --model $Model

# Aufruf 3: installiertes CLI (nach: pip install ".[claude]")
# llm-client --config $Config --provider $Provider --model $Model
