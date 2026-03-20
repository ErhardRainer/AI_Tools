"""
Tests für Hilfsfunktionen: load_config, get_nested, build_provider.
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from llm_client import get_nested, load_config, build_provider, PROVIDERS


def _all_sdk_mocks():
    """Gibt ein sys.modules-Patch-Dict zurück, das alle benötigten SDKs mockt."""
    mock_openai = MagicMock()
    mock_openai.OpenAI.return_value = MagicMock()

    mock_anthropic = MagicMock()
    mock_anthropic.Anthropic.return_value = MagicMock()

    mock_genai = MagicMock()
    mock_google = MagicMock()
    mock_google.generativeai = mock_genai

    return {
        "openai": mock_openai,
        "anthropic": mock_anthropic,
        "google": mock_google,
        "google.generativeai": mock_genai,
    }


BASE_CONFIG = {
    "providers": {
        "openai":   {"api_key": "sk-test",      "model": "gpt-4o"},
        "claude":   {"api_key": "sk-ant-test",  "model": "claude-sonnet-4-6"},
        "gemini":   {"api_key": "AIza-test",    "model": "gemini-2.0-flash"},
        "grok":     {"api_key": "xai-test",     "model": "grok-3"},
        "kimi":     {"api_key": "sk-kimi-test", "model": "kimi-k2"},
        "deepseek": {"api_key": "sk-ds-test",   "model": "deepseek-chat"},
        "groq":     {"api_key": "gsk_test",     "model": "llama-3.3-70b-versatile"},
        "mistral":  {"api_key": "mist-test",    "model": "mistral-large-latest"},
    }
}


class TestGetNested(unittest.TestCase):

    def test_top_level_key(self):
        self.assertEqual(get_nested({"a": 1}, "a"), 1)

    def test_nested_key(self):
        self.assertEqual(get_nested({"a": {"b": {"c": 42}}}, "a.b.c"), 42)

    def test_missing_key_returns_none(self):
        self.assertIsNone(get_nested({"a": 1}, "b"))

    def test_missing_key_custom_default(self):
        self.assertEqual(get_nested({}, "x.y", default="fallback"), "fallback")

    def test_non_dict_intermediate(self):
        self.assertIsNone(get_nested({"a": "string"}, "a.b"))


class TestLoadConfig(unittest.TestCase):

    def test_loads_valid_json(self):
        data = {"key": "value", "nested": {"x": 1}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = f.name
        try:
            result = load_config(path)
            self.assertEqual(result, data)
        finally:
            os.unlink(path)

    def test_raises_for_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            load_config("/nonexistent/path/config.json")


class TestBuildProvider(unittest.TestCase):

    def test_all_providers_registered(self):
        expected = {"openai", "claude", "gemini", "grok", "kimi", "deepseek", "groq", "mistral"}
        self.assertEqual(set(PROVIDERS.keys()), expected)

    def test_unknown_provider_raises(self):
        with self.assertRaises(ValueError):
            build_provider("unknown_xyz", BASE_CONFIG)

    def test_missing_api_key_raises(self):
        with self.assertRaises(ValueError):
            build_provider("openai", {"providers": {"openai": {}}})

    def test_model_override_applied(self):
        with patch.dict(sys.modules, _all_sdk_mocks()):
            provider = build_provider("openai", BASE_CONFIG, model_override="gpt-4o-mini")
        self.assertEqual(provider.model, "gpt-4o-mini")

    def test_model_from_config_used_when_no_override(self):
        with patch.dict(sys.modules, _all_sdk_mocks()):
            provider = build_provider("grok", BASE_CONFIG)
        self.assertEqual(provider.model, "grok-3")

    def test_build_all_providers_without_error(self):
        with patch.dict(sys.modules, _all_sdk_mocks()):
            for name in PROVIDERS:
                with self.subTest(provider=name):
                    provider = build_provider(name, BASE_CONFIG)
                    self.assertIsNotNone(provider)


if __name__ == "__main__":
    unittest.main()
