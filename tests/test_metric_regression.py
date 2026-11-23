"""Regression tests for the policy-safety metric denominator and data-mode separation."""
import unittest
from energy_policy_llm.benchmark import Case, evaluate

FIELDS = dict(target_fraction=.5, target_date="2030-01-01",
              obligated_entities="utilities", numerator="eligible_renewables",
              denominator="retail_sales")

def make(n, gold, predicted, status="synthetic"):
    return Case(str(n), "instrument-"+str(n), "NM", "test", status,
                FIELDS, gold, FIELDS, predicted)

class MetricRegressionTests(unittest.TestCase):
    def test_conditional_unsafe_rate(self):
        result = evaluate([
            make(1, "ABSTAIN", "LEGAL_CONSTRAINT"),
            make(2, "LEGAL_CONSTRAINT", "LEGAL_CONSTRAINT")
        ], allow_synthetic=True)
        self.assertEqual(result["unsafe_accept_rate"], .5)
        self.assertEqual(result["unsafe_accept_rate_at_risk"], 1.)
        self.assertEqual(result["at_risk_count"], 1)

    def test_zero_at_risk_is_null(self):
        result = evaluate([make(1, "LEGAL_CONSTRAINT", "LEGAL_CONSTRAINT")],
                          allow_synthetic=True)
        self.assertIsNone(result["unsafe_accept_rate_at_risk"])

    def test_no_human_gold_in_synthetic_mode(self):
        with self.assertRaises(ValueError):
            evaluate([make(1,"ABSTAIN","ABSTAIN",status="adjudicated")],allow_synthetic=True)

    def test_no_synthetic_in_empirical_mode(self):
        with self.assertRaises(ValueError):
            evaluate([make(1,"ABSTAIN","ABSTAIN")],allow_synthetic=False)

    def test_unsafe_count(self):
        result=evaluate([make(1,"ABSTAIN","LEGAL_CONSTRAINT")],allow_synthetic=True)
        self.assertEqual(result["unsafe_accept_count"],1)

if __name__ == "__main__":
    unittest.main()
