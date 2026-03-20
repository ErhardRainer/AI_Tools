"""
Tests für KimiProvider — Moonshot AI (platform.moonshot.cn)
Modelle: kimi-k2, moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k, ...
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _mock_openai(reply: str = "Test-Antwort von Kimi"):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = reply
    mock_client.chat.completions.create.return_value = mock_response

    mock_module = MagicMock()
    mock_module.OpenAI.return_value = mock_client
    return mock_module, mock_client


class TestKimiProvider(unittest.TestCase):

    def test_default_model(self):
        from llm_client import KimiProvider
        mock_module, _ = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = KimiProvider(api_key="sk-kimi-test")
        self.assertEqual(provider.model, "kimi-k2")

    def test_custom_model_moonshot_128k(self):
        from llm_client import KimiProvider
        mock_module, _ = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = KimiProvider(api_key="sk-kimi-test", model="moonshot-v1-128k")
        self.assertEqual(provider.model, "moonshot-v1-128k")

    def test_uses_moonshot_base_url(self):
        """KimiProvider muss api.moonshot.cn/v1 als base_url verwenden."""
        from llm_client import KimiProvider
        mock_module, _ = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            KimiProvider(api_key="sk-kimi-test")
        _, kwargs = mock_module.OpenAI.call_args
        self.assertEqual(kwargs["base_url"], "https://api.moonshot.cn/v1")

    def test_send_returns_response(self):
        from llm_client import KimiProvider
        mock_module, _ = _mock_openai("Kimi K2 Antwort")
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = KimiProvider(api_key="sk-kimi-test")
            result = provider.send("System", "Kontext", "Task")
        self.assertEqual(result, "Kimi K2 Antwort")

    def test_send_with_context_builds_correct_message_roles(self):
        from llm_client import KimiProvider
        mock_module, mock_client = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = KimiProvider(api_key="sk-kimi-test")
            provider.send("System", "Kontext vorhanden", "Aufgabe")

        messages = mock_client.chat.completions.create.call_args[1]["messages"]
        roles = [m["role"] for m in messages]
        self.assertEqual(roles, ["system", "user", "assistant", "user"])

    def test_send_without_context_skips_ack(self):
        from llm_client import KimiProvider
        mock_module, mock_client = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = KimiProvider(api_key="sk-kimi-test")
            provider.send("System", "   ", "Task")

        messages = mock_client.chat.completions.create.call_args[1]["messages"]
        roles = [m["role"] for m in messages]
        self.assertEqual(roles, ["system", "user"])

    def test_send_uses_correct_model_in_api_call(self):
        from llm_client import KimiProvider
        mock_module, mock_client = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = KimiProvider(api_key="sk-kimi-test", model="moonshot-v1-32k")
            provider.send("System", "", "Task")

        call_kwargs = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs["model"], "moonshot-v1-32k")


if __name__ == "__main__":
    unittest.main()
