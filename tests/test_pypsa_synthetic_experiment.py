"""PyPSA optional-integration tests; normal lightweight CI skips if not installed."""
import unittest

try:
    import pypsa
    import highspy
except ImportError:
    pypsa = None

@unittest.skipUnless(pypsa is not None, "Optional PyPSA + HiGHS integration dependencies")
class PypsaSyntheticIntegrationTests(unittest.TestCase):
    def test_actual_solver_and_proxy_gap(self):
        from energy_policy_llm.pypsa_synthetic_experiment import run_comparison
        r = run_comparison()
        self.assertTrue(r["pypsa_solver_called"])
        self.assertEqual(r["baseline"]["solver_status"], "ok")
        self.assertEqual(r["generation_proxy"]["solver_status"], "ok")
        self.assertAlmostEqual(r["baseline"]["renewable_generation_share"], 0.0, places=5)
        self.assertAlmostEqual(r["generation_proxy"]["renewable_generation_share"], 0.5, places=5)
        self.assertAlmostEqual(r["baseline"]["objective_usd_synthetic"], 1000.0, places=3)
        self.assertAlmostEqual(r["generation_proxy"]["objective_usd_synthetic"], 2500.0, places=3)
        self.assertAlmostEqual(r["cost_increase_usd_synthetic"], 1500.0, places=3)
        self.assertEqual(r["baseline"]["rec_illustrative_shortfall_mwh"], 5)
        self.assertEqual(r["generation_proxy"]["rec_illustrative_shortfall_mwh"], 5)
        self.assertFalse(r["generation_proxy"]["legal_compliance_established"])
if __name__ == "__main__":
    unittest.main()
