"""
Tests für MistralProvider — Mistral AI (console.mistral.ai)
Modelle: mistral-large-latest, mistral-small-latest, codestral-latest, open-mixtral-8x22b, ...
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _mock_openai(reply: str = "Test-Antwort von Mistral"):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = reply
    mock_client.chat.completions.create.return_value = mock_response

    mock_module = MagicMock()
    mock_module.OpenAI.return_value = mock_client
    return mock_module, mock_client


class TestMistralProvider(unittest.TestCase):

    def test_default_model(self):
        from llm_client import MistralProvider
        mock_module, _ = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = MistralProvider(api_key="mist-test")
        self.assertEqual(provider.model, "mistral-large-latest")

    def test_custom_model_codestral(self):
        from llm_client import MistralProvider
        mock_module, _ = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = MistralProvider(api_key="mist-test", model="codestral-latest")
        self.assertEqual(provider.model, "codestral-latest")

    def test_uses_mistral_base_url(self):
        """MistralProvider muss api.mistral.ai/v1 als base_url verwenden."""
        from llm_client import MistralProvider
        mock_module, _ = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            MistralProvider(api_key="mist-test")
        _, kwargs = mock_module.OpenAI.call_args
        self.assertEqual(kwargs["base_url"], "https://api.mistral.ai/v1")

    def test_send_returns_response(self):
        from llm_client import MistralProvider
        mock_module, _ = _mock_openai("Mistral Large Antwort")
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = MistralProvider(api_key="mist-test")
            result = provider.send("System", "Kontext", "Task")
        self.assertEqual(result, "Mistral Large Antwort")

    def test_send_with_context_builds_correct_message_roles(self):
        from llm_client import MistralProvider
        mock_module, mock_client = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = MistralProvider(api_key="mist-test")
            provider.send("System", "Kontext vorhanden", "Task")

        messages = mock_client.chat.completions.create.call_args[1]["messages"]
        roles = [m["role"] for m in messages]
        self.assertEqual(roles, ["system", "user", "assistant", "user"])

    def test_send_without_context_skips_ack(self):
        from llm_client import MistralProvider
        mock_module, mock_client = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = MistralProvider(api_key="mist-test")
            provider.send("System", "", "Task ohne Kontext")

        messages = mock_client.chat.completions.create.call_args[1]["messages"]
        roles = [m["role"] for m in messages]
        self.assertEqual(roles, ["system", "user"])

    def test_small_model(self):
        from llm_client import MistralProvider
        mock_module, _ = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = MistralProvider(api_key="mist-test", model="mistral-small-latest")
        self.assertEqual(provider.model, "mistral-small-latest")


if __name__ == "__main__":
    unittest.main()
