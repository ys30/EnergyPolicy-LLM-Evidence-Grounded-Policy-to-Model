import unittest
from dataclasses import replace
from hashlib import sha256
from energy_policy_llm.research_gate import GoldProvenance, gate_holdout

DOC_A = "Example source A: renewable retail sales obligation."
DOC_B = "Example source B: renewable electricity target."
H_A = sha256(DOC_A.encode()).hexdigest()
H_B = sha256(DOC_B.encode()).hexdigest()
SOURCES = {H_A: DOC_A, H_B: DOC_B}

def record(name="a", state="CA", split="train", digest=H_A, instrument="A"):
    txt = SOURCES[digest]
    return GoldProvenance(name, instrument, state, split, digest,
                          "hypothetical-2026", "section-one", txt[0:22],
                          0, 22, "reviewer-1", "reviewer-2", "adjudicator-3", True)

class ResearchGateTests(unittest.TestCase):
    def test_clean_holdout(self):
        self.assertEqual(gate_holdout([record(), record("b", "NM", "test", H_B, "B")],
                                      SOURCES, {"NM"})["records"], 2)

    def test_no_gold_claim_without_adjudication(self):
        with self.assertRaises(ValueError):
            gate_holdout([record(), replace(record("b", "NM", "test", H_B, "B"), adjudicated=False)],
                         SOURCES, {"NM"})

    def test_unverified_snapshot_rejected(self):
        with self.assertRaises(ValueError):
            gate_holdout([record(), record("b", "NM", "test", H_B, "B")], {H_A:DOC_A}, {"NM"})

    def test_instrument_leakage(self):
        with self.assertRaises(ValueError):
            gate_holdout([record(), record("b", "NM", "test", H_B, "A")], SOURCES, {"NM"})

    def test_holdout_jurisdiction_leakage(self):
        with self.assertRaises(ValueError):
            gate_holdout([record(), record("b", "CA", "test", H_B, "B")], SOURCES, {"CA"})

    def test_undeclared_test_jurisdiction(self):
        with self.assertRaises(ValueError):
            gate_holdout([record(), record("b", "NM", "test", H_B, "B")], SOURCES, {"AZ"})

    def test_quote_mismatch(self):
        with self.assertRaises(ValueError):
            gate_holdout([record(), replace(record("b", "NM", "test", H_B, "B"), quote="fabricated")],
                         SOURCES, {"NM"})

    def test_reviewer_id_distinct(self):
        with self.assertRaises(ValueError):
            gate_holdout([record(), replace(record("b", "NM", "test", H_B, "B"),
                              annotator_2="reviewer-1")], SOURCES, {"NM"})

    def test_no_test_set(self):
        with self.assertRaises(ValueError):
            gate_holdout([record()], SOURCES, {"NM"})

if __name__ == "__main__":
    unittest.main()
