"""
Tests für fetch_context_urls().

Keine echten Netzwerkzugriffe — requests.get wird vollständig gemockt.
"""

import sys
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LLM_Client.llm_client import fetch_context_urls

# ---------------------------------------------------------------------------
# Hilfsfunktion: Fake-Response bauen
# ---------------------------------------------------------------------------

def _mock_response(content: bytes | str, content_type: str, status: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status
    resp.headers = {"Content-Type": content_type}
    if isinstance(content, bytes):
        resp.content = content
        resp.text    = content.decode("utf-8", errors="replace")
    else:
        resp.content = content.encode("utf-8")
        resp.text    = content
    resp.raise_for_status = MagicMock()
    return resp


# ---------------------------------------------------------------------------
# Kein URL-Inhalt
# ---------------------------------------------------------------------------

class TestNoUrl(unittest.TestCase):

    def test_empty_string(self):
        self.assertEqual(fetch_context_urls(""), "")

    def test_none_returns_empty(self):
        # None ist kein gültiger Typ, aber Funktion prüft `if not text`
        self.assertEqual(fetch_context_urls(None), None)

    def test_plain_text_without_url(self):
        text = "Kein Link enthalten."
        self.assertEqual(fetch_context_urls(text), text)

    def test_text_with_non_http_url(self):
        text = "Pfad: /home/user/file.pdf"
        self.assertEqual(fetch_context_urls(text), text)


# ---------------------------------------------------------------------------
# Plaintext-URL
# ---------------------------------------------------------------------------

class TestPlainText(unittest.TestCase):

    def test_txt_url_replaced(self):
        mock_resp = _mock_response("Hallo Welt", "text/plain")
        with patch("requests.get", return_value=mock_resp):
            result = fetch_context_urls("Inhalt: https://example.com/file.txt")
        self.assertIn("Hallo Welt", result)
        self.assertIn("example.com", result)
        self.assertNotIn("https://example.com/file.txt Hallo", result)

    def test_multiple_urls(self):
        mock_resp = _mock_response("Text", "text/plain")
        with patch("requests.get", return_value=mock_resp):
            result = fetch_context_urls(
                "A: https://a.com/a.txt und B: https://b.com/b.txt"
            )
        self.assertEqual(result.count("[Inhalt von"), 2)

    def test_trailing_punctuation_stripped_from_url(self):
        """URL darf kein abschließendes Komma oder Punkt enthalten."""
        fetched_urls = []

        def fake_get(url, **kwargs):
            fetched_urls.append(url)
            return _mock_response("ok", "text/plain")

        with patch("requests.get", side_effect=fake_get):
            fetch_context_urls("Siehe https://example.com/file.txt.")

        self.assertTrue(fetched_urls[0].endswith(".txt"))
        self.assertFalse(fetched_urls[0].endswith("."))


# ---------------------------------------------------------------------------
# HTML-URL
# ---------------------------------------------------------------------------

class TestHtmlFetch(unittest.TestCase):

    def test_html_content_type_triggers_extraction(self):
        html = "<html><body><p>Hallo</p><script>js</script></body></html>"
        mock_resp = _mock_response(html, "text/html; charset=utf-8")
        with patch("requests.get", return_value=mock_resp):
            result = fetch_context_urls("Lies https://example.com/page")
        self.assertIn("Hallo", result)
        self.assertNotIn("<p>", result)
        self.assertNotIn("<script>", result)

    def test_html_extension_triggers_extraction(self):
        html = "<html><body>Inhalt</body></html>"
        mock_resp = _mock_response(html, "application/octet-stream")
        with patch("requests.get", return_value=mock_resp):
            result = fetch_context_urls("https://example.com/page.html")
        self.assertIn("Inhalt", result)

    def test_html_fallback_without_beautifulsoup(self):
        """Ohne beautifulsoup4 wird ein simpler Tag-Stripper verwendet."""
        html = "<p>Fallback</p>"
        mock_resp = _mock_response(html, "text/html")
        with patch("requests.get", return_value=mock_resp):
            with patch.dict("sys.modules", {"bs4": None}):
                result = fetch_context_urls("https://example.com/")
        self.assertIn("Fallback", result)
        self.assertNotIn("<p>", result)


# ---------------------------------------------------------------------------
# PDF-URL
# ---------------------------------------------------------------------------

class TestPdfFetch(unittest.TestCase):

    def _make_fake_pypdf(self, pages_text: list[str]):
        """Erstellt ein Mock-pypdf-Modul mit gegebenen Seitentexten."""
        mock_pypdf = MagicMock()
        mock_page_objects = []
        for text in pages_text:
            p = MagicMock()
            p.extract_text.return_value = text
            mock_page_objects.append(p)
        mock_pypdf.PdfReader.return_value.pages = mock_page_objects
        return mock_pypdf

    def test_pdf_content_type_triggers_extraction(self):
        mock_resp = _mock_response(b"%PDF-fake", "application/pdf")
        fake_pypdf = self._make_fake_pypdf(["Seite 1 Text", "Seite 2 Text"])
        with patch("requests.get", return_value=mock_resp):
            with patch.dict("sys.modules", {"pypdf": fake_pypdf}):
                result = fetch_context_urls("https://example.com/doc")
        self.assertIn("Seite 1 Text", result)
        self.assertIn("Seite 2 Text", result)

    def test_pdf_extension_triggers_extraction(self):
        mock_resp = _mock_response(b"%PDF-fake", "application/octet-stream")
        fake_pypdf = self._make_fake_pypdf(["PDF-Inhalt"])
        with patch("requests.get", return_value=mock_resp):
            with patch.dict("sys.modules", {"pypdf": fake_pypdf}):
                result = fetch_context_urls("https://example.com/report.pdf")
        self.assertIn("PDF-Inhalt", result)

    def test_pdf_missing_pypdf_shows_error(self):
        mock_resp = _mock_response(b"%PDF-fake", "application/pdf")
        with patch("requests.get", return_value=mock_resp):
            with patch.dict("sys.modules", {"pypdf": None}):
                result = fetch_context_urls("https://example.com/report.pdf")
        self.assertIn("Fehler", result)
        self.assertIn("pypdf", result)

    def test_empty_pdf_pages_skipped(self):
        mock_resp = _mock_response(b"%PDF", "application/pdf")
        fake_pypdf = self._make_fake_pypdf(["", "Nur Seite 2", ""])
        with patch("requests.get", return_value=mock_resp):
            with patch.dict("sys.modules", {"pypdf": fake_pypdf}):
                result = fetch_context_urls("https://example.com/doc.pdf")
        self.assertIn("Nur Seite 2", result)


# ---------------------------------------------------------------------------
# Fehlerfälle
# ---------------------------------------------------------------------------

class TestErrors(unittest.TestCase):

    def test_network_error_replaced_with_message(self):
        import requests as req_mod
        with patch("requests.get", side_effect=req_mod.exceptions.ConnectionError("offline")):
            result = fetch_context_urls("Lies https://unreachable.example.com/file.txt bitte.")
        self.assertIn("Fehler beim Laden", result)
        self.assertIn("unreachable.example.com", result)

    def test_http_error_replaced_with_message(self):
        mock_resp = _mock_response(b"Not Found", "text/plain", status=404)
        mock_resp.raise_for_status.side_effect = Exception("404 Not Found")
        with patch("requests.get", return_value=mock_resp):
            result = fetch_context_urls("https://example.com/missing.txt")
        self.assertIn("Fehler", result)

    def test_requests_not_installed_shows_install_hint(self):
        with patch.dict("sys.modules", {"requests": None}):
            result = fetch_context_urls("https://example.com/file.txt")
        self.assertIn("Fehler", result)
        self.assertIn("requests", result)

    def test_text_before_and_after_url_preserved(self):
        mock_resp = _mock_response("Dokumentinhalt", "text/plain")
        with patch("requests.get", return_value=mock_resp):
            result = fetch_context_urls("Vortext https://example.com/doc.txt Nachtext")
        self.assertIn("Vortext", result)
        self.assertIn("Nachtext", result)
        self.assertIn("Dokumentinhalt", result)


if __name__ == "__main__":
    unittest.main()
