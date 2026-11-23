import unittest
from energy_policy_llm.real_text_baseline import extract_clause

class RealTextBaselineTests(unittest.TestCase):
    def test_digit_percentage_and_year(self):
        r = extract_clause("By 2030 50 percent of retail sales must qualify")
        self.assertEqual((r["target_fraction"],r["target_year"],r["denominator"]),(.5,2030,"retail_sales"))
    def test_word_percentage_must_abstain(self):
        r = extract_clause("No later than 2030, fifty percent of retail sales")
        self.assertIsNone(r["target_fraction"])
        self.assertEqual(r["decision"],"ABSTAIN")
    def test_multiple_goals_do_not_guess(self):
        r = extract_clause("50% by 2030 and 80% by 2050")
        self.assertIsNone(r["target_fraction"])
        self.assertIsNone(r["target_year"])
    def test_invalid_fraction(self):
        with self.assertRaises(ValueError): extract_clause("200% by 2030")
    def test_never_claims_legal_compliance(self):
        self.assertEqual(extract_clause("60% of generation by 2030")["decision"],"ABSTAIN")

if __name__ == "__main__":
    unittest.main()
