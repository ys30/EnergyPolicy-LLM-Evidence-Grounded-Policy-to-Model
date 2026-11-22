import unittest
from dataclasses import replace
from energy_policy_llm.evidence import (
    Evidence, EvidenceStatus, PolicyObligation, Decision, determine_generation_mapping
)


def policy(denominator="retail_electricity_sales", status=EvidenceStatus.HUMAN_REVIEW_PENDING,
           accounting="certificate_accounting", numerator="eligible_renewables"):
    ev = Evidence("https://example.org/rule", "section 1", "2026-edition", "2026-11-22",
                  status, "Verified clause snippet" if status == EvidenceStatus.CLAUSE_VERIFIED else None)
    return PolicyObligation("case", "CA", "retail sellers", .6, "2030-12-31",
                            numerator, denominator, accounting, ev)


class EvidenceContractTests(unittest.TestCase):
    def test_retail_abstains_by_default(self):
        self.assertEqual(determine_generation_mapping(policy())[0], Decision.ABSTAIN)

    def test_retail_proxy_is_not_legal(self):
        self.assertEqual(determine_generation_mapping(policy(), allow_illustrative_proxy=True)[0], Decision.SCENARIO_PROXY)

    def test_non_renewable_target_not_proxied(self):
        self.assertEqual(determine_generation_mapping(policy(numerator="zero_carbon"), allow_illustrative_proxy=True)[0], Decision.ABSTAIN)

    def test_unreviewed_generation_abstains(self):
        self.assertEqual(determine_generation_mapping(policy(denominator="local_generation"))[0], Decision.ABSTAIN)

    def test_audited_generation_can_compile(self):
        p = policy("local_generation", EvidenceStatus.CLAUSE_VERIFIED, "physical_generation_no_credits")
        self.assertEqual(determine_generation_mapping(p)[0], Decision.LEGAL_CONSTRAINT)

    def test_verified_but_credit_accounting_abstains(self):
        p = policy("local_generation", EvidenceStatus.CLAUSE_VERIFIED)
        self.assertEqual(determine_generation_mapping(p)[0], Decision.ABSTAIN)

    def test_verified_evidence_without_quote_invalid(self):
        p = policy()
        p = replace(p, evidence=replace(p.evidence, status=EvidenceStatus.CLAUSE_VERIFIED))
        with self.assertRaises(ValueError):
            determine_generation_mapping(p)

    def test_target_range_validation(self):
        with self.assertRaises(ValueError):
            determine_generation_mapping(replace(policy(), target_fraction=1.1))

    def test_non_https_evidence_invalid(self):
        p = policy()
        p = replace(p, evidence=replace(p.evidence, document_url="http://insecure.test"))
        with self.assertRaises(ValueError):
            determine_generation_mapping(p)


if __name__ == "__main__":
    unittest.main()
