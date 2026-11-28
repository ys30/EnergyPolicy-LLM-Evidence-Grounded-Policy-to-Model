"""Run actual PyPSA + HiGHS solves on fabricated toy inputs; never claim legal compliance."""
import json
from pathlib import Path
from energy_policy_llm.pypsa_synthetic_experiment import run_comparison

def main():
    result = run_comparison()
    output = Path("outputs/pypsa_synthetic/experiment_results.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print("Results saved to", output)

if __name__ == "__main__":
    main()
