"""
Tests für das Preset/Alias-System: PRESET_REGISTRY, mapping_reload(), resolve_preset().
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import llm_client


# Hilfsfunktion: Registry nach jedem Test zurücksetzen
def _clear_registry():
    llm_client.PRESET_REGISTRY.clear()


SAMPLE_PRESETS = {
    "coding":    {"provider": "claude",   "model": "claude-opus-4-6"},
    "fast":      {"provider": "groq",     "model": "llama-3.1-8b-instant"},
    "cheap":     {"provider": "deepseek", "model": "deepseek-chat"},
    "reasoning": {"provider": "deepseek", "model": "deepseek-reasoner"},
    "longctx":   {"provider": "kimi",     "model": "moonshot-v1-128k"},
}


class TestMappingReloadFromDict(unittest.TestCase):

    def tearDown(self):
        _clear_registry()

    def test_load_from_config_dict_with_presets_key(self):
        config = {"presets": SAMPLE_PRESETS}
        result = llm_client.mapping_reload(config)
        self.assertEqual(result, SAMPLE_PRESETS)
        self.assertEqual(llm_client.PRESET_REGISTRY, SAMPLE_PRESETS)

    def test_load_from_flat_presets_dict(self):
        """mapping_reload akzeptiert auch ein dict ohne 'presets'-Wrapper."""
        result = llm_client.mapping_reload(SAMPLE_PRESETS)
        self.assertEqual(result, SAMPLE_PRESETS)

    def test_reload_replaces_existing_registry(self):
        llm_client.mapping_reload({"presets": {"old": {"provider": "openai", "model": "gpt-4o"}}})
        llm_client.mapping_reload({"presets": SAMPLE_PRESETS})
        self.assertNotIn("old", llm_client.PRESET_REGISTRY)
        self.assertIn("coding", llm_client.PRESET_REGISTRY)

    def test_empty_presets_clears_registry(self):
        llm_client.mapping_reload({"presets": SAMPLE_PRESETS})
        llm_client.mapping_reload({"presets": {}})
        self.assertEqual(llm_client.PRESET_REGISTRY, {})

    def test_invalid_entry_raises_value_error(self):
        bad = {"broken": "not-a-dict"}
        with self.assertRaises(ValueError):
            llm_client.mapping_reload({"presets": bad})

    def test_entry_missing_provider_raises_value_error(self):
        bad = {"noprovider": {"model": "gpt-4o"}}
        with self.assertRaises(ValueError):
            llm_client.mapping_reload({"presets": bad})


class TestMappingReloadFromFile(unittest.TestCase):

    def tearDown(self):
        _clear_registry()

    def test_load_from_json_file_with_presets_key(self):
        data = {"presets": SAMPLE_PRESETS, "other": "ignored"}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = f.name
        try:
            result = llm_client.mapping_reload(path)
            self.assertEqual(result, SAMPLE_PRESETS)
        finally:
            os.unlink(path)

    def test_load_from_flat_json_file(self):
        """JSON-Datei ohne 'presets'-Schlüssel wird als flache Mapping-Tabelle behandelt."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(SAMPLE_PRESETS, f)
            path = f.name
        try:
            result = llm_client.mapping_reload(path)
            self.assertEqual(result, SAMPLE_PRESETS)
        finally:
            os.unlink(path)

    def test_missing_file_raises_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            llm_client.mapping_reload("/nonexistent/presets.json")


class TestResolvePreset(unittest.TestCase):

    def setUp(self):
        llm_client.mapping_reload({"presets": SAMPLE_PRESETS})

    def tearDown(self):
        _clear_registry()

    def test_resolve_known_preset(self):
        provider, model = llm_client.resolve_preset("coding")
        self.assertEqual(provider, "claude")
        self.assertEqual(model, "claude-opus-4-6")

    def test_resolve_all_sample_presets(self):
        expected = {
            "coding":    ("claude",   "claude-opus-4-6"),
            "fast":      ("groq",     "llama-3.1-8b-instant"),
            "cheap":     ("deepseek", "deepseek-chat"),
            "reasoning": ("deepseek", "deepseek-reasoner"),
            "longctx":   ("kimi",     "moonshot-v1-128k"),
        }
        for alias, (exp_provider, exp_model) in expected.items():
            with self.subTest(alias=alias):
                provider, model = llm_client.resolve_preset(alias)
                self.assertEqual(provider, exp_provider)
                self.assertEqual(model, exp_model)

    def test_unknown_preset_raises_key_error(self):
        with self.assertRaises(KeyError):
            llm_client.resolve_preset("nonexistent_alias")

    def test_error_message_contains_alias_name(self):
        try:
            llm_client.resolve_preset("xyz_unknown")
        except KeyError as e:
            self.assertIn("xyz_unknown", str(e))

    def test_preset_without_model_returns_empty_string(self):
        llm_client.mapping_reload({"presets": {"nomodel": {"provider": "openai"}}})
        provider, model = llm_client.resolve_preset("nomodel")
        self.assertEqual(provider, "openai")
        self.assertEqual(model, "")

    def test_resolve_before_reload_raises_key_error(self):
        _clear_registry()
        with self.assertRaises(KeyError):
            llm_client.resolve_preset("coding")


class TestPresetRegistryIsModuleLevel(unittest.TestCase):
    """Stellt sicher, dass PRESET_REGISTRY dasselbe Objekt ist, das mapping_reload befüllt."""

    def tearDown(self):
        _clear_registry()

    def test_registry_is_same_object_after_reload(self):
        original_id = id(llm_client.PRESET_REGISTRY)
        llm_client.mapping_reload({"presets": SAMPLE_PRESETS})
        # Das Dict-Objekt bleibt dasselbe (clear + update), nur der Inhalt ändert sich
        self.assertEqual(id(llm_client.PRESET_REGISTRY), original_id)

    def test_mapping_reload_returns_the_registry(self):
        result = llm_client.mapping_reload({"presets": {"myalias": {"provider": "openai", "model": "gpt-4o"}}})
        self.assertIs(result, llm_client.PRESET_REGISTRY)
        self.assertIn("myalias", result)


if __name__ == "__main__":
    unittest.main()
