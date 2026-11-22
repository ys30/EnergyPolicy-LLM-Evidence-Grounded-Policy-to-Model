import argparse
import json
from pathlib import Path
from .schema import Metric, PolicyTarget
from .compiler import compile_generation_share
from .toy_lp import solve_proxy


def main():
    parser = argparse.ArgumentParser(description="Auditable policy-to-model toy workflow")
    parser.add_argument("--mode", choices=["strict", "proxy"], default="strict")
    args = parser.parse_args()
    cases = Path(__file__).resolve().parents[2] / "data" / "policies" / "cases.json"
    for record in json.loads(cases.read_text(encoding="utf-8")):
        target = PolicyTarget(**{**record, "metric": Metric(record["metric"])})
        result = compile_generation_share(target, allow_proxy=(args.mode == "proxy"))
        print(f"{target.case_id}: {result.status} | {result.justification}")
        if result.status == "PROXY_ONLY":
            baseline = solve_proxy(0.0)
            scenario = solve_proxy(result.fraction)
            print(f"  SYNTHETIC ONLY: baseline cost={baseline.total_cost_arbitrary_units:.2f}; "
                  f"proxy cost={scenario.total_cost_arbitrary_units:.2f}; "
                  f"delta={scenario.total_cost_arbitrary_units-baseline.total_cost_arbitrary_units:+.2f} arbitrary units")


if __name__ == "__main__":
    main()
