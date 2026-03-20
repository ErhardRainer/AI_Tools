# ==============================================================================
# run_presets.ps1 — Beispiele für das Preset/Alias-System
# ==============================================================================
# Presets werden in config.json unter "presets" definiert und lösen sich
# automatisch zu Provider + Modell auf. Kein Merken von Modellnamen nötig.
#
# Standard-Presets (aus config.template.json):
#   coding    → claude   + claude-opus-4-6         (beste Code-Qualität)
#   balanced  → openai   + gpt-4o                  (ausgewogen)
#   fast      → groq     + llama-3.1-8b-instant    (maximale Geschwindigkeit)
#   cheap     → deepseek + deepseek-chat            (günstigste Option)
#   reasoning → deepseek + deepseek-reasoner        (Chain-of-Thought / R1)
#   longctx   → kimi     + moonshot-v1-128k         (sehr langer Kontext)
#   creative  → gemini   + gemini-2.0-flash         (kreative Aufgaben)
#   code      → mistral  + codestral-latest         (Code-Spezialist)
# ==============================================================================

$Config = "$PSScriptRoot\..\config.json"

# --- Preset ohne Modell-Override ---
python "$PSScriptRoot\..\llm_client.py" --config $Config --preset coding
python "$PSScriptRoot\..\llm_client.py" --config $Config --preset fast
python "$PSScriptRoot\..\llm_client.py" --config $Config --preset cheap
python "$PSScriptRoot\..\llm_client.py" --config $Config --preset reasoning

# --- Preset mit explizitem Provider-Override (überschreibt Preset-Provider) ---
# python "$PSScriptRoot\..\llm_client.py" --config $Config --preset coding --provider openai

# --- Preset mit explizitem Modell-Override (überschreibt Preset-Modell) ---
# python "$PSScriptRoot\..\llm_client.py" --config $Config --preset coding --model claude-sonnet-4-6

# --- Als Python-Modul ---
# python -m LLM_Client --config $Config --preset reasoning

# --- Als installiertes CLI (nach: pip install .) ---
# llm-client --config $Config --preset balanced
