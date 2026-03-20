# run_url_fetch.ps1 — fetch_context_urls: URLs im Kontext automatisch abrufen
#
# fetch_context_urls() erkennt HTTP(S)-URLs im context-Feld via Regex und
# ersetzt sie durch den abgerufenen Inhalt (PDF, HTML oder Plaintext).
# Der LLM erhält so den echten Dokumentinhalt statt einer rohen URL.
#
# Voraussetzungen:
#   pip install requests               # Basis-HTTP
#   pip install pypdf                  # PDF-Unterstützung
#   pip install beautifulsoup4         # HTML-Bereinigung
# oder alle auf einmal:
#   pip install ".[url-fetch]"

$Config = "$PSScriptRoot\..\config.json"

# ---------------------------------------------------------------------------
# a) Via CLI: URL einer PDF-Datei im Kontext — wird automatisch abgerufen
# ---------------------------------------------------------------------------

python -m LLM_Client `
    --config $Config `
    --provider openai `
    --prompts-file "$PSScriptRoot\prompts_url_context.json"

# ---------------------------------------------------------------------------
# b) Direkt als Python-Modul — URL im Kontext programmatisch auflösen
# ---------------------------------------------------------------------------

# python -c "
# from LLM_Client import fetch_context_urls, build_provider, load_config
# config  = load_config('$Config')
# context = fetch_context_urls('https://example.com/report.pdf')
# provider = build_provider('openai', config)
# print(provider.send(
#     system  = 'Du bist ein Experte fuer Textzusammenfassungen.',
#     context = context,
#     task    = 'Fasse den Inhalt in 5 Stichpunkten zusammen.'
# ))
# "

# ---------------------------------------------------------------------------
# c) Mehrere URLs im Kontext (werden nacheinander aufgeloest)
# ---------------------------------------------------------------------------

# python -c "
# from LLM_Client import fetch_context_urls
# ctx = '''
# Dokument 1: https://example.com/report.pdf
# Webseite:   https://example.com/about.html
# Textdatei:  https://example.com/notes.txt
# '''
# print(fetch_context_urls(ctx))
# "

# ---------------------------------------------------------------------------
# d) Über die LLM-API (wenn llm-api läuft)
# ---------------------------------------------------------------------------

# curl -X POST http://localhost:8000/chat `
#   -H 'Content-Type: application/json' `
#   -d '{
#     "provider": "openai",
#     "system":   "Du bist ein Experte fuer Textzusammenfassungen.",
#     "context":  "Bitte analysiere https://example.com/report.pdf",
#     "task":     "Fasse den Inhalt in 5 Stichpunkten zusammen."
#   }'
# Die API ruft die PDF-URL automatisch ab und sendet den extrahierten Text ans Modell.
