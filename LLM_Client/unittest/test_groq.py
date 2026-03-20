"""
Tests für GroqProvider — Groq (console.groq.com)
Modelle: llama-3.3-70b-versatile, llama-3.1-8b-instant, gemma2-9b-it, mixtral-8x7b-32768, ...
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _mock_openai(reply: str = "Test-Antwort von Groq"):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = reply
    mock_client.chat.completions.create.return_value = mock_response

    mock_module = MagicMock()
    mock_module.OpenAI.return_value = mock_client
    return mock_module, mock_client


class TestGroqProvider(unittest.TestCase):

    def test_default_model(self):
        from llm_client import GroqProvider
        mock_module, _ = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = GroqProvider(api_key="gsk_test")
        self.assertEqual(provider.model, "llama-3.3-70b-versatile")

    def test_custom_model_gemma(self):
        from llm_client import GroqProvider
        mock_module, _ = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = GroqProvider(api_key="gsk_test", model="gemma2-9b-it")
        self.assertEqual(provider.model, "gemma2-9b-it")

    def test_uses_groq_base_url(self):
        """GroqProvider muss api.groq.com/openai/v1 als base_url verwenden."""
        from llm_client import GroqProvider
        mock_module, _ = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            GroqProvider(api_key="gsk_test")
        _, kwargs = mock_module.OpenAI.call_args
        self.assertEqual(kwargs["base_url"], "https://api.groq.com/openai/v1")

    def test_send_returns_response(self):
        from llm_client import GroqProvider
        mock_module, _ = _mock_openai("LLaMA 3.3 70B Antwort")
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = GroqProvider(api_key="gsk_test")
            result = provider.send("System", "Kontext", "Task")
        self.assertEqual(result, "LLaMA 3.3 70B Antwort")

    def test_send_with_context_builds_correct_message_roles(self):
        from llm_client import GroqProvider
        mock_module, mock_client = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = GroqProvider(api_key="gsk_test")
            provider.send("System", "Kontext", "Task")

        messages = mock_client.chat.completions.create.call_args[1]["messages"]
        roles = [m["role"] for m in messages]
        self.assertEqual(roles, ["system", "user", "assistant", "user"])

    def test_send_without_context_skips_ack(self):
        from llm_client import GroqProvider
        mock_module, mock_client = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = GroqProvider(api_key="gsk_test")
            provider.send("System", "", "Task")

        messages = mock_client.chat.completions.create.call_args[1]["messages"]
        roles = [m["role"] for m in messages]
        self.assertEqual(roles, ["system", "user"])

    def test_mixtral_model(self):
        from llm_client import GroqProvider
        mock_module, _ = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = GroqProvider(api_key="gsk_test", model="mixtral-8x7b-32768")
        self.assertEqual(provider.model, "mixtral-8x7b-32768")


if __name__ == "__main__":
    unittest.main()
