import unittest
from dataclasses import dataclass
from energy_policy_llm.field_semantic_screen import screen_field_semantics

@dataclass(frozen=True)
class Draft:
    entity_id: str = "distribution_cooperative"
    year: int = 2030
    target_fraction: float = .5
    metric: str = "ELIGIBLE_RENEWABLE_RETAIL_SALES"
    legal_type: str = "TARGET"
    condition_operator: str = "NONE"
    condition_ids: tuple[str,...] = ()
    provision: str = "17.9.571.8"

class SemanticRiskTests(unittest.TestCase):
    def check(self, candidate, fields):
        return {f.code for f in screen_field_semantics(candidate,evidence_text_by_field=fields)}

    def test_correct_visible_support_is_not_legal_confirmation(self):
        flags=self.check(Draft(),{
            "entity_id":"distribution cooperative",
            "metric":"New Mexico retail sales",
            "target_fraction":"fifty percent",
            "year":"2030"})
        self.assertEqual(flags,set())

    def test_wrong_fraction_and_year(self):
        flags=self.check(Draft(),{
            "entity_id":"distribution cooperative",
            "metric":"retail sales",
            "target_fraction":"forty percent",
            "year":"2050"})
        self.assertIn("FRACTION_QUOTE_MISMATCH",flags)
        self.assertIn("YEAR_QUOTE_MISMATCH",flags)

    def test_wrong_denominator_and_entity(self):
        flags=self.check(Draft(),{
            "entity_id":"New Mexico",
            "metric":"local total generation",
            "target_fraction":"50%",
            "year":"2030"})
        self.assertIn("ENTITY_SUPPORT_NOT_VISIBLE",flags)
        self.assertIn("RETAIL_DENOMINATOR_NOT_SUPPORTED",flags)

    def test_all_conditions_must_be_explicit(self):
        d=Draft(year=2050,target_fraction=.8,legal_type="CONDITIONAL_TARGET",
                condition_operator="ALL",
                condition_ids=("technical","reliability","affordability"))
        flags=self.check(d,{"entity_id":"distribution cooperative",
                            "metric":"retail sales",
                            "target_fraction":"eighty percent",
                            "year":"2050",
                            "condition_ids":"reliability and affordability"})
        self.assertIn("CONDITION_SUPPORT_NOT_VISIBLE:technical",flags)

    def test_suspicious_original_cross_reference_is_not_rewritten(self):
        d=Draft(provision="17.9.571.11(D)")
        flags=self.check(d,{"entity_id":"distribution cooperative",
                            "metric":"retail sales","target_fraction":"50%","year":"2030",
                            "reference":"17.9.571.13(E)"})
        self.assertIn("SUSPECT_CROSS_REFERENCE",flags)

if __name__=="__main__":
    unittest.main()
