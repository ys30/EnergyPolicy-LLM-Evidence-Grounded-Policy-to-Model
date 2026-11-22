import unittest
from energy_policy_llm.schema import PolicyTarget, Metric
from energy_policy_llm.compiler import compile_generation_share
from energy_policy_llm.extract import extract_percent_year
from energy_policy_llm.toy_lp import solve_proxy


def target(metric=Metric.RETAIL_SALES_SHARE, legal_review="needs_clause_review"):
    return PolicyTarget("test", "NM", 2030, .5, metric, "public utilities", "https://example.org", legal_review)


class PipelineTests(unittest.TestCase):
    def test_retail_standard_abstains(self):
        self.assertEqual(compile_generation_share(target()).status, "ABSTAIN")

    def test_retail_standard_proxy_not_legal(self):
        dec = compile_generation_share(target(), allow_proxy=True)
        self.assertEqual(dec.status, "PROXY_ONLY")
        self.assertFalse(dec.legal_equivalence)

    def test_clean_standard_not_proxy(self):
        self.assertEqual(compile_generation_share(target(Metric.CLEAN_RETAIL_SALES_SHARE), allow_proxy=True).status, "ABSTAIN")

    def test_verified_generation_share_compiles(self):
        dec = compile_generation_share(target(Metric.GENERATION_SHARE, "clause_verified"))
        self.assertTrue(dec.legal_equivalence)
        self.assertEqual(dec.fraction, .5)

    def test_unverified_generation_share_abstains(self):
        self.assertEqual(compile_generation_share(target(Metric.GENERATION_SHARE)).status, "ABSTAIN")

    def test_extraction_limited_baseline(self):
        self.assertEqual(extract_percent_year("renewables 60% by 2030"), (.6, 2030))
        self.assertIsNone(extract_percent_year("achieve the statutory target"))

    def test_toy_cost_monotonic(self):
        self.assertLessEqual(solve_proxy(0).total_cost_arbitrary_units, solve_proxy(.5).total_cost_arbitrary_units)
        self.assertLessEqual(solve_proxy(.5).total_cost_arbitrary_units, solve_proxy(.8).total_cost_arbitrary_units)

    def test_toy_infeasible_over_resource_limit(self):
        with self.assertRaises(ValueError):
            solve_proxy(.95)


if __name__ == "__main__":
    unittest.main()
