"""An offline real-section-inspired PARAPHRASE smoke test, not empirical evaluation."""
import json
from pathlib import Path
from energy_policy_llm.real_text_baseline import extract_clause

root = Path(__file__).resolve().parents[1]
data = json.loads((root / "data/fixtures/official_section_paraphrases_v11.json").read_text())
if data["dataset_kind"] != "official_section_derived_paraphrase_smoke_test_not_gold":
    raise ValueError("Not the explicitly labeled smoke-test fixture")
for case in data["cases"]:
    print(json.dumps({"case_id":case["id"], "output":extract_clause(case["fragment"])},sort_keys=True))
print("NOT REAL LLM RESULTS; no gold labels, no accuracy estimate, no source snapshot.")
