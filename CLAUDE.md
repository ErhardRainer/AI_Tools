# CLAUDE.md — AI Assistant Guide for This Repository

## Repository Overview

This repository (`OpenAI`) contains Python-based tools for working with the OpenAI API, primarily focused on the **OpenAI Assistants API**. The project is documented in German with some English identifiers.

**Repository description (README):** _"Tools rund um OpenAI wie Assistant AI und Chat-GPT-API usw."_ (Tools around OpenAI such as Assistant AI and Chat-GPT-API, etc.)

---

## Structure

```
OpenAI/
├── README.md                          # Brief German description
├── CLAUDE.md                          # This file
├── .gitignore                         # Excludes real config.json and secrets
├── Assistant_AI/
│   └── Assistant_AI.ipynb             # Assistants API notebook (47 cells)
└── LLM_Client/
    ├── llm_client.py                  # Multi-provider LLM client script
    └── config.template.json           # Config template (copy → config.json)
```

---

## The Main Notebook: `Assistant_AI/Assistant_AI.ipynb`

This notebook is a comprehensive reference implementation for the **OpenAI Assistants API** (beta). It is structured as a sequential workflow:

### Section 0 — Setup
- Dependency imports: `pprint`, `json`, `time`, `openai`, `os`, `pandas`
- Guards with `try/except ImportError` with descriptive error messages
- Uses a `get_value_from_json_file(json_file_path, key_path)` utility to read config (e.g. API key) from a JSON file using dot-separated key paths
- The OpenAI `client` is initialized from config stored in a JSON file (not hardcoded)

### Section 1 — File Upload (Knowledgebase)
Manages files uploaded to OpenAI for use as a retrieval knowledge base.

| Function | Description |
|---|---|
| `upload_files(directory_path)` | Upload all allowed files from a directory |
| `upload_file(filepath)` | Upload a single file |
| `upload_files_array(filepaths)` | Upload a list of file paths |
| `get_files(purpose_filter, filename_pattern)` | List files, optionally filtered; returns a DataFrame |
| `convert_xlsx_to_csv(xlsx_file_path, csv_file_path, skip_rows)` | Convert Excel to CSV before uploading |
| `delete_unassociated_files()` | Delete files not linked to any assistant |

Allowed file extensions: `.pdf`, `.txt`, `.json`, `.csv`

Upload limits: 512 MB per file, 100 GB total storage.

### Section 2 — Assistant Management
Creates and manages OpenAI Assistants.

| Function | Description |
|---|---|
| `create_assistant(name, instruction, retrieval, code_interpreter, file_ids, model)` | Create a new assistant; model defaults to `gpt-4-1106-preview` |
| `update_assistant(assistant_id, ...)` | Update existing assistant attributes (reads current state first) |
| `add_files_assistant(assistant_id, new_file_ids)` | Add files to an existing assistant |
| `get_assistants(name, dataframe)` | List assistants, optionally filter by name; can return DataFrame |
| `get_assistant_attributes(assistant_id)` | Retrieve attributes dict (id, name, model, created_at, file_ids, tools) |
| `get_file_association(assistant_name)` | Map files to their associated assistants |
| `delete_assistant_by_name(name)` | Delete all assistants matching a given name |

### Section 3 — Conversation (Threads)
Implements a full conversation loop using OpenAI threads.

| Step | API Call |
|---|---|
| Create thread | `client.beta.threads.create()` |
| Add user message | `client.beta.threads.messages.create(thread_id, role='user', content=...)` |
| Run assistant | `client.beta.threads.runs.create(thread_id, assistant_id, instructions=...)` |
| Poll status | `client.beta.threads.runs.retrieve(thread_id, run_id)` in a `while` loop with `time.sleep(10)` |
| Read response | `client.beta.threads.messages.list(thread_id)` |

The run polling pattern waits until `run.status` is `"completed"` or `"failed"`.

---

## Key Conventions

### Language
- **Code**: Python, with English function/variable names
- **Comments and markdown cells**: German
- **Mixed**: Some docstrings are in English

### Configuration
- API keys and config values are read from an external JSON file using `get_value_from_json_file()` — never hardcoded in the notebook
- The OpenAI client is created as `client = openai.OpenAI(api_key=...)`

### Coding patterns
- Functions always check current state before modifying (e.g. `update_assistant` reads existing attributes first)
- File operations return two lists: `uploaded_files` and `not_uploaded_files`
- DataFrames (pandas) are used for structured listing of files and assistants
- Error handling uses `try/except` with descriptive `ImportError` messages for missing dependencies

### OpenAI API version
- Uses the **beta Assistants API** (`client.beta.assistants`, `client.beta.threads`)
- Default model: `gpt-4-1106-preview`
- Tool types used: `retrieval` and `code_interpreter`

---

---

## LLM_Client — Multi-Provider Script

`LLM_Client/llm_client.py` sends a **system prompt**, **context prompt**, and **task prompt** to one of three LLM providers via a unified interface. All keys and settings come from a JSON config file.

### Supported Providers

| Provider | SDK | Install |
|---|---|---|
| `openai` | `openai` | `pip install openai` |
| `claude` | `anthropic` | `pip install anthropic` |
| `gemini` | `google-generativeai` | `pip install google-generativeai` |

### Setup

```bash
cp LLM_Client/config.template.json LLM_Client/config.json
# Edit config.json and fill in your API keys
```

`config.json` is excluded from git via `.gitignore`.

### Config file structure

```json
{
  "default_provider": "openai",
  "providers": {
    "openai":  { "api_key": "sk-...",     "model": "gpt-4o" },
    "claude":  { "api_key": "sk-ant-...", "model": "claude-sonnet-4-6" },
    "gemini":  { "api_key": "AIza...",    "model": "gemini-2.0-flash" }
  },
  "prompts": {
    "system":  "You are a helpful assistant.",
    "context": "Optional background information or document content.",
    "task":    "Summarize the context in three bullet points."
  }
}
```

### Running

```bash
# Use the default_provider from config
python LLM_Client/llm_client.py --config LLM_Client/config.json

# Override provider at runtime
python LLM_Client/llm_client.py --config LLM_Client/config.json --provider claude

# Override provider and model
python LLM_Client/llm_client.py --config LLM_Client/config.json --provider gemini --model gemini-2.0-pro
```

### Prompt flow

The three prompts are mapped to API roles as follows:

| Prompt | OpenAI role | Claude param | Gemini |
|---|---|---|---|
| `system` | `system` message | `system=` parameter | `system_instruction=` |
| `context` | `user` turn (followed by a brief assistant ack) | same | prepended to user content |
| `task` | final `user` turn | final `user` turn | appended to user content |

If `context` is empty, it is skipped entirely.

### Architecture

- `load_config(path)` — reads JSON config
- `get_nested(data, "a.b.c")` — dot-path accessor
- `OpenAIProvider`, `ClaudeProvider`, `GeminiProvider` — each has a `.send(system, context, task) → str` method
- `build_provider(name, config, model_override)` — factory that instantiates the right class
- `main()` — CLI entry point with `argparse`

---

## Development Workflow

### Prerequisites
```bash
pip install openai pandas openpyxl pprint
```

### Running the notebook
```bash
jupyter notebook Assistant_AI/Assistant_AI.ipynb
```
or
```bash
jupyter lab
```

### Typical workflow
1. Configure your OpenAI API key in a JSON config file
2. Run **Section 0** to initialize the client
3. Run **Section 1** to upload knowledge base files
4. Run **Section 2** to create/configure an assistant
5. Run **Section 3** to start a conversation thread

### Git branches
- `master` / `main` — stable branch
- `claude/...` — AI-generated feature/documentation branches

---

## Things to Watch Out For

- The `retrieval` tool type used in this notebook corresponds to the older Assistants API v1. In newer versions of the OpenAI API, `retrieval` was renamed to `file_search`. If upgrading, update the tool type string in `create_assistant()`.
- `client.beta.assistants.list(limit="20")` — the `limit` is passed as a string; newer SDK versions may require an integer.
- The polling loop in Section 3.4 uses `time.sleep(10)` which can be slow. Consider using exponential backoff or the SDK's built-in `poll()` methods in newer versions.
- No authentication or secrets should be committed — always store the API key in a config file excluded from git (add to `.gitignore` if not already).
