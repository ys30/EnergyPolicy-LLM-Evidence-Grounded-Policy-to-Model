"""Offline source-capture tests; every HTML example here is synthetic."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.capture_corpus_ci import capture, SOURCES

def source_html(section):
    chunks=[f"<p>{section} RENEWABLE PORTFOLIO STANDARD:</p>"]
    chunks += ["<p>A. Renewable energy shall comprise fifty percent of retail sales; RECs must be retired.</p>" for _ in range(60)]
    return "<html><body>" + "".join(chunks) + "</body></html>"

class CaptureCorpusTests(unittest.TestCase):
    def test_rejects_incomplete_page(self):
        with tempfile.TemporaryDirectory() as d:
            with patch("scripts.capture_corpus_ci.fetch_official_html", return_value="<html>403 Forbidden</html>"):
                with self.assertRaises(RuntimeError):
                    capture(Path(d))

    def test_synthetic_source_never_promoted_to_gold(self):
        with tempfile.TemporaryDirectory() as d:
            pages=[source_html(x[2]) for x in SOURCES]
            with patch("scripts.capture_corpus_ci.fetch_official_html", side_effect=pages):
                manifest=capture(Path(d))
            self.assertEqual(manifest["gold_count"],0)
            self.assertEqual(len(manifest["sources"]),2)
            for source in manifest["sources"]:
                self.assertGreater(source["candidate_count"],0)
                self.assertEqual(source["gold_status"],"unreviewed")
                data=json.loads((Path(d)/source["candidate_file"]).read_text())
                self.assertTrue(all(item["status"]=="candidate_unreviewed" for item in data))

if __name__ == "__main__":
    unittest.main()
