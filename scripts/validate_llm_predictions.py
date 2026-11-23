"""Validate actual LLM prediction JSONL, without scoring against unavailable gold."""
import argparse
import json
from energy_policy_llm.prediction_io import load_predictions

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--predictions", required=True)
    args = p.parse_args()
    data = load_predictions(args.predictions)
    summary = {"prediction_records": data["count"], "case_ids": data["case_ids"],
               "gold_labels_verified": False, "accuracy_computed": False}
    print(json.dumps(summary, indent=2))
    print("Schema validation only; no claim that predictions came from an LLM without independent run logs.")

if __name__ == "__main__":
    main()
