import unittest
from energy_policy_llm.sensitivity import experiment
from energy_policy_llm.toy_lp import solve_proxy


class SensitivityTests(unittest.TestCase):
    def test_baseline(self):
        self.assertEqual(solve_proxy(0).total_cost_arbitrary_units, 100)

    def test_toy_at_60(self):
        self.assertEqual(solve_proxy(.6).total_cost_arbitrary_units, 137.5)

    def test_toy_at_50(self):
        self.assertEqual(solve_proxy(.5).total_cost_arbitrary_units, 127.5)

    def test_retail_sales_not_compiled(self):
        self.assertEqual(experiment()[1]["strict_decision"], "ABSTAIN")

    def test_generation_can_run(self):
        self.assertEqual(experiment()[0]["strict_decision"], "RUN")

    def test_all_synthetic(self):
        self.assertTrue(all(x["real_policy_result"] is False for x in experiment()))

    def test_invalid_share(self):
        with self.assertRaises(ValueError):
            solve_proxy(.95)


if __name__ == "__main__":
    unittest.main()
