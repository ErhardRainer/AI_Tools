"""
Tests für ImageGen.

Keine echten API-Calls — alle Provider-SDKs und requests werden gemockt.
"""

import base64
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ImageGen.image_gen import (
    ImageData,
    ImageResult,
    OpenAIImageProvider,
    GoogleImageProvider,
    StabilityProvider,
    FalProvider,
    build_provider,
    load_config,
    mapping_reload,
    resolve_preset,
    PRESET_REGISTRY,
)

# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

DUMMY_B64 = base64.b64encode(b"fake-image-bytes").decode()

def _openai_response(url="https://img.example.com/1.png", b64=None, revised="revised prompt"):
    item = MagicMock()
    item.url = url
    item.b64_json = b64
    item.revised_prompt = revised
    resp = MagicMock()
    resp.data = [item]
    return resp

def _stability_response(b64=DUMMY_B64):
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {"image": b64, "finish_reason": "SUCCESS", "seed": 42}
    return resp

def _fal_response(url="https://fal.media/img/1.png"):
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {"images": [{"url": url, "width": 1024, "height": 1024}]}
    return resp


# ---------------------------------------------------------------------------
# ImageData
# ---------------------------------------------------------------------------

class TestImageData(unittest.TestCase):

    def test_save_from_b64(self):
        img = ImageData(b64_json=DUMMY_B64)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            tmp = f.name
        img.save(tmp)
        self.assertEqual(Path(tmp).read_bytes(), b"fake-image-bytes")
        Path(tmp).unlink()

    def test_save_from_url(self):
        img = ImageData(url="https://example.com/img.png")
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.content = b"url-image-bytes"
        with patch("requests.get", return_value=mock_resp):
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                tmp = f.name
            img.save(tmp)
        self.assertEqual(Path(tmp).read_bytes(), b"url-image-bytes")
        Path(tmp).unlink()

    def test_save_no_content_raises(self):
        img = ImageData()
        with self.assertRaises(ValueError):
            img.save("/tmp/nope.png")

    def test_to_dict(self):
        img = ImageData(url="https://x.com/img.png", b64_json="abc")
        d = img.to_dict()
        self.assertEqual(d["url"], "https://x.com/img.png")
        self.assertEqual(d["b64_json"], "abc")


# ---------------------------------------------------------------------------
# ImageResult
# ---------------------------------------------------------------------------

class TestImageResult(unittest.TestCase):

    def test_save_all_pattern(self):
        result = ImageResult(
            provider="openai", model="dall-e-3",
            images=[ImageData(b64_json=DUMMY_B64), ImageData(b64_json=DUMMY_B64)],
        )
        with tempfile.TemporaryDirectory() as td:
            pattern = str(Path(td) / "img_{n}.png")
            paths = result.save_all(pattern)
        self.assertEqual(len(paths), 2)
        self.assertIn("img_1.png", paths[0])
        self.assertIn("img_2.png", paths[1])


# ---------------------------------------------------------------------------
# OpenAIImageProvider
# ---------------------------------------------------------------------------

class TestOpenAIImageProvider(unittest.TestCase):

    def _make_provider(self):
        mock_openai = MagicMock()
        with patch.dict("sys.modules", {"openai": mock_openai}):
            p = OpenAIImageProvider(api_key="sk-test", model="dall-e-3")
        p.client = MagicMock()
        return p

    def test_generate_returns_image_result(self):
        p = self._make_provider()
        p.client.images.generate.return_value = _openai_response()
        result = p.generate("a cat")
        self.assertIsInstance(result, ImageResult)
        self.assertEqual(result.provider, "openai")
        self.assertEqual(result.model, "dall-e-3")
        self.assertEqual(len(result.images), 1)
        self.assertEqual(result.images[0].url, "https://img.example.com/1.png")

    def test_revised_prompt_captured(self):
        p = self._make_provider()
        p.client.images.generate.return_value = _openai_response(revised="A fluffy cat sitting.")
        result = p.generate("cat")
        self.assertEqual(result.revised_prompt, "A fluffy cat sitting.")

    def test_default_model(self):
        mock_openai = MagicMock()
        with patch.dict("sys.modules", {"openai": mock_openai}):
            p = OpenAIImageProvider(api_key="sk-test")
        self.assertEqual(p.model, "dall-e-3")

    def test_missing_sdk_raises(self):
        with patch.dict("sys.modules", {"openai": None}):
            with self.assertRaises(ImportError):
                OpenAIImageProvider(api_key="sk-test")

    def test_generate_passes_size_quality(self):
        p = self._make_provider()
        p.client.images.generate.return_value = _openai_response()
        p.generate("cat", size="1792x1024", quality="hd", n=1)
        call_kwargs = p.client.images.generate.call_args[1]
        self.assertEqual(call_kwargs["size"], "1792x1024")
        self.assertEqual(call_kwargs["quality"], "hd")


# ---------------------------------------------------------------------------
# GoogleImageProvider
# ---------------------------------------------------------------------------

class TestGoogleImageProvider(unittest.TestCase):

    def _make_imagen_provider(self, model="imagen-4.0-generate-001"):
        mock_genai = MagicMock()
        mock_genai.types.GenerateImagesConfig = MagicMock(return_value=MagicMock())
        p = GoogleImageProvider.__new__(GoogleImageProvider)
        p.model = model
        p._genai = mock_genai
        p.client = MagicMock()
        return p

    def _make_gemini_provider(self, model="gemini-2.5-flash-image-preview"):
        mock_genai = MagicMock()
        mock_genai.types.GenerateContentConfig = MagicMock(return_value=MagicMock())
        p = GoogleImageProvider.__new__(GoogleImageProvider)
        p.model = model
        p._genai = mock_genai
        p.client = MagicMock()
        return p

    def test_imagen_generate_returns_image_result(self):
        p = self._make_imagen_provider()
        fake_img = MagicMock()
        fake_img.image.image_bytes = b"fake-png-bytes"
        p.client.models.generate_images.return_value = MagicMock(
            generated_images=[fake_img]
        )
        result = p.generate("a mountain")
        self.assertIsInstance(result, ImageResult)
        self.assertEqual(result.provider, "google")
        self.assertEqual(len(result.images), 1)
        expected_b64 = base64.b64encode(b"fake-png-bytes").decode()
        self.assertEqual(result.images[0].b64_json, expected_b64)

    def test_imagen_default_model_is_v4(self):
        self.assertEqual(GoogleImageProvider.DEFAULT_MODEL, "imagen-4.0-generate-001")

    def test_gemini_flash_generate_returns_image_result(self):
        p = self._make_gemini_provider()
        # Gemini Flash response: candidates[0].content.parts mit inline_data
        fake_part = MagicMock()
        fake_part.text = None
        fake_part.inline_data = MagicMock()
        fake_part.inline_data.data = b"gemini-image-bytes"
        p.client.models.generate_content.return_value = MagicMock(
            candidates=[MagicMock(content=MagicMock(parts=[fake_part]))]
        )
        result = p.generate("a sunset")
        self.assertIsInstance(result, ImageResult)
        self.assertEqual(result.provider, "google")
        self.assertEqual(len(result.images), 1)
        expected_b64 = base64.b64encode(b"gemini-image-bytes").decode()
        self.assertEqual(result.images[0].b64_json, expected_b64)

    def test_gemini_flash_no_image_raises(self):
        p = self._make_gemini_provider()
        # Antwort ohne Bild-Teile
        text_only_part = MagicMock()
        text_only_part.text = "Ich kann kein Bild generieren."
        text_only_part.inline_data = None
        p.client.models.generate_content.return_value = MagicMock(
            candidates=[MagicMock(content=MagicMock(parts=[text_only_part]))]
        )
        with self.assertRaises(ValueError):
            p.generate("a scene")

    def test_is_gemini_model_detection(self):
        p_imagen = self._make_imagen_provider("imagen-4.0-generate-001")
        p_gemini = self._make_gemini_provider("gemini-2.0-flash-exp")
        self.assertFalse(p_imagen._is_gemini_model())
        self.assertTrue(p_gemini._is_gemini_model())

    def test_gemini_flash_uses_generate_content(self):
        p = self._make_gemini_provider()
        fake_part = MagicMock()
        fake_part.text = None
        fake_part.inline_data = MagicMock(data=b"bytes")
        p.client.models.generate_content.return_value = MagicMock(
            candidates=[MagicMock(content=MagicMock(parts=[fake_part]))]
        )
        p.generate("test")
        p.client.models.generate_content.assert_called_once()
        p.client.models.generate_images.assert_not_called()

    def test_imagen_uses_generate_images(self):
        p = self._make_imagen_provider()
        fake_img = MagicMock()
        fake_img.image.image_bytes = b"bytes"
        p.client.models.generate_images.return_value = MagicMock(
            generated_images=[fake_img]
        )
        p.generate("test")
        p.client.models.generate_images.assert_called_once()
        p.client.models.generate_content.assert_not_called()

    def test_missing_sdk_raises(self):
        with patch.dict("sys.modules", {"google": None, "google.genai": None}):
            with self.assertRaises(ImportError):
                GoogleImageProvider(api_key="test")


# ---------------------------------------------------------------------------
# StabilityProvider
# ---------------------------------------------------------------------------

class TestStabilityProvider(unittest.TestCase):

    def _make_provider(self, model="core"):
        with patch.dict("sys.modules", {"requests": MagicMock()}):
            p = StabilityProvider(api_key="sk-stab-test", model=model)
        return p

    def test_core_endpoint(self):
        p = self._make_provider("core")
        self.assertIn("/core", p._endpoint())

    def test_sd3_endpoint(self):
        p = self._make_provider("sd3-large")
        self.assertIn("/sd3", p._endpoint())

    def test_ultra_endpoint(self):
        p = self._make_provider("ultra")
        self.assertIn("/ultra", p._endpoint())

    def test_generate_returns_image_result(self):
        p = self._make_provider()
        with patch("requests.post", return_value=_stability_response()):
            result = p.generate("a forest")
        self.assertIsInstance(result, ImageResult)
        self.assertEqual(result.provider, "stability")
        self.assertEqual(len(result.images), 1)
        self.assertEqual(result.images[0].b64_json, DUMMY_B64)

    def test_generate_n_images(self):
        p = self._make_provider()
        with patch("requests.post", return_value=_stability_response()) as mock_post:
            result = p.generate("forest", n=3)
        self.assertEqual(mock_post.call_count, 3)
        self.assertEqual(len(result.images), 3)

    def test_missing_image_in_response_raises(self):
        p = self._make_provider()
        bad_resp = MagicMock()
        bad_resp.raise_for_status = MagicMock()
        bad_resp.json.return_value = {"finish_reason": "ERROR"}
        with patch("requests.post", return_value=bad_resp):
            with self.assertRaises(ValueError):
                p.generate("test")


# ---------------------------------------------------------------------------
# FalProvider
# ---------------------------------------------------------------------------

class TestFalProvider(unittest.TestCase):

    def _make_provider(self, model="fal-ai/flux/dev"):
        with patch.dict("sys.modules", {"requests": MagicMock()}):
            p = FalProvider(api_key="fal-test", model=model)
        return p

    def test_generate_returns_image_result(self):
        p = self._make_provider()
        with patch("requests.post", return_value=_fal_response()):
            result = p.generate("a robot")
        self.assertIsInstance(result, ImageResult)
        self.assertEqual(result.provider, "fal")
        self.assertEqual(result.images[0].url, "https://fal.media/img/1.png")

    def test_default_model(self):
        p = self._make_provider()
        self.assertEqual(p.model, "fal-ai/flux/dev")

    def test_empty_images_raises(self):
        p = self._make_provider()
        bad_resp = MagicMock()
        bad_resp.raise_for_status = MagicMock()
        bad_resp.json.return_value = {"images": []}
        with patch("requests.post", return_value=bad_resp):
            with self.assertRaises(ValueError):
                p.generate("test")

    def test_num_images_passed(self):
        p = self._make_provider()
        with patch("requests.post", return_value=_fal_response()) as mock_post:
            p.generate("test", n=2)
        body = mock_post.call_args[1]["json"]
        self.assertEqual(body["num_images"], 2)


# ---------------------------------------------------------------------------
# build_provider / Factory
# ---------------------------------------------------------------------------

class TestBuildProvider(unittest.TestCase):

    CONFIG = {
        "providers": {
            "openai":    {"api_key": "sk-test",      "model": "dall-e-3"},
            "stability": {"api_key": "sk-stab-test", "model": "core"},
            "fal":       {"api_key": "fal-test",     "model": "fal-ai/flux/dev"},
        }
    }

    def test_build_openai(self):
        mock_openai = MagicMock()
        with patch.dict("sys.modules", {"openai": mock_openai}):
            p = build_provider("openai", self.CONFIG)
        self.assertIsInstance(p, OpenAIImageProvider)

    def test_build_stability(self):
        with patch.dict("sys.modules", {"requests": MagicMock()}):
            p = build_provider("stability", self.CONFIG)
        self.assertIsInstance(p, StabilityProvider)

    def test_build_fal(self):
        with patch.dict("sys.modules", {"requests": MagicMock()}):
            p = build_provider("fal", self.CONFIG)
        self.assertIsInstance(p, FalProvider)

    def test_model_override(self):
        mock_openai = MagicMock()
        with patch.dict("sys.modules", {"openai": mock_openai}):
            p = build_provider("openai", self.CONFIG, model_override="dall-e-2")
        self.assertEqual(p.model, "dall-e-2")

    def test_unknown_provider_raises(self):
        with self.assertRaises(ValueError):
            build_provider("nicht_vorhanden", self.CONFIG)

    def test_missing_api_key_raises(self):
        cfg = {"providers": {"openai": {"model": "dall-e-3"}}}
        with self.assertRaises(ValueError):
            build_provider("openai", cfg)


# ---------------------------------------------------------------------------
# Preset-System
# ---------------------------------------------------------------------------

class TestPresets(unittest.TestCase):

    def setUp(self):
        PRESET_REGISTRY.clear()

    def test_mapping_reload_from_dict(self):
        mapping_reload({"presets": {"quality": {"provider": "openai", "model": "dall-e-3"}}})
        self.assertIn("quality", PRESET_REGISTRY)

    def test_resolve_preset(self):
        mapping_reload({"presets": {"flux": {"provider": "fal", "model": "fal-ai/flux/dev"}}})
        provider, model = resolve_preset("flux")
        self.assertEqual(provider, "fal")
        self.assertEqual(model, "fal-ai/flux/dev")

    def test_resolve_unknown_raises(self):
        with self.assertRaises(KeyError):
            resolve_preset("unbekannt")

    def test_invalid_preset_raises(self):
        with self.assertRaises(ValueError):
            mapping_reload({"presets": {"bad": "kein-dict"}})


# ---------------------------------------------------------------------------
# load_config
# ---------------------------------------------------------------------------

class TestLoadConfig(unittest.TestCase):

    def test_loads_valid_json(self):
        data = {"providers": {"openai": {"api_key": "sk-test"}}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = f.name
        loaded = load_config(path)
        self.assertEqual(loaded["providers"]["openai"]["api_key"], "sk-test")
        Path(path).unlink()

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            load_config("/nonexistent/config.json")


if __name__ == "__main__":
    unittest.main()
