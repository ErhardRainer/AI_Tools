"""
Tests für DeepSeekProvider — DeepSeek (platform.deepseek.com)
Modelle: deepseek-chat (V3), deepseek-reasoner (R1), ...
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _mock_openai(reply: str = "Test-Antwort von DeepSeek"):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = reply
    mock_client.chat.completions.create.return_value = mock_response

    mock_module = MagicMock()
    mock_module.OpenAI.return_value = mock_client
    return mock_module, mock_client


class TestDeepSeekProvider(unittest.TestCase):

    def test_default_model(self):
        from llm_client import DeepSeekProvider
        mock_module, _ = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = DeepSeekProvider(api_key="sk-ds-test")
        self.assertEqual(provider.model, "deepseek-chat")

    def test_reasoner_model(self):
        """deepseek-reasoner (R1) ist ein Chain-of-Thought-Modell."""
        from llm_client import DeepSeekProvider
        mock_module, _ = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = DeepSeekProvider(api_key="sk-ds-test", model="deepseek-reasoner")
        self.assertEqual(provider.model, "deepseek-reasoner")

    def test_uses_deepseek_base_url(self):
        """DeepSeekProvider muss api.deepseek.com als base_url verwenden."""
        from llm_client import DeepSeekProvider
        mock_module, _ = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            DeepSeekProvider(api_key="sk-ds-test")
        _, kwargs = mock_module.OpenAI.call_args
        self.assertEqual(kwargs["base_url"], "https://api.deepseek.com")

    def test_send_returns_response(self):
        from llm_client import DeepSeekProvider
        mock_module, _ = _mock_openai("DeepSeek V3 Antwort")
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = DeepSeekProvider(api_key="sk-ds-test")
            result = provider.send("System", "Kontext", "Task")
        self.assertEqual(result, "DeepSeek V3 Antwort")

    def test_send_with_context_builds_correct_message_roles(self):
        from llm_client import DeepSeekProvider
        mock_module, mock_client = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = DeepSeekProvider(api_key="sk-ds-test")
            provider.send("System", "Kontext vorhanden", "Task")

        messages = mock_client.chat.completions.create.call_args[1]["messages"]
        roles = [m["role"] for m in messages]
        self.assertEqual(roles, ["system", "user", "assistant", "user"])

    def test_send_without_context_skips_ack(self):
        from llm_client import DeepSeekProvider
        mock_module, mock_client = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = DeepSeekProvider(api_key="sk-ds-test")
            provider.send("System", "", "Task")

        messages = mock_client.chat.completions.create.call_args[1]["messages"]
        roles = [m["role"] for m in messages]
        self.assertEqual(roles, ["system", "user"])

    def test_send_uses_correct_model_in_api_call(self):
        from llm_client import DeepSeekProvider
        mock_module, mock_client = _mock_openai()
        with patch.dict(sys.modules, {"openai": mock_module}):
            provider = DeepSeekProvider(api_key="sk-ds-test", model="deepseek-reasoner")
            provider.send("System", "", "Task")

        call_kwargs = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs["model"], "deepseek-reasoner")


if __name__ == "__main__":
    unittest.main()
