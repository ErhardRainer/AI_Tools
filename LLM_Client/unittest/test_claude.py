"""
Tests für ClaudeProvider — console.anthropic.com
Modelle: claude-sonnet-4-6, claude-opus-4-6, claude-haiku-4-5-20251001, ...
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _mock_anthropic(reply: str = "Test-Antwort von Claude"):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content[0].text = reply
    mock_client.messages.create.return_value = mock_response

    mock_module = MagicMock()
    mock_module.Anthropic.return_value = mock_client
    return mock_module, mock_client


class TestClaudeProvider(unittest.TestCase):

    def test_default_model(self):
        from llm_client import ClaudeProvider
        mock_module, _ = _mock_anthropic()
        with patch.dict(sys.modules, {"anthropic": mock_module}):
            provider = ClaudeProvider(api_key="sk-ant-test")
        self.assertEqual(provider.model, "claude-sonnet-4-6")

    def test_custom_model(self):
        from llm_client import ClaudeProvider
        mock_module, _ = _mock_anthropic()
        with patch.dict(sys.modules, {"anthropic": mock_module}):
            provider = ClaudeProvider(api_key="sk-ant-test", model="claude-opus-4-6")
        self.assertEqual(provider.model, "claude-opus-4-6")

    def test_send_returns_response(self):
        from llm_client import ClaudeProvider
        mock_module, _ = _mock_anthropic("Antwort von Claude Sonnet")
        with patch.dict(sys.modules, {"anthropic": mock_module}):
            provider = ClaudeProvider(api_key="sk-ant-test")
            result = provider.send("System", "Kontext", "Task")
        self.assertEqual(result, "Antwort von Claude Sonnet")

    def test_send_passes_system_as_parameter(self):
        """Claude erhält das System-Prompt als eigenen Parameter, nicht als Nachricht."""
        from llm_client import ClaudeProvider
        mock_module, mock_client = _mock_anthropic()
        with patch.dict(sys.modules, {"anthropic": mock_module}):
            provider = ClaudeProvider(api_key="sk-ant-test")
            provider.send("Mein System-Prompt", "Kontext", "Task")

        call_kwargs = mock_client.messages.create.call_args[1]
        self.assertEqual(call_kwargs["system"], "Mein System-Prompt")

    def test_send_with_context_adds_ack_message(self):
        from llm_client import ClaudeProvider
        mock_module, mock_client = _mock_anthropic()
        with patch.dict(sys.modules, {"anthropic": mock_module}):
            provider = ClaudeProvider(api_key="sk-ant-test")
            provider.send("System", "Kontext vorhanden", "Task")

        messages = mock_client.messages.create.call_args[1]["messages"]
        roles = [m["role"] for m in messages]
        self.assertEqual(roles, ["user", "assistant", "user"])

    def test_send_without_context_skips_ack(self):
        from llm_client import ClaudeProvider
        mock_module, mock_client = _mock_anthropic()
        with patch.dict(sys.modules, {"anthropic": mock_module}):
            provider = ClaudeProvider(api_key="sk-ant-test")
            provider.send("System", "", "Task ohne Kontext")

        messages = mock_client.messages.create.call_args[1]["messages"]
        roles = [m["role"] for m in messages]
        self.assertEqual(roles, ["user"])

    def test_send_uses_max_tokens(self):
        from llm_client import ClaudeProvider
        mock_module, mock_client = _mock_anthropic()
        with patch.dict(sys.modules, {"anthropic": mock_module}):
            provider = ClaudeProvider(api_key="sk-ant-test")
            provider.send("System", "", "Task")

        call_kwargs = mock_client.messages.create.call_args[1]
        self.assertIn("max_tokens", call_kwargs)
        self.assertGreater(call_kwargs["max_tokens"], 0)


if __name__ == "__main__":
    unittest.main()
