"""Validate research probe metadata; NOT a real LLM benchmark."""
import json
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "data/policies/real_rule_probes_v08.json"
data = json.loads(p.read_text(encoding="utf-8"))
assert data["schema_version"] == "0.8.0"
assert data["expected_default_decision"] == "ABSTAIN"
assert "not_human_adjudicated_gold" in data["status"]
ids = set()
for probe in data["records"]:
    assert probe["id"] not in ids
    ids.add(probe["id"])
    assert probe["source"].startswith("https://www.srca.nm.gov/")
    assert probe["provision"].startswith("17.9.")
    assert probe["risk"] in {"entity_scope", "denominator", "certificate", "technology_eligibility", "exception"}
print(f"{len(ids)} section-grounded, unadjudicated research probes validated (0 gold labels).")
