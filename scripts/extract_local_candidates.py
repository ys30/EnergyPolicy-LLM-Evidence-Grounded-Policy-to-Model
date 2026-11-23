"""Extract source-hashed candidates from one locally frozen official text snapshot."""
import argparse
from pathlib import Path
from energy_policy_llm.candidates import extract_candidates, verify_candidates, export_candidates

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--snapshot", type=Path, required=True)
    p.add_argument("--source-id", required=True)
    p.add_argument("--source-version", required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    text = args.snapshot.read_text(encoding="utf-8")
    candidates = extract_candidates(text, args.source_id, args.source_version)
    verify_candidates(candidates, text)
    export_candidates(candidates, args.output)
    print(f"{len(candidates)} unreviewed candidates exported; gold count remains zero")

if __name__ == "__main__":
    main()
