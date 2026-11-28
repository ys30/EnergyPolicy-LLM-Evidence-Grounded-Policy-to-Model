"""Compare two externally generated, pinned-model annotation JSONL files.

This tool DOES NOT call LLMs or generate human gold. Each model file must be
created independently, with documented model identity and exact source evidence.
"""
import argparse
import json
from pathlib import Path
from energy_policy_llm.dual_llm_review import load_jsonl, create_comparison_queue

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-a", type=Path, required=True)
    parser.add_argument("--model-b", type=Path, required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Refusing to overwrite existing review queue")
    text = args.snapshot.read_text(encoding="utf-8")
    result = create_comparison_queue(load_jsonl(args.model_a), load_jsonl(args.model_b),
                                     {args.source_id: text})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Cases:", result["case_count"], "agreed:", result["ai_agreed"],
          "disagreed:", result["ai_disagreed"], "human_verified:", result["human_verified"],
          "gold:", result["gold_count"])

if __name__ == "__main__":
    main()
