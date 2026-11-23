"""Run policy benchmark with a mandatory provenance gate."""
import argparse
import json
from pathlib import Path
from energy_policy_llm.validated_eval import load_and_run

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--snapshots", type=Path)
    parser.add_argument("--synthetic-demo", action="store_true")
    args = parser.parse_args()
    result = load_and_run(str(args.dataset), synthetic=args.synthetic_demo,
                          snapshots_path=str(args.snapshots) if args.snapshots else None)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.synthetic_demo:
        print("SYNTHETIC PIPELINE CHECK. NOT RESEARCH ACCURACY.")

if __name__ == "__main__":
    main()
