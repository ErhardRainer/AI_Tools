"""
Tests für GrokProvider — xAI Grok (console.x.ai)
Modelle: grok-3, grok-3-mini, grok-3-fast, grok-2-1212, ...
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _mock_openai(reply: str = "Test-Antwort von Grok"):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = reply
    mock_client.chat.completions.create.return_value = mock_response

    mock_module = MagicMock()
    mock_module.OpenAI.return_value = mock_client
    return mock_module, mock_client


class TestGrokProvider(unittest.TestCase):

    def test_default_model(self):
        from llm_client import GrokProvider
        mock_module, _ = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = GrokProvider(api_key="xai-test")
        self.assertEqual(provider.model, "grok-3")

    def test_custom_model(self):
        from llm_client import GrokProvider
        mock_module, _ = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = GrokProvider(api_key="xai-test", model="grok-3-mini")
        self.assertEqual(provider.model, "grok-3-mini")

    def test_uses_xai_base_url(self):
        """GrokProvider muss api.x.ai/v1 als base_url verwenden."""
        from llm_client import GrokProvider
        mock_module, _ = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            GrokProvider(api_key="xai-test")
        _, kwargs = mock_module.OpenAI.call_args
        self.assertEqual(kwargs["base_url"], "https://api.x.ai/v1")

    def test_send_returns_response(self):
        from llm_client import GrokProvider
        mock_module, _ = _mock_openai("Antwort von Grok-3")
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = GrokProvider(api_key="xai-test")
            result = provider.send("System", "Kontext", "Task")
        self.assertEqual(result, "Antwort von Grok-3")

    def test_send_with_context_builds_correct_message_roles(self):
        from llm_client import GrokProvider
        mock_module, mock_client = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = GrokProvider(api_key="xai-test")
            provider.send("System", "Kontext", "Task")

        messages = mock_client.chat.completions.create.call_args[1]["messages"]
        roles = [m["role"] for m in messages]
        self.assertEqual(roles, ["system", "user", "assistant", "user"])

    def test_send_without_context_skips_ack(self):
        from llm_client import GrokProvider
        mock_module, mock_client = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = GrokProvider(api_key="xai-test")
            provider.send("System", "", "Task")

        messages = mock_client.chat.completions.create.call_args[1]["messages"]
        roles = [m["role"] for m in messages]
        self.assertEqual(roles, ["system", "user"])


if __name__ == "__main__":
    unittest.main()
