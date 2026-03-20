"""
Tests für load_prompts_file().

Variante a: einzelnes Prompt-Set  {system, context, task}
Variante b: benannte Prompt-Sets  {name: {system, context, task}, ...}
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import llm_client


def _write_json(tmp_dir: str, data: dict, filename: str = "prompts.json") -> str:
    path = os.path.join(tmp_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return path


# ---------------------------------------------------------------------------
# Variante a — einzelnes Prompt-Set
# ---------------------------------------------------------------------------

class TestLoadPromptsFileSingle(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_loads_all_three_keys(self):
        path = _write_json(self.tmp, {
            "system":  "Du bist ein Assistent.",
            "context": "Hintergrundinformation.",
            "task":    "Beantworte die Frage.",
        })
        result = llm_client.load_prompts_file(path)
        self.assertEqual(result["system"],  "Du bist ein Assistent.")
        self.assertEqual(result["context"], "Hintergrundinformation.")
        self.assertEqual(result["task"],    "Beantworte die Frage.")

    def test_missing_context_defaults_to_empty_string(self):
        path = _write_json(self.tmp, {"system": "S", "task": "T"})
        result = llm_client.load_prompts_file(path)
        self.assertEqual(result["context"], "")

    def test_missing_system_defaults_to_empty_string(self):
        path = _write_json(self.tmp, {"task": "T"})
        result = llm_client.load_prompts_file(path)
        self.assertEqual(result["system"], "")

    def test_name_parameter_ignored_for_single_set(self):
        """name wird ignoriert, wenn das Format Variante a ist."""
        path = _write_json(self.tmp, {"system": "S", "task": "T"})
        result = llm_client.load_prompts_file(path, name="anything")
        self.assertEqual(result["task"], "T")

    def test_returns_exactly_three_keys(self):
        path = _write_json(self.tmp, {"system": "S", "context": "C", "task": "T", "extra": "X"})
        result = llm_client.load_prompts_file(path)
        self.assertEqual(set(result.keys()), {"system", "context", "task"})


# ---------------------------------------------------------------------------
# Variante b — benannte Prompt-Sets
# ---------------------------------------------------------------------------

MULTI_PROMPTS = {
    "default": {
        "system":  "Standard-Assistent.",
        "context": "",
        "task":    "Standard-Aufgabe.",
    },
    "summarize": {
        "system":  "Zusammenfassungs-Assistent.",
        "context": "Langer Text.",
        "task":    "Fasse in drei Punkten zusammen.",
    },
    "translate": {
        "system":  "Übersetzer.",
        "context": "",
        "task":    "Übersetze ins Englische.",
    },
}


class TestLoadPromptsFileMulti(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = _write_json(self.tmp, MULTI_PROMPTS)

    def test_loads_named_set(self):
        result = llm_client.load_prompts_file(self.path, name="summarize")
        self.assertEqual(result["system"], "Zusammenfassungs-Assistent.")
        self.assertEqual(result["task"],   "Fasse in drei Punkten zusammen.")

    def test_loads_different_named_set(self):
        result = llm_client.load_prompts_file(self.path, name="translate")
        self.assertEqual(result["task"], "Übersetze ins Englische.")

    def test_default_name_used_when_no_name_given(self):
        result = llm_client.load_prompts_file(self.path)
        self.assertEqual(result["task"], "Standard-Aufgabe.")

    def test_explicit_default_name(self):
        result = llm_client.load_prompts_file(self.path, name="default")
        self.assertEqual(result["task"], "Standard-Aufgabe.")

    def test_unknown_name_raises_key_error(self):
        with self.assertRaises(KeyError):
            llm_client.load_prompts_file(self.path, name="nonexistent")

    def test_error_message_contains_name(self):
        try:
            llm_client.load_prompts_file(self.path, name="xyz_missing")
        except KeyError as e:
            self.assertIn("xyz_missing", str(e))

    def test_missing_fields_in_named_set_default_to_empty(self):
        path = _write_json(self.tmp, {"minimal": {"task": "Nur Aufgabe"}})
        result = llm_client.load_prompts_file(path, name="minimal")
        self.assertEqual(result["system"],  "")
        self.assertEqual(result["context"], "")
        self.assertEqual(result["task"],    "Nur Aufgabe")

    def test_single_entry_without_name_uses_only_entry(self):
        """Wenn Variante b genau einen Eintrag hat und kein name angegeben ist,
        wird dieser Eintrag automatisch verwendet."""
        path = _write_json(self.tmp, {
            "onlyone": {"system": "S", "context": "C", "task": "T"}
        })
        result = llm_client.load_prompts_file(path)
        self.assertEqual(result["task"], "T")


# ---------------------------------------------------------------------------
# Fehlerfälle
# ---------------------------------------------------------------------------

class TestLoadPromptsFileErrors(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_missing_file_raises_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            llm_client.load_prompts_file("/nonexistent/prompts.json")

    def test_invalid_format_raises_value_error(self):
        """Ein Eintrag mit nicht-dict-Wert und keinen Prompt-Schlüsseln."""
        path = _write_json(self.tmp, {"bad_entry": "not a dict"})
        with self.assertRaises(ValueError):
            llm_client.load_prompts_file(path)

    def test_no_name_and_no_default_key_raises_key_error(self):
        """Variante b, kein 'default' Schlüssel, mehr als ein Eintrag."""
        path = _write_json(self.tmp, {
            "alpha": {"task": "A"},
            "beta":  {"task": "B"},
        })
        with self.assertRaises(KeyError):
            llm_client.load_prompts_file(path)


if __name__ == "__main__":
    unittest.main()
