# run_output.ps1 — Beispiele für die Ausgabe-Optionen des LLM Client
#
# Zeigt alle vier Ausgabe-Modi:
#   a) Datei mit Header      --output DATEI --output-format header   (Standard)
#   b) Datei ohne Header     --output DATEI --output-format plain
#   c) Nur Konsole           kein --output   (bisheriges Verhalten)
#   d) JSON extrahieren      --output-format json   (nur sinnvoll wenn Modell JSON liefern soll)
#
# Die Konsolenausgabe (Provider, Model, System, Context, Task, Response)
# erscheint in allen Modi — --output schreibt zusätzlich in die Datei.

$Config   = "$PSScriptRoot\..\config.json"
$Provider = "openai"
$Model    = "gpt-4o"

# ---------------------------------------------------------------------------
# a) Ausgabe in Datei MIT Header (Standard-Format)
#    Datei enthält: Provider, Model, System, Context, Task, Trennlinie, Response
# ---------------------------------------------------------------------------
python "$PSScriptRoot\..\llm_client.py" `
    --config $Config `
    --provider $Provider `
    --model $Model `
    --output "output_with_header.txt" `
    --output-format header

# ---------------------------------------------------------------------------
# b) Ausgabe in Datei OHNE Header (nur der Antwort-Text)
#    Nützlich wenn die Antwort direkt weiterverarbeitet werden soll
# ---------------------------------------------------------------------------
python "$PSScriptRoot\..\llm_client.py" `
    --config $Config `
    --provider $Provider `
    --model $Model `
    --output "output_plain.txt" `
    --output-format plain

# ---------------------------------------------------------------------------
# c) Nur Konsolenausgabe — kein --output-Flag, wie bisher
# ---------------------------------------------------------------------------
python "$PSScriptRoot\..\llm_client.py" `
    --config $Config `
    --provider $Provider `
    --model $Model

# ---------------------------------------------------------------------------
# d) JSON-Modus: nur den extrahierten JSON-Block ausgeben / speichern
#    Nur sinnvoll wenn der Task das Modell explizit zu JSON-Ausgabe auffordert.
#    Alles außerhalb des JSON-Blocks (Erklärtext, Markdown-Wrapper) wird entfernt.
#
#    Ohne --output: extrahiertes JSON erscheint auf der Konsole
#    Mit --output:  extrahiertes JSON wird in die Datei geschrieben
# ---------------------------------------------------------------------------

# Nur auf Konsole ausgeben (kein --output):
# python "$PSScriptRoot\..\llm_client.py" `
#     --config $Config `
#     --provider $Provider `
#     --model $Model `
#     --output-format json

# In Datei schreiben:
# python "$PSScriptRoot\..\llm_client.py" `
#     --config $Config `
#     --provider $Provider `
#     --model $Model `
#     --output "output.json" `
#     --output-format json

# ---------------------------------------------------------------------------
# Als Python-Modul (alternativ zum direkten Script-Aufruf):
# ---------------------------------------------------------------------------
# python -m LLM_Client --config $Config --provider $Provider --output "out.txt" --output-format plain

# ---------------------------------------------------------------------------
# Als installiertes CLI (nach: pip install .):
# ---------------------------------------------------------------------------
# llm-client --config $Config --provider $Provider --output "out.txt" --output-format header

# ---------------------------------------------------------------------------
# Programmatisch: format_output und extract_json können auch direkt importiert werden
# ---------------------------------------------------------------------------
# from LLM_Client import extract_json, format_output
# json_text = extract_json(response)                         # wirft ValueError wenn kein JSON
# content   = format_output(response, header_lines, "json")  # gibt formatierten String zurück
