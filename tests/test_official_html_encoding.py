"""Test legacy official HTML decoding without any outbound HTTP request."""
import unittest
from unittest.mock import patch
from email.message import Message
from energy_policy_llm.sources import fetch_official_html, html_to_text

class Response:
    def __init__(self, raw, declared="utf-8"):
        self.raw = raw
        self.headers = Message()
        self.headers["Content-Type"] = "text/html; charset=" + declared
    def geturl(self):
        return "https://www.srca.nm.gov/wp-content/uploads/2025/06/17.9.571.html"
    def read(self, n=-1):
        return self.raw[:n]
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False

class OfficialHtmlEncodingTests(unittest.TestCase):
    def test_windows_1252_html_fallback(self):
        html = "<p>17.9.571.8  RENEWABLE PORTFOLIO STANDARD:— definition of ‘retail sales’</p>"
        raw = html.encode("cp1252")
        with patch("energy_policy_llm.sources.urlopen", return_value=Response(raw)):
            decoded = fetch_official_html("https://www.srca.nm.gov/wp-content/uploads/2025/06/17.9.571.html")
        self.assertIn("—", decoded)
        self.assertNotIn("\ufffd", decoded)
        self.assertIn("17.9.571.8", html_to_text(decoded))
    def test_strict_utf8(self):
        with patch("energy_policy_llm.sources.urlopen", return_value=Response("<p>Résumé</p>".encode("utf8"))):
            output = fetch_official_html("https://www.srca.nm.gov/wp-content/uploads/2025/06/17.9.571.html")
        self.assertIn("Résumé", output)

if __name__ == "__main__":
    unittest.main()
