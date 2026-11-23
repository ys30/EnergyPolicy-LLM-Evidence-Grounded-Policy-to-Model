"""Optional network capture; writes only ignored local outputs.

python scripts/capture_official_sources.py --case NM_RPS_2030_PUBLIC_UTILITIES
No remote model calls and no automatic gold-label promotion.
"""
import argparse
import json
import sys
from pathlib import Path
from energy_policy_llm.sources import fetch_official_html, save_snapshot

root = Path(__file__).resolve().parents[1]
registry = json.loads((root / "data/policies/evidence_registry_v02.json").read_text(encoding="utf-8"))
cases = {case["case_id"]: case for case in registry["cases"]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=sorted(cases), required=True)
    args = parser.parse_args()
    entry = cases[args.case]
    html = fetch_official_html(entry["primary_url"])
    meta = save_snapshot(args.case, entry["primary_url"], html, root / "outputs/source_snapshots")
    print(json.dumps(meta, indent=2))
    print("SOURCE SNAPSHOT ONLY; not annotated or independently legally reviewed.")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Source capture failed: {exc}", file=sys.stderr)
        sys.exit(1)
