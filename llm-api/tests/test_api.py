"""
Tests für die LLM API.

Keine echten API-Calls — build_provider wird gemockt,
load_config liest eine temporäre Test-Config.
"""

import importlib
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Test-Config als temporäre Datei bereitstellen, damit api.py beim Import
# load_config() erfolgreich aufrufen kann.
# ---------------------------------------------------------------------------

TEST_CONFIG = {
    "default_provider": "openai",
    "providers": {
        "openai":   {"api_key": "sk-test",      "model": "gpt-4o"},
        "grok":     {"api_key": "xai-test",     "model": "grok-3"},
        "deepseek": {"api_key": "sk-ds-test",   "model": "deepseek-chat"},
    },
    "presets": {
        "fast": {"provider": "grok", "model": "grok-3-mini"},
    },
}

# Temp-Datei anlegen und LLM_CONFIG setzen, bevor api.py geladen wird
_tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
json.dump(TEST_CONFIG, _tmp)
_tmp.close()
os.environ["LLM_CONFIG"] = _tmp.name

# LLM_Client (Repo-Root) und api.py (llm-api/) in den Suchpfad aufnehmen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import api  # noqa: E402  (muss nach env-Setup importiert werden)
from fastapi.testclient import TestClient  # noqa: E402

client = TestClient(api.app)

# ---------------------------------------------------------------------------
# Hilfsfunktion: Mock-Provider zurückgeben
# ---------------------------------------------------------------------------

def _make_mock_provider(response_text: str = "Test-Antwort", model: str = "gpt-4o") -> MagicMock:
    mock = MagicMock()
    mock.model = model
    mock.send.return_value = response_text
    return mock


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

class TestHealth(unittest.TestCase):

    def test_returns_ok(self):
        resp = client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"status": "ok"})


# ---------------------------------------------------------------------------
# /providers
# ---------------------------------------------------------------------------

class TestProviders(unittest.TestCase):

    def test_returns_200(self):
        resp = client.get("/providers")
        self.assertEqual(resp.status_code, 200)

    def test_contains_provider_list(self):
        resp = client.get("/providers")
        data = resp.json()
        self.assertIn("providers", data)
        self.assertIsInstance(data["providers"], list)
        self.assertIn("openai", data["providers"])

    def test_contains_presets(self):
        resp = client.get("/providers")
        data = resp.json()
        self.assertIn("presets", data)
        self.assertIn("fast", data["presets"])

    def test_contains_default_provider(self):
        resp = client.get("/providers")
        data = resp.json()
        self.assertIn("default_provider", data)


# ---------------------------------------------------------------------------
# POST /chat — Happy Paths
# ---------------------------------------------------------------------------

class TestChatSuccess(unittest.TestCase):

    def test_basic_chat(self):
        mock = _make_mock_provider("Hallo Welt")
        with patch("api.build_provider", return_value=mock):
            resp = client.post("/chat", json={
                "provider": "openai",
                "system": "Du bist ein Assistent.",
                "task": "Sag Hallo.",
            })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["response"], "Hallo Welt")
        self.assertEqual(data["provider"], "openai")

    def test_model_override(self):
        mock = _make_mock_provider(model="gpt-4o-mini")
        with patch("api.build_provider", return_value=mock) as bp:
            client.post("/chat", json={
                "provider": "openai",
                "model": "gpt-4o-mini",
                "system": "S",
                "task": "T",
            })
        _, kwargs = bp.call_args
        self.assertEqual(kwargs.get("model_override") or bp.call_args[0][2], "gpt-4o-mini")

    def test_default_provider_used_when_no_provider_given(self):
        mock = _make_mock_provider()
        with patch("api.build_provider", return_value=mock) as bp:
            resp = client.post("/chat", json={
                "system": "S",
                "task": "T",
            })
        self.assertEqual(resp.status_code, 200)
        called_provider = bp.call_args[0][0]
        self.assertEqual(called_provider, "openai")  # default_provider aus TEST_CONFIG

    def test_preset_resolves_provider(self):
        mock = _make_mock_provider(model="grok-3-mini")
        with patch("api.build_provider", return_value=mock) as bp:
            resp = client.post("/chat", json={
                "preset": "fast",
                "system": "S",
                "task": "T",
            })
        self.assertEqual(resp.status_code, 200)
        called_provider = bp.call_args[0][0]
        self.assertEqual(called_provider, "grok")

    def test_output_format_json_extracts_json(self):
        mock = _make_mock_provider('Text davor\n```json\n{"x": 1}\n```\nText danach')
        with patch("api.build_provider", return_value=mock):
            resp = client.post("/chat", json={
                "provider": "openai",
                "system": "S",
                "task": "T",
                "output_format": "json",
            })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["response"], '{"x": 1}')

    def test_context_passed_to_provider(self):
        mock = _make_mock_provider()
        with patch("api.build_provider", return_value=mock):
            client.post("/chat", json={
                "provider": "openai",
                "system": "S",
                "context": "Kontext-Text",
                "task": "T",
            })
        mock.send.assert_called_once_with(
            system="S", context="Kontext-Text", task="T"
        )


# ---------------------------------------------------------------------------
# POST /chat — Fehlerfälle
# ---------------------------------------------------------------------------

class TestChatErrors(unittest.TestCase):

    def test_unknown_preset_returns_400(self):
        resp = client.post("/chat", json={
            "preset": "unbekannt_xyz",
            "system": "S",
            "task": "T",
        })
        self.assertEqual(resp.status_code, 400)
        self.assertIn("unbekannt_xyz", resp.json()["detail"])

    def test_invalid_provider_returns_400(self):
        with patch("api.build_provider", side_effect=ValueError("Unbekannter Provider")):
            resp = client.post("/chat", json={
                "provider": "nicht_vorhanden",
                "system": "S",
                "task": "T",
            })
        self.assertEqual(resp.status_code, 400)

    def test_provider_send_error_returns_502(self):
        mock = _make_mock_provider()
        mock.send.side_effect = RuntimeError("API nicht erreichbar")
        with patch("api.build_provider", return_value=mock):
            resp = client.post("/chat", json={
                "provider": "openai",
                "system": "S",
                "task": "T",
            })
        self.assertEqual(resp.status_code, 502)

    def test_output_format_json_no_json_returns_422(self):
        mock = _make_mock_provider("Hier ist kein JSON, nur Text.")
        with patch("api.build_provider", return_value=mock):
            resp = client.post("/chat", json={
                "provider": "openai",
                "system": "S",
                "task": "T",
                "output_format": "json",
            })
        self.assertEqual(resp.status_code, 422)

    def test_missing_task_returns_422(self):
        resp = client.post("/chat", json={
            "provider": "openai",
            "system": "S",
            # task fehlt
        })
        self.assertEqual(resp.status_code, 422)

    def test_missing_system_returns_422(self):
        resp = client.post("/chat", json={
            "provider": "openai",
            # system fehlt
            "task": "T",
        })
        self.assertEqual(resp.status_code, 422)


# ---------------------------------------------------------------------------
# Authentifizierung
# ---------------------------------------------------------------------------

class TestAuthentication(unittest.TestCase):

    def setUp(self):
        # API_KEY temporär setzen
        api.API_KEY = "test-secret-key"

    def tearDown(self):
        api.API_KEY = ""

    def test_no_key_returns_401(self):
        resp = client.post("/chat", json={"provider": "openai", "system": "S", "task": "T"})
        self.assertEqual(resp.status_code, 401)

    def test_wrong_key_returns_401(self):
        resp = client.post(
            "/chat",
            json={"provider": "openai", "system": "S", "task": "T"},
            headers={"X-API-Key": "falscher-key"},
        )
        self.assertEqual(resp.status_code, 401)

    def test_correct_key_passes(self):
        mock = _make_mock_provider()
        with patch("api.build_provider", return_value=mock):
            resp = client.post(
                "/chat",
                json={"provider": "openai", "system": "S", "task": "T"},
                headers={"X-API-Key": "test-secret-key"},
            )
        self.assertEqual(resp.status_code, 200)

    def test_health_requires_no_key(self):
        # /health soll immer erreichbar sein, auch ohne Auth
        resp = client.get("/health")
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# Aufräumen
# ---------------------------------------------------------------------------

def tearDownModule():
    os.unlink(_tmp.name)


if __name__ == "__main__":
    unittest.main()
