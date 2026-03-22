"""
Tests für set_api_key() und set_default_model().

Alle Tests verwenden temporäre Dateien — keine echten config.json werden angefasst.
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import llm_client


def _make_config(tmp_dir: str, data: dict) -> str:
    """Schreibt ein dict als JSON in eine temporäre Datei und gibt den Pfad zurück."""
    path = os.path.join(tmp_dir, "config.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return path


def _read_config(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# set_api_key
# ---------------------------------------------------------------------------

class TestSetApiKey(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_sets_key_for_existing_provider(self):
        path = _make_config(self.tmp, {
            "providers": {"openai": {"api_key": "old-key", "model": "gpt-4o"}}
        })
        llm_client.set_api_key("openai", "sk-new", path)
        cfg = _read_config(path)
        self.assertEqual(cfg["providers"]["openai"]["api_key"], "sk-new")

    def test_preserves_existing_model_field(self):
        path = _make_config(self.tmp, {
            "providers": {"openai": {"api_key": "old", "model": "gpt-4o"}}
        })
        llm_client.set_api_key("openai", "sk-new", path)
        cfg = _read_config(path)
        self.assertEqual(cfg["providers"]["openai"]["model"], "gpt-4o")

    def test_creates_provider_if_missing(self):
        path = _make_config(self.tmp, {"providers": {}})
        llm_client.set_api_key("claude", "sk-ant-abc", path)
        cfg = _read_config(path)
        self.assertEqual(cfg["providers"]["claude"]["api_key"], "sk-ant-abc")

    def test_creates_providers_section_if_missing(self):
        path = _make_config(self.tmp, {})
        llm_client.set_api_key("grok", "xai-123", path)
        cfg = _read_config(path)
        self.assertEqual(cfg["providers"]["grok"]["api_key"], "xai-123")

    def test_preserves_other_providers(self):
        path = _make_config(self.tmp, {
            "providers": {
                "openai": {"api_key": "sk-openai", "model": "gpt-4o"},
                "claude": {"api_key": "sk-claude", "model": "claude-sonnet-4-6"},
            }
        })
        llm_client.set_api_key("openai", "sk-updated", path)
        cfg = _read_config(path)
        self.assertEqual(cfg["providers"]["claude"]["api_key"], "sk-claude")

    def test_preserves_prompts_section(self):
        path = _make_config(self.tmp, {
            "providers": {"openai": {"api_key": "old"}},
            "prompts": {"system": "Du bist ein Assistent.", "task": "Hilf mir."},
        })
        llm_client.set_api_key("openai", "sk-new", path)
        cfg = _read_config(path)
        self.assertEqual(cfg["prompts"]["system"], "Du bist ein Assistent.")

    def test_writes_valid_json(self):
        path = _make_config(self.tmp, {"providers": {}})
        llm_client.set_api_key("deepseek", "sk-ds", path)
        # Kein Fehler beim Einlesen = valides JSON
        cfg = _read_config(path)
        self.assertIsInstance(cfg, dict)

    def test_raises_for_missing_config_file(self):
        with self.assertRaises(FileNotFoundError):
            llm_client.set_api_key("openai", "sk-x", "/nonexistent/config.json")

    def test_raises_for_empty_provider(self):
        path = _make_config(self.tmp, {})
        with self.assertRaises(ValueError):
            llm_client.set_api_key("", "sk-x", path)

    def test_raises_for_empty_api_key(self):
        path = _make_config(self.tmp, {})
        with self.assertRaises(ValueError):
            llm_client.set_api_key("openai", "", path)

    def test_multiple_calls_accumulate(self):
        path = _make_config(self.tmp, {})
        llm_client.set_api_key("openai", "sk-o", path)
        llm_client.set_api_key("claude", "sk-c", path)
        cfg = _read_config(path)
        self.assertEqual(cfg["providers"]["openai"]["api_key"], "sk-o")
        self.assertEqual(cfg["providers"]["claude"]["api_key"], "sk-c")


# ---------------------------------------------------------------------------
# set_default_model
# ---------------------------------------------------------------------------

class TestSetDefaultModel(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_sets_model_for_existing_provider(self):
        path = _make_config(self.tmp, {
            "providers": {"openai": {"api_key": "sk-x", "model": "gpt-4o"}}
        })
        llm_client.set_default_model("openai", "gpt-4o-mini", path)
        cfg = _read_config(path)
        self.assertEqual(cfg["providers"]["openai"]["model"], "gpt-4o-mini")

    def test_preserves_api_key(self):
        path = _make_config(self.tmp, {
            "providers": {"openai": {"api_key": "sk-keep", "model": "gpt-4o"}}
        })
        llm_client.set_default_model("openai", "gpt-4o-mini", path)
        cfg = _read_config(path)
        self.assertEqual(cfg["providers"]["openai"]["api_key"], "sk-keep")

    def test_creates_provider_if_missing(self):
        path = _make_config(self.tmp, {"providers": {}})
        llm_client.set_default_model("deepseek", "deepseek-reasoner", path)
        cfg = _read_config(path)
        self.assertEqual(cfg["providers"]["deepseek"]["model"], "deepseek-reasoner")

    def test_creates_providers_section_if_missing(self):
        path = _make_config(self.tmp, {})
        llm_client.set_default_model("groq", "gemma2-9b-it", path)
        cfg = _read_config(path)
        self.assertEqual(cfg["providers"]["groq"]["model"], "gemma2-9b-it")

    def test_preserves_other_providers(self):
        path = _make_config(self.tmp, {
            "providers": {
                "openai":  {"api_key": "sk-o", "model": "gpt-4o"},
                "mistral": {"api_key": "sk-m", "model": "mistral-large-latest"},
            }
        })
        llm_client.set_default_model("openai", "gpt-4o-mini", path)
        cfg = _read_config(path)
        self.assertEqual(cfg["providers"]["mistral"]["model"], "mistral-large-latest")

    def test_raises_for_missing_config_file(self):
        with self.assertRaises(FileNotFoundError):
            llm_client.set_default_model("openai", "gpt-4o", "/no/such/file.json")

    def test_raises_for_empty_provider(self):
        path = _make_config(self.tmp, {})
        with self.assertRaises(ValueError):
            llm_client.set_default_model("", "gpt-4o", path)

    def test_raises_for_empty_model(self):
        path = _make_config(self.tmp, {})
        with self.assertRaises(ValueError):
            llm_client.set_default_model("openai", "", path)

    def test_set_api_key_and_model_independently(self):
        """set_api_key und set_default_model können unabhängig kombiniert werden."""
        path = _make_config(self.tmp, {})
        llm_client.set_api_key("kimi", "sk-kimi", path)
        llm_client.set_default_model("kimi", "moonshot-v1-128k", path)
        cfg = _read_config(path)
        self.assertEqual(cfg["providers"]["kimi"]["api_key"], "sk-kimi")
        self.assertEqual(cfg["providers"]["kimi"]["model"], "moonshot-v1-128k")


if __name__ == "__main__":
    unittest.main()
