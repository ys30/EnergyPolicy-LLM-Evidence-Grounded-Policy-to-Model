import unittest
from copy import deepcopy
from energy_policy_llm.validated_eval import run_verified_evaluation

FIELDS = {"target_fraction":.5,"target_date":"2030-01-01",
          "obligated_entities":"distribution_cooperative","denominator":"retail_sales",
          "numerator":"eligible_renewables"}

def sample():
    gold, pred = [], []
    for i, state, split in [(0,"demo_CA","train"),(1,"demo_NM","test")]:
        gold.append({"case_id":f"syn-{i}","instrument_id":f"instrument-{i}",
                     "jurisdiction":state,"split":split,"gold_status":"synthetic",
                     "gold_fields":FIELDS.copy(),"gold_decision":"ABSTAIN"})
        pred.append({"case_id":f"syn-{i}","predicted_fields":FIELDS.copy(),"predicted_decision":"ABSTAIN"})
    return {"dataset_kind":"synthetic_fixture","heldout_jurisdictions":["demo_NM"],
            "gold_records":gold,"predictions":pred}

class GatedEvaluationTests(unittest.TestCase):
    def test_valid_demo(self):
        result=run_verified_evaluation(sample(),{},synthetic=True)
        self.assertEqual(result["n_test"],1)
        self.assertFalse(result["publication_ready"])
    def test_unsafe_detected(self):
        p=sample();p["predictions"][1]["predicted_decision"]="LEGAL_CONSTRAINT"
        self.assertEqual(run_verified_evaluation(p,{},synthetic=True)["test_metrics"]["unsafe_accept_count"],1)
    def test_demo_rejected_in_empirical_mode(self):
        with self.assertRaises(ValueError):run_verified_evaluation(sample(),{},synthetic=False)
    def test_missing_prediction_rejected(self):
        p=sample();p["predictions"].pop()
        with self.assertRaises(ValueError):run_verified_evaluation(p,{},synthetic=True)
    def test_wrong_prediction_id_rejected(self):
        p=sample();p["predictions"][1]["case_id"]="not-gold"
        with self.assertRaises(ValueError):run_verified_evaluation(p,{},synthetic=True)
    def test_duplicate_prediction_rejected(self):
        p=sample();p["predictions"][1]["case_id"]="syn-0"
        with self.assertRaises(ValueError):run_verified_evaluation(p,{},synthetic=True)
    def test_test_leakage_rejected(self):
        p=sample();p["gold_records"][0]["jurisdiction"]="demo_NM"
        with self.assertRaises(ValueError):run_verified_evaluation(p,{},synthetic=True)
    def test_group_leakage_rejected(self):
        p=sample();p["gold_records"][1]["instrument_id"]="instrument-0"
        with self.assertRaises(ValueError):run_verified_evaluation(p,{},synthetic=True)
    def test_fabricated_empirical_gold_not_accepted(self):
        p=sample();p["dataset_kind"]="human_adjudicated"
        for g in p["gold_records"]:g["gold_status"]="adjudicated"
        with self.assertRaises((ValueError,KeyError)):run_verified_evaluation(p,{},synthetic=False)
    def test_unrecognized_holdout_rejected(self):
        p=sample();p["heldout_jurisdictions"]=["other"]
        with self.assertRaises(ValueError):run_verified_evaluation(p,{},synthetic=True)

if __name__=="__main__":
    unittest.main()
