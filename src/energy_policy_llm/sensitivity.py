"""Synthetic policy translation sensitivity experiment, not empirical policy research."""
from dataclasses import dataclass
from .toy_lp import solve_proxy


@dataclass(frozen=True)
class Scenario:
    name: str
    target_share: float
    legal_denominator: str
    modeled_denominator: str


def experiment():
    baseline = solve_proxy(0).total_cost_arbitrary_units
    cases = [
        Scenario("synthetic_correct_generation_share", .6, "local_generation", "local_generation"),
        Scenario("synthetic_retail_sales_miscompiled", .6, "retail_sales", "local_generation"),
        Scenario("synthetic_target_strength_wrong", .5, "retail_sales", "local_generation"),
    ]
    results = []
    for case in cases:
        cost = solve_proxy(case.target_share).total_cost_arbitrary_units
        results.append({
            "scenario": case.name,
            "assumption": case.target_share,
            "naive_optimization_cost": round(cost, 6),
            "increment_over_unconstrained": round(cost - baseline, 6),
            "strict_decision": "RUN" if case.legal_denominator == case.modeled_denominator else "ABSTAIN",
            "real_policy_result": False,
        })
    return results


def main():
    import json
    print(json.dumps(experiment(), indent=2))
    print("SYNTHETIC ONLY. No real-world legal compliance or PyPSA results.")


if __name__ == "__main__":
    main()
