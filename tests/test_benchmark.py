import unittest
from dataclasses import replace
from energy_policy_llm.benchmark import Case, evaluate, validate_splits


def case(case_id="x", instrument_id="instrument-1", split="test", status="synthetic"):
    fields = dict(target_fraction=.5, target_date="2030-01-01", obligated_entities="utilities",
                  numerator="eligible_renewables", denominator="retail_sales")
    return Case(case_id, instrument_id, "NM", split, status, fields, "ABSTAIN", fields.copy(), "ABSTAIN")


class BenchmarkTests(unittest.TestCase):
    def test_synthetic_requires_explicit_flag(self):
        with self.assertRaises(ValueError):
            evaluate([case()])

    def test_synthetic_evaluation(self):
        result = evaluate([case()], allow_synthetic=True)
        self.assertEqual(result["all_fields_exact_match"], 1)
        self.assertEqual(result["unsafe_accept_count"], 0)
        self.assertEqual(result["dataset_status"], "synthetic_fixture")

    def test_instrument_group_leakage(self):
        with self.assertRaises(ValueError):
            validate_splits([case("x", split="train"), case("y", split="test")])

    def test_distinct_instruments_may_split(self):
        validate_splits([case("x", "a", "train"), case("y", "b", "test")])

    def test_unsafe_acceptance_metric(self):
        c = replace(case(), predicted_decision="LEGAL_CONSTRAINT")
        self.assertEqual(evaluate([c], allow_synthetic=True)["unsafe_accept_rate"], 1)

    def test_missing_field_counts_incorrect(self):
        c = replace(case(), predicted_fields={})
        self.assertEqual(evaluate([c], allow_synthetic=True)["all_fields_exact_match"], 0)

    def test_invalid_gold_status(self):
        with self.assertRaises(ValueError):
            evaluate([replace(case(), gold_status="human_review_pending")], allow_synthetic=True)

    def test_empty_eval_rejected(self):
        with self.assertRaises(ValueError):
            evaluate([], allow_synthetic=True)


if __name__ == "__main__":
    unittest.main()
