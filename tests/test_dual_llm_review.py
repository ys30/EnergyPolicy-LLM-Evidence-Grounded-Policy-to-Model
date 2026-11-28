"""Tests use fabricated fixture predictions; never claim actual two-model results."""
import copy
import hashlib
import unittest
from energy_policy_llm.dual_llm_review import create_comparison_queue, register_human_review

TEXT = "17.9.571.8(C) Fifty percent of retail electricity sales in 2030."
SHA = hashlib.sha256(TEXT.encode()).hexdigest()
PROMPT = hashlib.sha256(b"fixture prompt").hexdigest()

def pred(model_id="provider-a/model-a", fraction=.50):
    return {
        "case_id": "NM25-009", "source_id": "NM_COOP_2025",
        "model_id": model_id, "model_version": "fixture-1", "prompt_sha256": PROMPT,
        "source_sha256": SHA,
        "predicted_fields": {"target_fraction": fraction, "target_date": "2030-01-01",
                             "denominator_metric": "NM_TOTAL_RETAIL_SALES_MWH"},
        "evidence_spans": [{"start_char": 0, "end_char": len(TEXT), "exact_text": TEXT}],
    }

class DualLLMReviewTests(unittest.TestCase):
    def test_ai_agreement_is_not_gold(self):
        r = create_comparison_queue([pred()], [pred("provider-b/model-b")], {"NM_COOP_2025": TEXT})
        self.assertEqual((r["ai_agreed"], r["gold_count"]), (1, 0))
        self.assertTrue(r["records"][0]["human_review_required"])
        self.assertFalse(r["records"][0]["gold_eligible"])

    def test_critical_disagreement(self):
        r = create_comparison_queue([pred()], [pred("provider-b/model-b", .60)], {"NM_COOP_2025": TEXT})
        self.assertEqual(r["ai_disagreed"], 1)
        self.assertIn("target_fraction", r["records"][0]["critical_field_disagreements"])

    def test_reject_same_model_identity(self):
        with self.assertRaises(ValueError):
            create_comparison_queue([pred()], [pred()], {"NM_COOP_2025": TEXT})

    def test_reject_incorrect_source_or_span(self):
        x = pred()
        x["evidence_spans"][0]["exact_text"] = "invented"
        with self.assertRaises(ValueError):
            create_comparison_queue([x], [pred("provider-b/model-b")], {"NM_COOP_2025": TEXT})

    def test_human_verification_remains_non_gold(self):
        item = create_comparison_queue([pred()], [pred("provider-b/model-b")], {"NM_COOP_2025": TEXT})["records"][0]
        review = {
            "reviewer_id": "human-1", "decision": "ACCEPT",
            "reviewed_all_fields": True, "reviewed_full_source_context": True,
            "final_fields": copy.deepcopy(item["ai_a"]["predicted_fields"]),
            "rationale": "Reviewed source evidence and fields independently.",
            "reviewed_evidence_spans": item["ai_a"]["evidence_spans"]
        }
        updated = register_human_review(item, review, TEXT)
        self.assertEqual(updated["reference_status"], "HUMAN_VERIFIED")
        self.assertFalse(updated["gold_eligible"])

    def test_cannot_rubber_stamp_without_full_source_review(self):
        item = create_comparison_queue([pred()], [pred("provider-b/model-b")], {"NM_COOP_2025": TEXT})["records"][0]
        review = {"reviewer_id": "human-1", "decision": "ACCEPT",
                  "reviewed_all_fields": True, "reviewed_full_source_context": False,
                  "final_fields": pred()["predicted_fields"], "rationale": "Agreed",
                  "reviewed_evidence_spans": pred()["evidence_spans"]}
        with self.assertRaises(ValueError):
            register_human_review(item, review, TEXT)

if __name__ == "__main__":
    unittest.main()
