"""Static audit of source-section locators; not a legal/LLM evaluation."""
import json
from pathlib import Path
from energy_policy_llm.provenance import load_catalog, validate_anchor_catalog

root = Path(__file__).resolve().parents[1]
data = load_catalog(root / "data/policies/source_anchors_v06.json")
print(json.dumps(validate_anchor_catalog(data), indent=2, sort_keys=True))
print("No primary text snapshots or gold labels are implied by section locators.")
