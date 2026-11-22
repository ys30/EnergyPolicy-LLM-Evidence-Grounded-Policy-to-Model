"""Offline worklist generator: discovery cases do not become gold automatically."""
import csv
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cases = json.loads((root / "data/policies/evidence_registry_v02.json").read_text(encoding="utf-8"))["cases"]
path = root / "outputs/annotation_queue.csv"
path.parent.mkdir(exist_ok=True)
cols = ["case_id", "primary_url", "provision", "document_version", "snapshot_sha256",
        "start_char", "end_char", "exact_text", "numerator", "denominator",
        "entity_scope", "accounting", "annotator_1", "annotator_2",
        "adjudicator", "decision"]
with path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=cols)
    writer.writeheader()
    for case in cases:
        writer.writerow({"case_id": case["case_id"], "primary_url": case["primary_url"],
                         "provision": case["provision"], "numerator": case["numerator"],
                         "denominator": case["denominator"], "entity_scope": case["obligated_entities"],
                         "accounting": case["accounting"], "decision": "candidate"})
print(f"Generated {len(cases)} review queue rows in {path} (zero gold annotations).")
