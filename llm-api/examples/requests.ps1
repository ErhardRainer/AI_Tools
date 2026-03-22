# requests.ps1 — Beispielaufrufe für die LLM API
#
# Voraussetzung: API läuft auf http://localhost:8000
#   docker compose -f llm-api/docker-compose.yml up
#   oder: uvicorn api:app --reload  (im llm-api/-Verzeichnis)
#
# Interaktive Doku: http://localhost:8000/docs

$Base = "http://localhost:8000"

# Optionaler API-Key (nur wenn API_KEY-Umgebungsvariable im Container gesetzt)
# $Headers = @{ "X-API-Key" = "dein-api-key" }
$Headers = @{}

# ---------------------------------------------------------------------------
# Health-Check
# ---------------------------------------------------------------------------

Invoke-RestMethod -Uri "$Base/health" -Method Get

# ---------------------------------------------------------------------------
# Verfügbare Provider und Presets anzeigen
# ---------------------------------------------------------------------------

Invoke-RestMethod -Uri "$Base/providers" -Method Get | ConvertTo-Json -Depth 5

# ---------------------------------------------------------------------------
# a) Einfacher Chat-Request (Standard-Provider aus config.json)
# ---------------------------------------------------------------------------

$Body = @{
    system  = "Du bist ein hilfreicher Assistent."
    context = ""
    task    = "Erkläre Quantencomputing in zwei Sätzen."
} | ConvertTo-Json

Invoke-RestMethod -Uri "$Base/chat" -Method Post `
    -ContentType "application/json" `
    -Headers $Headers `
    -Body $Body

# ---------------------------------------------------------------------------
# b) Provider explizit wählen
# ---------------------------------------------------------------------------

$Body = @{
    provider = "grok"
    system   = "Du bist ein Experte für Software-Architektur."
    task     = "Was sind die Vorteile von Microservices?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "$Base/chat" -Method Post `
    -ContentType "application/json" `
    -Headers $Headers `
    -Body $Body

# ---------------------------------------------------------------------------
# c) Provider und Modell überschreiben
# ---------------------------------------------------------------------------

$Body = @{
    provider = "openai"
    model    = "gpt-4o-mini"
    system   = "Du bist ein Python-Experte."
    task     = "Schreibe eine Funktion zum Prüfen ob eine Zahl prim ist."
} | ConvertTo-Json

Invoke-RestMethod -Uri "$Base/chat" -Method Post `
    -ContentType "application/json" `
    -Headers $Headers `
    -Body $Body

# ---------------------------------------------------------------------------
# d) Preset verwenden (aus config.json)
# ---------------------------------------------------------------------------

$Body = @{
    preset = "fast"
    system = "Du bist ein Assistent."
    task   = "Was ist die Hauptstadt von Frankreich?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "$Base/chat" -Method Post `
    -ContentType "application/json" `
    -Headers $Headers `
    -Body $Body

# ---------------------------------------------------------------------------
# e) JSON-Ausgabe extrahieren
#    Sinnvoll wenn das Modell explizit JSON liefern soll.
#    Alles außerhalb des JSON-Blocks wird weggeschnitten.
# ---------------------------------------------------------------------------

$Body = @{
    provider      = "openai"
    system        = "Antworte ausschließlich mit validem JSON, ohne Erklärungen."
    task          = 'Gib ein JSON-Objekt mit den Feldern "name", "sprache", "version" für Python zurück.'
    output_format = "json"
} | ConvertTo-Json

$Result = Invoke-RestMethod -Uri "$Base/chat" -Method Post `
    -ContentType "application/json" `
    -Headers $Headers `
    -Body $Body

# Antwort direkt als Objekt verwenden:
$JsonObj = $Result.response | ConvertFrom-Json
Write-Host "Name: $($JsonObj.name), Sprache: $($JsonObj.sprache)"

# ---------------------------------------------------------------------------
# f) Mit Kontext (z.B. Dokument-Inhalt)
# ---------------------------------------------------------------------------

$Dokument = Get-Content "mein_dokument.txt" -Raw  # eigene Datei einfügen

# $Body = @{
#     provider = "kimi"           # Kimi unterstützt sehr langen Kontext
#     model    = "moonshot-v1-128k"
#     system   = "Du bist ein Experte für Textzusammenfassungen."
#     context  = $Dokument
#     task     = "Fasse den Text in drei Stichpunkten zusammen."
# } | ConvertTo-Json -Depth 3
#
# Invoke-RestMethod -Uri "$Base/chat" -Method Post `
#     -ContentType "application/json" `
#     -Headers $Headers `
#     -Body $Body

# ---------------------------------------------------------------------------
# g) Authentifizierung mit API-Key (wenn API_KEY im Container gesetzt)
# ---------------------------------------------------------------------------

# $SecureHeaders = @{ "X-API-Key" = "dein-geheimer-schluessel" }
#
# Invoke-RestMethod -Uri "$Base/chat" -Method Post `
#     -ContentType "application/json" `
#     -Headers $SecureHeaders `
#     -Body ($Body)
