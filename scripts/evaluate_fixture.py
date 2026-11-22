"""Offline evaluator smoke test, NOT a research/LLM accuracy experiment."""
import json
from pathlib import Path
from energy_policy_llm.benchmark import Case, evaluate

root = Path(__file__).resolve().parents[1]
data = json.loads((root / "data/fixtures/synthetic_benchmark_v04.json").read_text(encoding="utf-8"))
if data.get("fixture_only") is not True or data.get("not_research_data") is not True:
    raise RuntimeError("Only the explicitly labeled synthetic fixture is supported")
cases = [Case(**entry) for entry in data["records"]]
result = evaluate(cases, allow_synthetic=True)
print(json.dumps(result, indent=2, sort_keys=True))
print("WARNING: SYNTHETIC EVALUATOR TEST. Not an LLM performance claim.")
