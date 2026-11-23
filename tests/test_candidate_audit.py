import unittest
from energy_policy_llm.candidates import extract_candidates
from energy_policy_llm.candidate_audit import audit_snapshot

class CandidateAuditTests(unittest.TestCase):
    def test_uncapped_collects_over_200(self):
        text = "17.9.572.8 RENEWABLE PORTFOLIO STANDARD:\n" + "".join(
            f"A. Renewable retail sales obligation clause {i}.\n" for i in range(240))
        audit = audit_snapshot(text, "NM_IOU_2023", "2023")
        self.assertEqual(audit["candidate_count_uncapped"], 241)
        self.assertEqual(audit["new_candidates_beyond_200"], 41)
        self.assertEqual(audit["keyword_lines_inside_sections_uncovered_count"], 0)
        self.assertEqual(len(extract_candidates(text,"nm","2023",limit=200)), 200)
    def test_presection_keyword_detected(self):
        text = ("Renewable portfolio overview.\n"
                "17.9.571.8 RENEWABLE PORTFOLIO STANDARD:\n"
                "A. Retail sales of renewable power are regulated.\n")
        audit = audit_snapshot(text, "nm", "2025")
        self.assertEqual(audit["keyword_lines_outside_matched_sections_count"], 1)
        self.assertEqual(audit["keyword_lines_inside_sections_uncovered_count"], 0)
    def test_short_keyword_line_is_flagged(self):
        text = "17.9.571.8 RENEWABLE PORTFOLIO STANDARD:\nREC cost\n"
        audit = audit_snapshot(text,"nm","2025")
        self.assertEqual(audit["keyword_lines_inside_sections_uncovered_count"], 1)
    def test_incomplete_nonlexical_clause_not_claimed_complete(self):
        audit = audit_snapshot("17.9.571.8 RENEWABLE PORTFOLIO STANDARD:\nA. It shall do so.", "nm", "2025")
        self.assertTrue(audit["requires_manual_review"])
if __name__=="__main__":
    unittest.main()
