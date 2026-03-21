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
    IdeogramProvider,
    LeonardoProvider,
    FireflyProvider,
    Auto1111Provider,
    OllamaDiffuserProvider,
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
# IdeogramProvider
# ---------------------------------------------------------------------------

class TestIdeogramProvider(unittest.TestCase):

    def _make_provider(self, model="V_3"):
        p = IdeogramProvider.__new__(IdeogramProvider)
        p.api_key = "test-key"
        p.model = model
        return p

    def test_generate_returns_image_result(self):
        p = self._make_provider()
        fake_img_bytes = b"fake-jpeg-bytes"
        fake_generate_resp = MagicMock()
        fake_generate_resp.json.return_value = {"data": [{"url": "https://ideogram.ai/img/abc"}]}
        fake_generate_resp.raise_for_status = MagicMock()
        fake_download_resp = MagicMock()
        fake_download_resp.content = fake_img_bytes
        fake_download_resp.raise_for_status = MagicMock()
        with patch("requests.post", return_value=fake_generate_resp), \
             patch("requests.get",  return_value=fake_download_resp):
            result = p.generate("a futuristic city")
        self.assertIsInstance(result, ImageResult)
        self.assertEqual(result.provider, "ideogram")
        self.assertEqual(len(result.images), 1)
        self.assertEqual(result.images[0].b64_json,
                         base64.b64encode(fake_img_bytes).decode())

    def test_aspect_ratio_mapping(self):
        p = self._make_provider()
        self.assertEqual(p._ASPECT_MAP.get("16:9"), "ASPECT_16_9")
        self.assertEqual(p._ASPECT_MAP.get("1:1"),  "ASPECT_1_1")

    def test_empty_data_raises(self):
        p = self._make_provider()
        resp = MagicMock()
        resp.json.return_value = {"data": []}
        resp.raise_for_status = MagicMock()
        with patch("requests.post", return_value=resp):
            with self.assertRaises(ValueError):
                p.generate("test")

    def test_negative_prompt_included(self):
        p = self._make_provider()
        captured = {}
        def fake_post(url, headers, json, timeout):
            captured["body"] = json
            resp = MagicMock()
            resp.json.return_value = {"data": [{"url": "http://x"}]}
            resp.raise_for_status = MagicMock()
            return resp
        dl = MagicMock(); dl.content = b"x"; dl.raise_for_status = MagicMock()
        with patch("requests.post", side_effect=fake_post), \
             patch("requests.get", return_value=dl):
            p.generate("test", negative_prompt="blurry")
        self.assertIn("negative_prompt", captured["body"]["image_request"])

    def test_default_model(self):
        self.assertEqual(IdeogramProvider.DEFAULT_MODEL, "V_3")

    def test_missing_sdk_raises(self):
        with patch.dict("sys.modules", {"requests": None}):
            with self.assertRaises(ImportError):
                IdeogramProvider(api_key="x")


# ---------------------------------------------------------------------------
# LeonardoProvider
# ---------------------------------------------------------------------------

class TestLeonardoProvider(unittest.TestCase):

    def _make_provider(self):
        p = LeonardoProvider.__new__(LeonardoProvider)
        p.api_key = "test-uuid-key"
        p.model = LeonardoProvider.DEFAULT_MODEL
        p.POLL_INTERVAL = 0  # kein Sleep in Tests
        p.POLL_TIMEOUT  = 30
        return p

    def test_generate_returns_image_result(self):
        p = self._make_provider()
        create_resp = MagicMock()
        create_resp.raise_for_status = MagicMock()
        create_resp.json.return_value = {
            "sdGenerationJob": {"generationId": "gen-123"}
        }
        poll_resp = MagicMock()
        poll_resp.raise_for_status = MagicMock()
        poll_resp.json.return_value = {
            "generations_by_pk": {
                "status": "COMPLETE",
                "generated_images": [{"url": "https://cdn.leonardo.ai/img.png"}],
            }
        }
        import requests as _req_mod
        with patch("requests.post", return_value=create_resp), \
             patch("requests.get",  return_value=poll_resp), \
             patch("time.sleep"):
            result = p.generate("a landscape")
        self.assertIsInstance(result, ImageResult)
        self.assertEqual(result.provider, "leonardo")
        self.assertEqual(result.images[0].url, "https://cdn.leonardo.ai/img.png")

    def test_failed_status_raises(self):
        p = self._make_provider()
        create_resp = MagicMock()
        create_resp.raise_for_status = MagicMock()
        create_resp.json.return_value = {"sdGenerationJob": {"generationId": "gen-x"}}
        poll_resp = MagicMock()
        poll_resp.raise_for_status = MagicMock()
        poll_resp.json.return_value = {"generations_by_pk": {"status": "FAILED"}}
        with patch("requests.post", return_value=create_resp), \
             patch("requests.get",  return_value=poll_resp), \
             patch("time.sleep"):
            with self.assertRaises(ValueError):
                p.generate("test")

    def test_timeout_raises(self):
        p = self._make_provider()
        p.POLL_TIMEOUT = -1  # sofort Timeout
        create_resp = MagicMock()
        create_resp.raise_for_status = MagicMock()
        create_resp.json.return_value = {"sdGenerationJob": {"generationId": "gen-y"}}
        with patch("requests.post", return_value=create_resp), \
             patch("time.sleep"):
            with self.assertRaises(TimeoutError):
                p.generate("test")

    def test_default_model(self):
        self.assertEqual(LeonardoProvider.DEFAULT_MODEL,
                         "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3")

    def test_missing_sdk_raises(self):
        with patch.dict("sys.modules", {"requests": None}):
            with self.assertRaises(ImportError):
                LeonardoProvider(api_key="x")


# ---------------------------------------------------------------------------
# FireflyProvider
# ---------------------------------------------------------------------------

class TestFireflyProvider(unittest.TestCase):

    def _make_provider(self, model="firefly-image-model-3"):
        p = FireflyProvider.__new__(FireflyProvider)
        p.client_id     = "test-client-id"
        p.client_secret = "test-client-secret"
        p.model         = model
        p._token        = "cached-token"
        return p

    def test_generate_returns_image_result(self):
        p = self._make_provider()
        fake_bytes = b"firefly-image"
        gen_resp = MagicMock()
        gen_resp.raise_for_status = MagicMock()
        gen_resp.json.return_value = {
            "outputs": [{"image": {"presignedUrl": "https://firefly.adobe.io/img.png"}}]
        }
        dl_resp = MagicMock()
        dl_resp.content = fake_bytes
        dl_resp.raise_for_status = MagicMock()
        with patch("requests.post", return_value=gen_resp), \
             patch("requests.get",  return_value=dl_resp):
            result = p.generate("a mountain")
        self.assertIsInstance(result, ImageResult)
        self.assertEqual(result.provider, "firefly")
        expected_b64 = base64.b64encode(fake_bytes).decode()
        self.assertEqual(result.images[0].b64_json, expected_b64)

    def test_token_fetched_when_not_cached(self):
        p = self._make_provider()
        p._token = None  # Token noch nicht gecacht
        token_resp = MagicMock()
        token_resp.raise_for_status = MagicMock()
        token_resp.json.return_value = {"access_token": "new-token"}
        gen_resp = MagicMock()
        gen_resp.raise_for_status = MagicMock()
        gen_resp.json.return_value = {
            "outputs": [{"image": {"presignedUrl": "https://x"}}]
        }
        dl_resp = MagicMock(); dl_resp.content = b"x"; dl_resp.raise_for_status = MagicMock()
        with patch("requests.post", side_effect=[token_resp, gen_resp]), \
             patch("requests.get", return_value=dl_resp):
            p.generate("test")
        self.assertEqual(p._token, "new-token")

    def test_no_outputs_raises(self):
        p = self._make_provider()
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json.return_value = {"outputs": []}
        with patch("requests.post", return_value=resp):
            with self.assertRaises(ValueError):
                p.generate("test")

    def test_default_model(self):
        self.assertEqual(FireflyProvider.DEFAULT_MODEL, "firefly-image-model-3")

    def test_missing_sdk_raises(self):
        with patch.dict("sys.modules", {"requests": None}):
            with self.assertRaises(ImportError):
                FireflyProvider(client_id="x", client_secret="y")


# ---------------------------------------------------------------------------
# Auto1111Provider
# ---------------------------------------------------------------------------

class TestAuto1111Provider(unittest.TestCase):

    def _make_provider(self, model="", base_url="http://127.0.0.1:7860"):
        p = Auto1111Provider.__new__(Auto1111Provider)
        p.model    = model
        p.base_url = base_url
        return p

    def test_generate_returns_image_result(self):
        p = self._make_provider()
        fake_b64 = base64.b64encode(b"fake-sd-image").decode()
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json.return_value = {"images": [fake_b64]}
        with patch("requests.post", return_value=resp):
            result = p.generate("a cat")
        self.assertIsInstance(result, ImageResult)
        self.assertEqual(result.provider, "auto1111")
        self.assertEqual(result.images[0].b64_json, fake_b64)

    def test_model_switch_called(self):
        p = self._make_provider(model="juggernautXL")
        txt2img_resp = MagicMock()
        txt2img_resp.raise_for_status = MagicMock()
        txt2img_resp.json.return_value = {"images": [base64.b64encode(b"x").decode()]}
        options_resp = MagicMock()
        options_resp.raise_for_status = MagicMock()
        calls = []
        def fake_post(url, **kwargs):
            calls.append(url)
            if "options" in url:
                return options_resp
            return txt2img_resp
        with patch("requests.post", side_effect=fake_post):
            p.generate("a dog")
        self.assertTrue(any("options" in c for c in calls))
        self.assertTrue(any("txt2img" in c for c in calls))

    def test_no_model_no_options_call(self):
        p = self._make_provider(model="")  # kein Modell → kein OPTIONS-Call
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json.return_value = {"images": [base64.b64encode(b"x").decode()]}
        with patch("requests.post", return_value=resp) as mock_post:
            p.generate("test")
        # Nur ein POST-Call (txt2img), kein options-Call
        self.assertEqual(mock_post.call_count, 1)
        self.assertIn("txt2img", mock_post.call_args[0][0])

    def test_empty_response_raises(self):
        p = self._make_provider()
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json.return_value = {"images": []}
        with patch("requests.post", return_value=resp):
            with self.assertRaises(ValueError):
                p.generate("test")

    def test_default_base_url(self):
        self.assertEqual(Auto1111Provider.DEFAULT_BASE_URL, "http://127.0.0.1:7860")

    def test_missing_sdk_raises(self):
        with patch.dict("sys.modules", {"requests": None}):
            with self.assertRaises(ImportError):
                Auto1111Provider()


# ---------------------------------------------------------------------------
# OllamaDiffuserProvider
# ---------------------------------------------------------------------------

class TestOllamaDiffuserProvider(unittest.TestCase):

    def _make_provider(self, model="flux.1-schnell"):
        p = OllamaDiffuserProvider.__new__(OllamaDiffuserProvider)
        p.model    = model
        p.base_url = "http://localhost:8000"
        return p

    def test_generate_returns_image_result(self):
        p = self._make_provider()
        fake_bytes = b"flux-image-bytes"
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.content = fake_bytes
        with patch("requests.post", return_value=resp):
            result = p.generate("a flower")
        self.assertIsInstance(result, ImageResult)
        self.assertEqual(result.provider, "ollamadiffuser")
        self.assertEqual(result.images[0].b64_json,
                         base64.b64encode(fake_bytes).decode())

    def test_n_images_makes_n_calls(self):
        p = self._make_provider()
        resp = MagicMock(); resp.raise_for_status = MagicMock(); resp.content = b"x"
        with patch("requests.post", return_value=resp) as mock_post:
            p.generate("test", n=3)
        self.assertEqual(mock_post.call_count, 3)

    def test_negative_prompt_in_payload(self):
        p = self._make_provider()
        captured = {}
        def fake_post(url, json, timeout):
            captured["json"] = json
            r = MagicMock(); r.raise_for_status = MagicMock(); r.content = b"x"
            return r
        with patch("requests.post", side_effect=fake_post):
            p.generate("test", negative_prompt="ugly")
        self.assertEqual(captured["json"]["negative_prompt"], "ugly")

    def test_default_model(self):
        self.assertEqual(OllamaDiffuserProvider.DEFAULT_MODEL, "flux.1-schnell")

    def test_missing_sdk_raises(self):
        with patch.dict("sys.modules", {"requests": None}):
            with self.assertRaises(ImportError):
                OllamaDiffuserProvider()


# ---------------------------------------------------------------------------
# build_provider / Factory
# ---------------------------------------------------------------------------

class TestBuildProvider(unittest.TestCase):

    CONFIG = {
        "providers": {
            "openai":          {"api_key": "sk-test",       "model": "dall-e-3"},
            "stability":       {"api_key": "sk-stab-test",  "model": "core"},
            "fal":             {"api_key": "fal-test",      "model": "fal-ai/flux/dev"},
            "ideogram":        {"api_key": "ideo-test",     "model": "V_3"},
            "leonardo":        {"api_key": "leo-test",      "model": "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3"},
            "firefly":         {"client_id": "cid", "client_secret": "csec", "model": "firefly-image-model-3"},
            "auto1111":        {"base_url": "http://127.0.0.1:7860", "model": ""},
            "ollamadiffuser":  {"base_url": "http://localhost:8000",  "model": "flux.1-schnell"},
        }
    }

    def test_build_openai(self):
        with patch.dict("sys.modules", {"openai": MagicMock()}):
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

    def test_build_ideogram(self):
        with patch.dict("sys.modules", {"requests": MagicMock()}):
            p = build_provider("ideogram", self.CONFIG)
        self.assertIsInstance(p, IdeogramProvider)

    def test_build_leonardo(self):
        with patch.dict("sys.modules", {"requests": MagicMock()}):
            p = build_provider("leonardo", self.CONFIG)
        self.assertIsInstance(p, LeonardoProvider)

    def test_build_firefly(self):
        with patch.dict("sys.modules", {"requests": MagicMock()}):
            p = build_provider("firefly", self.CONFIG)
        self.assertIsInstance(p, FireflyProvider)
        self.assertEqual(p.client_id, "cid")

    def test_build_firefly_missing_credentials_raises(self):
        cfg = {"providers": {"firefly": {"model": "firefly-image-model-3"}}}
        with self.assertRaises(ValueError):
            build_provider("firefly", cfg)

    def test_build_auto1111(self):
        with patch.dict("sys.modules", {"requests": MagicMock()}):
            p = build_provider("auto1111", self.CONFIG)
        self.assertIsInstance(p, Auto1111Provider)
        self.assertEqual(p.base_url, "http://127.0.0.1:7860")

    def test_build_ollamadiffuser(self):
        with patch.dict("sys.modules", {"requests": MagicMock()}):
            p = build_provider("ollamadiffuser", self.CONFIG)
        self.assertIsInstance(p, OllamaDiffuserProvider)
        self.assertEqual(p.model, "flux.1-schnell")

    def test_model_override(self):
        with patch.dict("sys.modules", {"openai": MagicMock()}):
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
