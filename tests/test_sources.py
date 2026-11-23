import tempfile
import unittest
from pathlib import Path
from energy_policy_llm.sources import html_to_text, save_snapshot, validate_source_url


class SourceTests(unittest.TestCase):
    def test_extract_text_ignores_script(self):
        result = html_to_text("<h1>17.9.571.8</h1><script>bad()</script><p>RPS 50%</p>")
        self.assertIn("RPS 50%", result)
        self.assertNotIn("bad()", result)

    def test_allowlist_official(self):
        validate_source_url("https://www.srca.nm.gov/parts/title17/17.009.0572.html")
        with self.assertRaises(ValueError):
            validate_source_url("https://example.com/anything")

    def test_insecure_rejected(self):
        with self.assertRaises(ValueError):
            validate_source_url("http://www.srca.nm.gov/test")

    def test_frozen_snapshot(self):
        with tempfile.TemporaryDirectory() as d:
            meta = save_snapshot("sample", "https://www.srca.nm.gov/example",
                                 "<p>RECs and retail sales.</p>", d)
            self.assertEqual(meta["gold_status"], "not_annotated")
            self.assertIn("RECs", (Path(d) / "sample.txt").read_text())
            with self.assertRaises(FileExistsError):
                save_snapshot("sample", "https://www.srca.nm.gov/example", "<p>Changed</p>", d)

    def test_bad_source_id(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                save_snapshot("../bad", "https://www.srca.nm.gov/example", "<p>text</p>", d)


if __name__ == "__main__":
    unittest.main()
