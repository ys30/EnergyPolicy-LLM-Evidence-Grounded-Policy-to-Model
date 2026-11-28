import unittest
from dataclasses import replace
from energy_policy_llm.rec_accounting import (
    Certificate, AnnualRetailSales, illustrative_annual_balance,
    illustrative_multi_entity_balances)
from energy_policy_llm.pypsa_data_contract import (
    EntityMapping, SimulatedAnnualEnergy, illustrative_generation_share,
    require_verified_mapping)

def cert(id, **kwargs):
    values = {"certificate_id": id, "owner_id": "coop", "vintage_year": 2029,
              "mwh": 30.0, "eligible": True, "retired_by": "coop", "retired_for_year": 2030}
    values.update(kwargs)
    return Certificate(**values)

class RecAccountingTests(unittest.TestCase):
    def test_synthetic_retail_sales_shortfall(self):
        result = illustrative_annual_balance(
            AnnualRetailSales("coop", 2030, 100), [cert("A"), cert("B", mwh=15)], .5)
        self.assertEqual(result.eligible_retired_mwh, 45)
        self.assertEqual(result.illustrative_target_mwh, 50)
        self.assertEqual(result.illustrative_shortfall_mwh, 5)
        self.assertFalse(result.legally_validated)

    def test_prevent_double_counting(self):
        with self.assertRaisesRegex(ValueError, "Duplicate certificate"):
            illustrative_annual_balance(AnnualRetailSales("coop", 2030, 100),
                                         [cert("D"), cert("D")], .5)

    def test_exclude_unretired_other_owner_ineligible_and_wrong_year(self):
        cs = [cert("valid"), cert("unretired", retired_by=None, retired_for_year=None),
              cert("other", owner_id="other"),
              cert("ineligible", eligible=False),
              cert("wrong-year", retired_for_year=2029),
              cert("future", vintage_year=2031)]
        r = illustrative_annual_balance(AnnualRetailSales("coop", 2030, 100), cs, .5)
        self.assertEqual(r.eligible_retired_mwh, 30)
        self.assertEqual(len(r.excluded_certificate_ids), 5)

    def test_vintage_restriction_is_explicit_scenario_assumption(self):
        r = illustrative_annual_balance(AnnualRetailSales("coop", 2030, 100),
                                         [cert("old", vintage_year=2020)], .5,
                                         max_vintage_age_years=4)
        self.assertEqual(r.eligible_retired_mwh, 0)
        self.assertFalse(r.legally_validated)

    def test_invalid_amounts(self):
        with self.assertRaises(ValueError):
            cert("bad", mwh=float("nan"))
        with self.assertRaises(ValueError):
            AnnualRetailSales("coop", 2030, -1)

    def test_no_double_entity_year_and_exact_target_coverage(self):
        sales = AnnualRetailSales("coop", 2030, 100)
        with self.assertRaises(ValueError):
            illustrative_multi_entity_balances([sales, sales], [], {("coop",2030): .5})
        with self.assertRaises(ValueError):
            illustrative_multi_entity_balances([sales], [], {})

    def test_generation_share_is_not_compliance(self):
        energy = SimulatedAnnualEnergy("coop", 2030, 100, 70)
        self.assertEqual(illustrative_generation_share(energy), .7)
        r = illustrative_annual_balance(AnnualRetailSales("coop",2030,100), [], .5)
        self.assertEqual(r.eligible_retired_mwh, 0)
        self.assertEqual(r.illustrative_shortfall_mwh, 50)

    def test_mapping_requires_manual_verification(self):
        mapping = EntityMapping("coop","synthetic",("bus-1",))
        with self.assertRaisesRegex(ValueError,"Unverified"):
            require_verified_mapping(mapping)
        require_verified_mapping(replace(mapping, verified=True))

if __name__ == "__main__":
    unittest.main()
