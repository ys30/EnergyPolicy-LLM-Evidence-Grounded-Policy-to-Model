"""Realistic wrapped section references should not split official chapter bounds."""
import unittest
from energy_policy_llm.candidates import SECTION, extract_candidates
from energy_policy_llm.candidate_audit import audit_snapshot

DOC = """17.9.572.16\u00a0 CUSTOMERS QUALIFIED PURSUANT TO SECTION:
A. Renewable electricity purchases follow section rules.
C. Rule
17.9.572.16 NMAC only exempts customers from certain renewable costs.
A utility may document its renewable compliance as provided in
17.9.572.19 NMAC, documenting retirement of renewable certificates.
17.9.572.17\u00a0 CERTIFICATE TRACKING SYSTEM:
A. Renewable certificates must be registered.
17.9.572.18\u00a0 VOLUNTARY RENEWABLE TARIFFS:
A. Cooperative and utility retail purchases.
17.9.572.19\u00a0 ANNUAL RENEWABLE ENERGY PORTFOLIO REPORT:
A. Renewable compliance report.
"""
class SectionHeadingCrossrefTests(unittest.TestCase):
    def test_wrapped_nmac_references_are_not_headings(self):
        headings=[x.group(1) for x in SECTION.finditer(DOC)]
        self.assertEqual(headings,["17.9.572.16","17.9.572.17","17.9.572.18","17.9.572.19"])
    def test_audit_order_and_duplicates(self):
        result=audit_snapshot(DOC,"NM_IOU","2023")
        self.assertTrue(result["heading_order_valid"])
        self.assertEqual(result["duplicate_heading_ids"],[])
        self.assertEqual(result["nonincreasing_section_ids"],[])
        self.assertEqual(result["keyword_lines_inside_sections_uncovered_count"],0)
    def test_crossref_policy_lines_retained_with_parent_section(self):
        items=extract_candidates(DOC,"NM_IOU","2023")
        matched=[x for x in items if "NMAC only exempts" in x.exact_text]
        self.assertEqual(len(matched),1)
        self.assertEqual(matched[0].provision,"17.9.572.16")
if __name__=="__main__":
    unittest.main()
