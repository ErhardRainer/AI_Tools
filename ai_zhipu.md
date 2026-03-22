# Zhipu AI — GLM

[Zurück zur Übersicht](README.md)

**Unternehmen:** Zhipu AI (Beijing, China)
**Gegründet:** 2019 (Spin-off der Tsinghua University)
**API-Konsole:** open.bigmodel.cn
**Dokumentation:** open.bigmodel.cn/dev/api

---

## News / Änderungsprotokoll

| Datum | Änderung |
|---|---|
| 2025-01 | GLM-4-Plus mit verbessertem Reasoning |
| 2024-06 | GLM-4 allgemein verfügbar — konkurriert mit GPT-4 |
| 2024-01 | GLM-4 veröffentlicht mit Vision-Fähigkeiten |

---

## Aktuelle Modelle

| Modell | Typ | Kontext | Besonderheiten |
|---|---|---|---|
| `glm-4-plus` | Flaggschiff | 128k | Stärkstes GLM-Modell |
| `glm-4` | Standard | 128k | Ausgewogene Variante |
| `glm-4-flash` | Schnell | 128k | Kostenlose Stufe verfügbar |
| `glm-4v-plus` | Vision | 8k | Multimodal (Text + Bild) |

---

## Besonderheiten

- **ChatGLM-Erbe:** Aufgebaut auf der ChatGLM-Forschung der Tsinghua University
- **Vision-fähig:** GLM-4V kann Bilder analysieren
- **Code Interpreter:** Serverseitige Code-Ausführung
- **Web Search:** Integrierter Webzugriff
- **Kostenlose Stufe:** GLM-4-Flash ist kostenlos nutzbar
- **Open-Weight-Varianten:** ChatGLM-6B auf Hugging Face verfügbar

## Authentifizierung

```python
from zhipuai import ZhipuAI

client = ZhipuAI(api_key="...")
```

## Typischer API-Aufruf

```python
from zhipuai import ZhipuAI

client = ZhipuAI(api_key="...")

response = client.chat.completions.create(
    model="glm-4-plus",
    messages=[
        {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
        {"role": "user", "content": "Erkläre Quantencomputing in drei Sätzen."}
    ]
)
print(response.choices[0].message.content)
```
