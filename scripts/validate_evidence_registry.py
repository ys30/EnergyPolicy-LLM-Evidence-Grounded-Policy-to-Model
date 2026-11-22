"""Run: python scripts/validate_evidence_registry.py. No external dependencies."""
import json
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "data/policies/evidence_registry_v02.json"
data = json.loads(path.read_text(encoding="utf-8"))
assert data["schema_version"] == "0.2.0"
ids = set()
allowed = {"discovered", "human_review_pending", "clause_verified"}
for case in data["cases"]:
    assert case["case_id"] not in ids, case["case_id"]
    ids.add(case["case_id"])
    assert case["primary_url"].startswith("https://")
    assert case["status"] in allowed
    assert 0 <= case["target_fraction"] <= 1
    assert case["denominator"] != "local_generation", "Do not relabel retail-sales obligations as generation standards"
    for field in ("obligated_entities", "numerator", "denominator", "accounting", "provision", "target_date"):
        assert str(case[field]).strip(), (case["case_id"], field)
print(f"Validated {len(ids)} distinct policy case records. Legal verification still pending.")
