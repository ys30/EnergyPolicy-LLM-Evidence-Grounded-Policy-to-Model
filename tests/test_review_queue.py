import unittest
from energy_policy_llm.review_queue import make_review_queue

TEXT = """17.9.571.7 DEFINITIONS:
A. Distribution cooperative is a defined utility entity.
17.9.571.8 RENEWABLE PORTFOLIO STANDARD:
A. Renewable certificates demonstrate compliance.
C. By 2030 fifty percent of retail sales.
17.9.571.10 REASONABLE COST THRESHOLD:
A. Renewable energy reasonable cost threshold applies.
"""

class ReviewQueueTests(unittest.TestCase):
    def test_priority_sections_and_offsets(self):
        queue=make_review_queue(TEXT,"NM_COOP","2025")
        self.assertEqual(queue["section_count"],3)
        self.assertEqual(queue["priority_section_count"],3)
        self.assertEqual(queue["gold_count"],0)
        for section in queue["sections"]:
            self.assertEqual(TEXT[section["section_start_char"]:section["section_end_char"]],section["section_text"])
            self.assertEqual(section["status"],"unreviewed_requires_independent_annotation")
    def test_candidate_spans_within_section(self):
        q=make_review_queue(TEXT,"NM_COOP","2025")
        for s in q["sections"]:
            for span in s["candidate_spans"]:
                self.assertTrue(s["section_start_char"] <= span["start_char"] < span["end_char"] <= s["section_end_char"])
if __name__=="__main__":
    unittest.main()
