# ==============================================================================
# run_config_writer.ps1 — API-Keys und Standard-Modelle in config.json setzen
# ==============================================================================
# set_api_key()       schreibt den API-Key eines Providers in die config.json.
# set_default_model() setzt das Standard-Modell eines Providers.
#
# Alle anderen Felder der Datei (andere Provider, Presets, Prompts) bleiben
# unverändert. Existiert der Provider-Eintrag noch nicht, wird er angelegt.
# ==============================================================================

$Config = "$PSScriptRoot\..\config.json"

# --- API-Key setzen (CLI) ---
# Schreibt providers.openai.api_key in config.json und beendet sofort.
python "$PSScriptRoot\..\llm_client.py" --config $Config --set-api-key openai  "sk-..."
python "$PSScriptRoot\..\llm_client.py" --config $Config --set-api-key claude  "sk-ant-..."
python "$PSScriptRoot\..\llm_client.py" --config $Config --set-api-key grok    "xai-..."
python "$PSScriptRoot\..\llm_client.py" --config $Config --set-api-key deepseek "sk-..."

# --- Standard-Modell setzen (CLI) ---
# Schreibt providers.openai.model in config.json und beendet sofort.
python "$PSScriptRoot\..\llm_client.py" --config $Config --set-default-model openai   "gpt-4o"
python "$PSScriptRoot\..\llm_client.py" --config $Config --set-default-model deepseek "deepseek-reasoner"
python "$PSScriptRoot\..\llm_client.py" --config $Config --set-default-model groq     "gemma2-9b-it"

# --- Als Python-Modul (gleichwertig zum direkten Script-Aufruf) ---
# python -m LLM_Client --config $Config --set-api-key claude "sk-ant-..."
# python -m LLM_Client --config $Config --set-default-model mistral "codestral-latest"

# --- Als installiertes CLI (nach: pip install .) ---
# llm-client --config $Config --set-api-key kimi "sk-..."
# llm-client --config $Config --set-default-model kimi "moonshot-v1-128k"

# --- Programmatisch (Python) ---
# from LLM_Client import set_api_key, set_default_model
#
# set_api_key("openai",   "sk-...",            "LLM_Client/config.json")
# set_api_key("claude",   "sk-ant-...",        "LLM_Client/config.json")
# set_api_key("deepseek", "sk-...",            "LLM_Client/config.json")
#
# set_default_model("openai",   "gpt-4o",             "LLM_Client/config.json")
# set_default_model("deepseek", "deepseek-reasoner",   "LLM_Client/config.json")
# set_default_model("groq",     "llama-3.1-8b-instant","LLM_Client/config.json")
