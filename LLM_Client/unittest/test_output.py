"""
Tests für extract_json() und format_output().
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from llm_client import extract_json, format_output


HEADER = [
    "Provider : openai",
    "Model    : gpt-4o",
    "System   : Du bist ein hilfreicher Assistent.",
    "Context  : (none)",
    "Task     : Gib mir ein JSON-Objekt.",
]
RESPONSE = "Das ist die Antwort."
JSON_RESPONSE = 'Hier ist das Ergebnis:\n```json\n{"key": "value", "n": 42}\n```\nFertig.'


class TestExtractJson(unittest.TestCase):

    def test_markdown_json_block(self):
        result = extract_json(JSON_RESPONSE)
        self.assertEqual(result, '{"key": "value", "n": 42}')

    def test_markdown_code_block_no_lang(self):
        text = 'Ergebnis:\n```\n{"a": 1}\n```'
        result = extract_json(text)
        parsed = json.loads(result)
        self.assertEqual(parsed["a"], 1)

    def test_raw_json_object(self):
        text = 'Hier ist das JSON: {"name": "test", "value": 42} Ende.'
        result = extract_json(text)
        parsed = json.loads(result)
        self.assertEqual(parsed["name"], "test")
        self.assertEqual(parsed["value"], 42)

    def test_raw_json_array(self):
        text = 'Liste der Elemente: [1, 2, 3] — Ende.'
        result = extract_json(text)
        self.assertEqual(json.loads(result), [1, 2, 3])

    def test_nested_json(self):
        text = '{"outer": {"inner": [1, 2, 3]}}'
        result = extract_json(text)
        parsed = json.loads(result)
        self.assertEqual(parsed["outer"]["inner"], [1, 2, 3])

    def test_no_json_raises(self):
        with self.assertRaises(ValueError):
            extract_json("Das ist nur normaler Text ohne JSON.")

    def test_invalid_json_in_markdown_block_falls_through_to_error(self):
        # Markdown-Block mit ungültigem JSON, kein Raw-JSON vorhanden
        text = "```json\n{ungültig: kein json}\n```"
        with self.assertRaises(ValueError):
            extract_json(text)

    def test_empty_string_raises(self):
        with self.assertRaises(ValueError):
            extract_json("")

    def test_returns_string(self):
        result = extract_json('{"x": 1}')
        self.assertIsInstance(result, str)

    def test_result_is_valid_json(self):
        result = extract_json(JSON_RESPONSE)
        parsed = json.loads(result)
        self.assertIn("key", parsed)


class TestFormatOutput(unittest.TestCase):

    def test_format_header_contains_all_header_lines(self):
        result = format_output(RESPONSE, HEADER, "header")
        for line in HEADER:
            self.assertIn(line, result)

    def test_format_header_contains_separator(self):
        result = format_output(RESPONSE, HEADER, "header")
        self.assertIn("-" * 60, result)

    def test_format_header_contains_response_label(self):
        result = format_output(RESPONSE, HEADER, "header")
        self.assertIn("Response:", result)

    def test_format_header_contains_response_text(self):
        result = format_output(RESPONSE, HEADER, "header")
        self.assertIn(RESPONSE, result)

    def test_format_header_ends_with_newline(self):
        result = format_output(RESPONSE, HEADER, "header")
        self.assertTrue(result.endswith("\n"))

    def test_format_plain_is_only_response(self):
        result = format_output(RESPONSE, HEADER, "plain")
        self.assertEqual(result, RESPONSE + "\n")

    def test_format_plain_has_no_header(self):
        result = format_output(RESPONSE, HEADER, "plain")
        self.assertNotIn("Provider", result)
        self.assertNotIn("Model", result)
        self.assertNotIn("Response:", result)

    def test_format_json_extracts_json(self):
        result = format_output(JSON_RESPONSE, HEADER, "json")
        parsed = json.loads(result.strip())
        self.assertEqual(parsed["key"], "value")

    def test_format_json_no_header(self):
        result = format_output(JSON_RESPONSE, HEADER, "json")
        self.assertNotIn("Provider", result)

    def test_format_json_ends_with_newline(self):
        result = format_output(JSON_RESPONSE, HEADER, "json")
        self.assertTrue(result.endswith("\n"))

    def test_format_json_no_json_raises(self):
        with self.assertRaises(ValueError):
            format_output("Kein JSON hier.", HEADER, "json")

    def test_unknown_format_raises(self):
        with self.assertRaises(ValueError):
            format_output(RESPONSE, HEADER, "unknown_format")

    def test_format_plain_ends_with_newline(self):
        result = format_output(RESPONSE, HEADER, "plain")
        self.assertTrue(result.endswith("\n"))


if __name__ == "__main__":
    unittest.main()
