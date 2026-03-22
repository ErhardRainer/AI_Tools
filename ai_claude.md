# Anthropic Claude

[Zurück zur Übersicht](README.md)

**Unternehmen:** Anthropic (San Francisco, USA)
**Gegründet:** 2021 (von ehemaligen OpenAI-Mitarbeitern)
**API-Konsole:** console.anthropic.com
**Preisübersicht:** anthropic.com/pricing
**Dokumentation:** docs.anthropic.com
**Status:** status.anthropic.com

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2026-02-17 | **Claude Sonnet 4.6** veröffentlicht — nah an Opus-Niveau, gleiches Preisniveau wie Sonnet 4.5 |
| 2026-02-05 | **Claude Opus 4.6** veröffentlicht — 1M-Kontext, stärkstes Claude-Modell |
| 2025-11-24 | **Claude Opus 4.5** veröffentlicht |
| 2025-10-15 | **Claude Haiku 4.5** veröffentlicht — schnellstes Modell |
| 2025-05-22 | **Claude 4** (Opus 4 und Sonnet 4) veröffentlicht |
| 2024-10-22 | **Claude 3.5 Sonnet v2** — „Computer Use" (Beta) |
| 2024-06-20 | **Claude 3.5 Sonnet** veröffentlicht |
| 2024-03-04 | **Claude 3** Familie: Opus, Sonnet, Haiku |
| 2023-07 | **Claude 2** veröffentlicht |
| 2023-03 | **Claude 1** veröffentlicht |

---

## Aktuelle Modelle (März 2026)

| Modell | Typ | Kontext | Input-Preis | Output-Preis | Besonderheiten |
|---|---|---|---|---|---|
| `claude-opus-4-6` | Flaggschiff | 1M | $5.00/1M | $25.00/1M | Stärkstes Modell, Deep Reasoning, 1M-Kontext |
| `claude-sonnet-4-6` | Ausgewogen | 1M | $3.00/1M | $15.00/1M | Bestes Preis-Leistungs-Verhältnis, nah an Opus |
| `claude-haiku-4-5-20251001` | Schnell | 200k | $1.00/1M | $5.00/1M | Schnellstes Modell, günstig, Echtzeit-Anwendungen |

### Long-Context-Preise (Sonnet 4.6)

| Kontext-Länge | Input | Output |
|---|---|---|
| ≤ 200k Token | $3.00/1M | $15.00/1M |
| > 200k Token | $6.00/1M | $22.50/1M |

### Kosten-Optimierung

- **Batch-Verarbeitung:** 50% Rabatt auf Input und Output
- **Prompt Caching:** Wiederkehrende Kontextteile cachen → bis zu 90% günstiger

---

## API-Besonderheiten

- **1M-Kontext:** Opus 4.6 und Sonnet 4.6 unterstützen 1 Million Token — genug für ganze Dokumentensammlungen
- **System-Prompt als Parameter:** `system=` statt als Message-Rolle — architektonisch sauberer
- **Extended Thinking:** Opus und Sonnet können ihren Denkprozess sichtbar machen
- **Tool Use:** Natives Function Calling mit JSON-Schema
- **Vision:** Bilder analysieren (alle Modelle)
- **Computer Use (Beta):** Claude kann Desktop-Anwendungen über Screenshots steuern
- **Constitutional AI:** Sicherheitsansatz durch Selbstkorrektur gegen eigene Prinzipien

## Authentifizierung

```python
import anthropic
client = anthropic.Anthropic(api_key="sk-ant-...")
```

## Typischer API-Aufruf

```python
import anthropic

client = anthropic.Anthropic(api_key="sk-ant-...")

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="Du bist ein hilfreicher Assistent.",
    messages=[
        {"role": "user", "content": "Erkläre Quantencomputing in drei Sätzen."}
    ]
)
print(message.content[0].text)
```

---

## Claude-Produkte

| Produkt | Beschreibung |
|---|---|
| **Claude.ai** | Web-Chat-Interface (kostenlos + Pro $20/Monat) |
| **Claude Code** | CLI-basierter Coding-Agent, 80.9% SWE-bench, ~4% aller GitHub-Commits |
| **Claude Agent SDK** | Python-SDK zum Bau eigener Agenten |
| **Claude for Enterprise** | Team-Verwaltung, SSO, Admin-Kontrollen |
| **Claude Artifacts** | Interaktive Code-/Visualisierungs-Ausgaben im Chat |

---

## Preisrechner-Tipp

Die aktuellen Preise ändern sich regelmäßig. Immer die offizielle Pricing-Seite prüfen:
anthropic.com/pricing
