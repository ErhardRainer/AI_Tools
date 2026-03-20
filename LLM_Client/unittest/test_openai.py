"""
Tests für OpenAIProvider — platform.openai.com
Modelle: gpt-4o, gpt-4o-mini, o3, o4-mini, ...
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _mock_openai(reply: str = "Test-Antwort von OpenAI"):
    """Gibt ein Mock-openai-Modul und den dazugehörigen mock_client zurück."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = reply
    mock_client.chat.completions.create.return_value = mock_response

    mock_module = MagicMock()
    mock_module.OpenAI.return_value = mock_client
    return mock_module, mock_client


class TestOpenAIProvider(unittest.TestCase):

    def _make_provider(self, model=None, reply="Test"):
        from llm_client import OpenAIProvider
        mock_module, mock_client = _mock_openai(reply)
        with patch.dict(sys.modules, {"openai": mock_module}):
            kwargs = {"api_key": "sk-test"}
            if model:
                kwargs["model"] = model
            provider = OpenAIProvider(**kwargs)
        provider._mock_client = mock_client
        return provider

    def test_default_model(self):
        provider = self._make_provider()
        self.assertEqual(provider.model, "gpt-4o")

    def test_custom_model(self):
        provider = self._make_provider(model="gpt-4o-mini")
        self.assertEqual(provider.model, "gpt-4o-mini")

    def test_send_returns_response(self):
        from llm_client import OpenAIProvider
        mock_module, mock_client = _mock_openai("Antwort von GPT-4o")
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = OpenAIProvider(api_key="sk-test")
            result = provider.send("System", "Kontext", "Task")
        self.assertEqual(result, "Antwort von GPT-4o")

    def test_send_with_context_adds_ack_message(self):
        from llm_client import OpenAIProvider
        mock_module, mock_client = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = OpenAIProvider(api_key="sk-test")
            provider.send("System", "Kontext vorhanden", "Task")

        messages = mock_client.chat.completions.create.call_args[1]["messages"]
        roles = [m["role"] for m in messages]
        self.assertEqual(roles, ["system", "user", "assistant", "user"])

    def test_send_without_context_skips_ack(self):
        from llm_client import OpenAIProvider
        mock_module, mock_client = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = OpenAIProvider(api_key="sk-test")
            provider.send("System", "", "Task ohne Kontext")

        messages = mock_client.chat.completions.create.call_args[1]["messages"]
        roles = [m["role"] for m in messages]
        self.assertEqual(roles, ["system", "user"])

    def test_system_prompt_is_first_message(self):
        from llm_client import OpenAIProvider
        mock_module, mock_client = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = OpenAIProvider(api_key="sk-test")
            provider.send("Mein System-Prompt", "", "Task")

        messages = mock_client.chat.completions.create.call_args[1]["messages"]
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[0]["content"], "Mein System-Prompt")


if __name__ == "__main__":
    unittest.main()
