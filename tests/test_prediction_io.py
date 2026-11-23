import json
import unittest
from energy_policy_llm.prediction_io import parse_predictions

def record():
    return {"case_id":"example", "model_id":"model", "model_version":"version",
            "prompt_sha256":"a"*64, "source_id":"source",
            "predicted_fields":{"target_fraction":None,"target_date":None,
                                "obligated_entities":None,"numerator":None,"denominator":None},
            "predicted_decision":"ABSTAIN"}

class PredictionIOTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(parse_predictions([json.dumps(record())])["count"],1)
    def test_invalid_json(self):
        with self.assertRaises(ValueError):parse_predictions(["not json"])
    def test_empty(self):
        with self.assertRaises(ValueError):parse_predictions([])
    def test_missing_prompt_hash(self):
        r=record();r.pop("prompt_sha256")
        with self.assertRaises(ValueError):parse_predictions([json.dumps(r)])
    def test_duplicate_prediction(self):
        x=json.dumps(record())
        with self.assertRaises(ValueError):parse_predictions([x,x])
    def test_invalid_decision(self):
        r=record();r["predicted_decision"]="COMPLIANT"
        with self.assertRaises(ValueError):parse_predictions([json.dumps(r)])
    def test_over_100_percent(self):
        r=record();r["predicted_fields"]["target_fraction"]=1.2
        with self.assertRaises(ValueError):parse_predictions([json.dumps(r)])
    def test_missing_field(self):
        r=record();r["predicted_fields"].pop("denominator")
        with self.assertRaises(ValueError):parse_predictions([json.dumps(r)])

if __name__ == "__main__":
    unittest.main()
