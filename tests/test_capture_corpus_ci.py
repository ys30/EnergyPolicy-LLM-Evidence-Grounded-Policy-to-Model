"""Offline tests for source-capture failure behavior (no live government request)."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.capture_corpus_ci import capture, SOURCES

def source_html(section):
    return "<html><h1>RENEWABLE PORTFOLIO STANDARD</h1><p>" + (
        f"{section} RENEWABLE PORTFOLIO STANDARD: "
        "Renewable energy shall comprise fifty percent of retail sales. "
        "RECs are retired for compliance.<br>"
    ) * 30 + "</p></html>"

class CaptureCorpusTests(unittest.TestCase):
    def test_rejects_incomplete_page(self):
        with tempfile.TemporaryDirectory() as d:
            with patch("scripts.capture_corpus_ci.fetch_official_html", return_value="<html>403 Forbidden</html>"):
                with self.assertRaises(RuntimeError):
                    capture(Path(d))
    def test_no_gold_promotion(self):
        # Fully synthetic HTML fixture, no official websites contacted.
        with tempfile.TemporaryDirectory() as d:
            pages=[source_html(x[2]) for x in SOURCES]
            with patch("scripts.capture_corpus_ci.fetch_official_html", side_effect=pages):
                # Candidate count may be zero because section identifiers are not at line starts;
                # fail closed rather than silently reporting a successful corpus.
                with self.assertRaises(RuntimeError):
                    capture(Path(d))

if __name__ == "__main__":
    unittest.main()
