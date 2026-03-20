# ==============================================================================
# run_prompts_file.ps1 — Prompts aus externer JSON-Datei laden
# ==============================================================================
# Statt Prompts in config.json zu hinterlegen, können sie aus einer separaten
# JSON-Datei geladen werden. Zwei Formate werden unterstützt:
#
# Variante a — einzelnes Prompt-Set:
#   { "system": "...", "context": "...", "task": "..." }
#
# Variante b — mehrere benannte Prompt-Sets:
#   {
#     "summarize": { "system": "...", "context": "...", "task": "..." },
#     "translate":  { "system": "...", "context": "...", "task": "..." }
#   }
# ==============================================================================

$Config      = "$PSScriptRoot\..\config.json"
$PromptsA    = "$PSScriptRoot\prompts_single.json"   # Variante a
$PromptsB    = "$PSScriptRoot\prompts_named.json"    # Variante b

# --- Variante a: einzelnes Prompt-Set ---
# Überschreibt die Prompts aus config.json vollständig.
python "$PSScriptRoot\..\llm_client.py" --config $Config --prompts-file $PromptsA

# --- Variante a mit Provider-Override ---
# python "$PSScriptRoot\..\llm_client.py" --config $Config --prompts-file $PromptsA --provider claude

# --- Variante b: benanntes Set "summarize" laden ---
python "$PSScriptRoot\..\llm_client.py" --config $Config --prompts-file $PromptsB --prompts-name summarize

# --- Variante b: benanntes Set "translate" laden ---
python "$PSScriptRoot\..\llm_client.py" --config $Config --prompts-file $PromptsB --prompts-name translate

# --- Variante b ohne --prompts-name: "default"-Set wird verwendet ---
# python "$PSScriptRoot\..\llm_client.py" --config $Config --prompts-file $PromptsB

# --- Preset + externe Prompts kombinieren ---
# python "$PSScriptRoot\..\llm_client.py" --config $Config --preset coding --prompts-file $PromptsB --prompts-name summarize

# --- Als Python-Modul ---
# python -m LLM_Client --config $Config --prompts-file $PromptsB --prompts-name translate

# --- Als installiertes CLI (nach: pip install .) ---
# llm-client --config $Config --prompts-file $PromptsA

# --- Programmatisch ---
# from LLM_Client import load_prompts_file, build_provider, load_config
#
# # Variante a
# prompts = load_prompts_file("prompts_single.json")
#
# # Variante b
# prompts = load_prompts_file("prompts_named.json", name="summarize")
#
# config   = load_config("config.json")
# provider = build_provider("openai", config)
# print(provider.send(**prompts))
