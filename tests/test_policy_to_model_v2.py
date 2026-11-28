import unittest
from dataclasses import replace
from energy_policy_llm.model_profile import synthetic_profile
from energy_policy_llm.policy_ir import PolicyIR, LegalType, MetricV2
from energy_policy_llm.compiler_v2 import compile_policy

SHA = "a" * 64
def target(**changes):
    base = PolicyIR("test-2030", SHA, "17.9.571.8(C)", LegalType.TARGET,
                    MetricV2.RENEWABLE_RETAIL_SALES, "distribution_cooperative",
                    year=2030, target_fraction=0.5, evidence_verified=True)
    return replace(base, **changes)

class CompilerV2Tests(unittest.TestCase):
    def test_no_implicit_retail_sales_to_generation(self):
        out = compile_policy(target(), synthetic_profile())
        self.assertEqual(out.status, "ABSTAIN")
        self.assertIn("retail_sales_mwh", out.missing_data)
        self.assertIsNone(out.expression)

    def test_proxy_requires_explicit_opt_in(self):
        out = compile_policy(target(), synthetic_profile(), allow_proxy=True)
        self.assertEqual(out.status, "SCENARIO_PROXY")
        self.assertFalse(out.legal_equivalence)
        self.assertIn("local_eligible_generation", out.expression)

    def test_full_synthetic_is_not_legal_validation(self):
        out = compile_policy(target(), synthetic_profile(full=True))
        self.assertEqual(out.status, "ABSTAIN")

    def test_adjudicated_reviewed_mapping_plan_only(self):
        profile = replace(synthetic_profile(full=True), reviewed_legal_mapping=True)
        out = compile_policy(target(human_adjudicated=True), profile)
        self.assertEqual(out.status, "PLAN_ONLY")
        self.assertFalse(out.legal_equivalence)
        self.assertIn("retail_sales_MWh", out.expression)

    def test_conditional_requires_all(self):
        with self.assertRaises(ValueError):
            target(legal_type=LegalType.CONDITIONAL_TARGET, condition_ids=("a","b","c"))
        conditional=target(legal_type=LegalType.CONDITIONAL_TARGET,
                           condition_ids=("technical","reliability","affordability"),
                           condition_operator="ALL", year=2050, target_fraction=.8)
        self.assertEqual(compile_policy(conditional, synthetic_profile(full=True)).status, "ABSTAIN")

    def test_source_ambiguity_overrides_proxy(self):
        self.assertEqual(compile_policy(target(source_ambiguity=True), synthetic_profile(), True).status, "ABSTAIN")

    def test_unverified_source_blocks_proxy(self):
        self.assertEqual(compile_policy(target(evidence_verified=False), synthetic_profile(), True).status, "ABSTAIN")

    def test_entity_year_mismatch(self):
        self.assertEqual(compile_policy(target(entity_id="other"), synthetic_profile(), True).status, "ABSTAIN")
        self.assertEqual(compile_policy(target(year=2040), synthetic_profile(), True).status, "ABSTAIN")

    def test_reporting_not_wrongly_abstained(self):
        reporting=PolicyIR("report",SHA,"17.9.571.13",LegalType.REPORTING,MetricV2.NONE,
                           "distribution_cooperative",evidence_verified=True)
        self.assertEqual(compile_policy(reporting, synthetic_profile()).status,"NOT_DIRECTLY_EXECUTABLE")

    def test_fraction_validation(self):
        for frac in (-.01,1.01,float("nan"),float("inf")):
            with self.subTest(frac=frac), self.assertRaises(ValueError):
                target(target_fraction=frac)

if __name__ == "__main__":
    unittest.main()
