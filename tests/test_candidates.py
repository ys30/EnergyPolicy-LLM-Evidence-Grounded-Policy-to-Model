import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from energy_policy_llm.candidates import extract_candidates, verify_candidates, export_candidates

TEXT = """17.9.571.8 RENEWABLE PORTFOLIO STANDARD:
A. A distribution cooperative shall demonstrate compliance by renewable energy certificates.
C. By 2030, no less than fifty percent of retail sales shall use renewable energy.
17.9.571.10 REASONABLE COST THRESHOLD:
A. A cooperative shall not incur excessive renewable cost.
"""

class CandidateTests(unittest.TestCase):
    def test_exact_offsets(self):
        items = extract_candidates(TEXT, "nm-coop", "2025-06-24")
        self.assertGreaterEqual(len(items), 3)
        verify_candidates(items, TEXT)
        self.assertIn("17.9.571.10", {item.provision for item in items})

    def test_mutation_detection(self):
        items = extract_candidates(TEXT, "nm", "2025")
        with self.assertRaises(ValueError):
            verify_candidates(items, TEXT + "changed")
        with self.assertRaises(ValueError):
            verify_candidates([replace(items[0], exact_text="invented")] + items[1:], TEXT)

    def test_no_gold_promotion(self):
        items = extract_candidates(TEXT, "nm", "2025")
        with self.assertRaises(ValueError):
            verify_candidates([replace(items[0], status="adjudicated")], TEXT)

    def test_empty_source(self):
        self.assertEqual(extract_candidates("Nothing relevant", "nm", "2025"), [])

    def test_write_once(self):
        items = extract_candidates(TEXT, "nm", "2025")
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "candidates.json"
            export_candidates(items, path)
            self.assertTrue(path.exists())
            with self.assertRaises(FileExistsError):
                export_candidates(items, path)

    def test_limit(self):
        self.assertEqual(len(extract_candidates(TEXT, "nm", "2025", limit=1)), 1)

if __name__ == "__main__":
    unittest.main()
