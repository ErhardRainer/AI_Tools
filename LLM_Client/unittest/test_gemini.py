"""
Tests für GeminiProvider — aistudio.google.com
Modelle: gemini-2.0-flash, gemini-2.0-pro, gemini-1.5-pro, ...
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _mock_genai(reply: str = "Test-Antwort von Gemini"):
    """Gibt ein Mock für google.generativeai zurück."""
    mock_model_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.text = reply
    mock_model_instance.generate_content.return_value = mock_response

    mock_module = MagicMock()
    mock_module.GenerativeModel.return_value = mock_model_instance
    return mock_module, mock_model_instance


def _patched_modules(mock_genai_module):
    """Erstellt ein sys.modules-Patch-Dict für google.generativeai."""
    mock_google = MagicMock()
    mock_google.generativeai = mock_genai_module
    return {
        "google": mock_google,
        "google.generativeai": mock_genai_module,
    }


class TestGeminiProvider(unittest.TestCase):

    def test_default_model(self):
        from llm_client import GeminiProvider
        mock_module, _ = _mock_genai()
        with patch.dict(sys.modules, _patched_modules(mock_module)):
            provider = GeminiProvider(api_key="AIza-test")
        self.assertEqual(provider.model, "gemini-2.0-flash")

    def test_custom_model(self):
        from llm_client import GeminiProvider
        mock_module, _ = _mock_genai()
        with patch.dict(sys.modules, _patched_modules(mock_module)):
            provider = GeminiProvider(api_key="AIza-test", model="gemini-2.0-pro")
        self.assertEqual(provider.model, "gemini-2.0-pro")

    def test_send_returns_response(self):
        from llm_client import GeminiProvider
        mock_module, _ = _mock_genai("Antwort von Gemini Flash")
        with patch.dict(sys.modules, _patched_modules(mock_module)):
            provider = GeminiProvider(api_key="AIza-test")
            result = provider.send("System", "Kontext", "Task")
        self.assertEqual(result, "Antwort von Gemini Flash")

    def test_send_concatenates_context_and_task(self):
        """Gemini erhält context + task als einen kombinierten User-Text."""
        from llm_client import GeminiProvider
        mock_module, mock_model_instance = _mock_genai()
        with patch.dict(sys.modules, _patched_modules(mock_module)):
            provider = GeminiProvider(api_key="AIza-test")
            provider.send("System", "Mein Kontext", "Meine Aufgabe")

        call_args = mock_model_instance.generate_content.call_args
        user_content = call_args[0][0]
        self.assertIn("Mein Kontext", user_content)
        self.assertIn("Meine Aufgabe", user_content)

    def test_send_without_context_uses_task_only(self):
        from llm_client import GeminiProvider
        mock_module, mock_model_instance = _mock_genai()
        with patch.dict(sys.modules, _patched_modules(mock_module)):
            provider = GeminiProvider(api_key="AIza-test")
            provider.send("System", "", "Nur die Aufgabe")

        call_args = mock_model_instance.generate_content.call_args
        user_content = call_args[0][0]
        self.assertEqual(user_content.strip(), "Nur die Aufgabe")

    def test_api_key_passed_to_configure(self):
        from llm_client import GeminiProvider
        mock_module, _ = _mock_genai()
        with patch.dict(sys.modules, _patched_modules(mock_module)):
            GeminiProvider(api_key="AIza-mykey")
        mock_module.configure.assert_called_once_with(api_key="AIza-mykey")


if __name__ == "__main__":
    unittest.main()
