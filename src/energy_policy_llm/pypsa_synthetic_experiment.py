"""Actually solve a tiny synthetic PyPSA network and contrast a generation proxy.

This experiment is NOT a legal RPS compliance model. REC retirement is computed
separately; the PyPSA generation-share proxy MUST NOT be called legal-equivalent.
"""
from dataclasses import asdict, dataclass
import math

from energy_policy_llm.rec_accounting import (
    Certificate, AnnualRetailSales, illustrative_annual_balance,
)

@dataclass(frozen=True)
class SolverScenario:
    scenario: str
    solver_status: str
    termination_condition: str
    objective_usd_synthetic: float
    renewable_generation_mwh: float
    fossil_generation_mwh: float
    total_generation_mwh: float
    renewable_generation_share: float
    rec_illustrative_shortfall_mwh: float
    legal_compliance_established: bool = False

def _network():
    import pandas as pd
    import pypsa

    n = pypsa.Network()
    n.set_snapshots(pd.date_range("2030-01-01", periods=4, freq="h"))
    n.add("Carrier", "renewable")
    n.add("Carrier", "fossil")
    n.add("Bus", "synthetic_bus")
    # 25 MW for four 1-hour steps -> 100 MWh simulated energy.
    n.add("Load", "synthetic_load", bus="synthetic_bus", p_set=25.0)
    n.add("Generator", "renewable", bus="synthetic_bus", carrier="renewable",
          p_nom=25.0, marginal_cost=40.0)
    n.add("Generator", "fossil", bus="synthetic_bus", carrier="fossil",
          p_nom=25.0, marginal_cost=10.0)
    return n

def solve_scenario(*, generation_share_proxy: bool) -> SolverScenario:
    n = _network()
    if generation_share_proxy:
        def add_nonlegal_share_constraint(network, snapshots):
            """Illustrative forced local-generation ratio; no REC/retail input."""
            dispatch = network.model.variables["Generator-p"]
            renewable = dispatch.sel(Generator="renewable").sum()
            # Here all load is met locally with no losses or imports: 100 MWh.
            total_load_mwh = 25.0 * len(snapshots)
            network.model.add_constraints(
                renewable >= 0.50 * total_load_mwh,
                name="SYNTHETIC_NONLEGAL_RENEWABLE_GENERATION_PROXY",
            )
        status, termination = n.optimize(
            solver_name="highs", extra_functionality=add_nonlegal_share_constraint,
            log_to_console=False)
    else:
        status, termination = n.optimize(solver_name="highs", log_to_console=False)
    if status != "ok" or termination != "optimal":
        raise RuntimeError(f"PyPSA solve failed: {status}/{termination}")
    ren = float(n.generators_t.p["renewable"].sum())
    fossil = float(n.generators_t.p["fossil"].sum())
    total = ren + fossil
    if not (math.isfinite(ren) and math.isfinite(fossil) and total > 0):
        raise RuntimeError("Invalid generation output")
    # Entirely independent synthetic certificates; NOT issued from this solved model.
    certs = [
        Certificate("SYN-REC-1", "coop", 2030, 30.0, True, "coop", 2030),
        Certificate("SYN-REC-2", "coop", 2029, 15.0, True, "coop", 2030),
        Certificate("SYN-REC-3", "coop", 2030, 20.0, True),
    ]
    rec_result = illustrative_annual_balance(
        AnnualRetailSales("coop", 2030, 100.0), certs, 0.50)
    return SolverScenario(
        scenario="nonlegal_generation_proxy" if generation_share_proxy else "unconstrained_baseline",
        solver_status=status, termination_condition=termination,
        objective_usd_synthetic=float(n.objective),
        renewable_generation_mwh=ren, fossil_generation_mwh=fossil,
        total_generation_mwh=total,
        renewable_generation_share=ren / total,
        rec_illustrative_shortfall_mwh=rec_result.illustrative_shortfall_mwh,
        legal_compliance_established=False)

def run_comparison() -> dict:
    base = solve_scenario(generation_share_proxy=False)
    proxy = solve_scenario(generation_share_proxy=True)
    if proxy.renewable_generation_share < .50 - 1e-6:
        raise AssertionError("Proxy generation constraint not satisfied")
    if abs(base.total_generation_mwh - 100.0) > 1e-6 or abs(proxy.total_generation_mwh - 100.0) > 1e-6:
        raise AssertionError("Unexpected toy electric energy balance")
    if proxy.rec_illustrative_shortfall_mwh != base.rec_illustrative_shortfall_mwh:
        raise AssertionError("REC shortfall must be independent of generator dispatch")
    if proxy.objective_usd_synthetic <= base.objective_usd_synthetic:
        raise AssertionError("Nonlegal proxy should increase toy model cost")
    return {
        "kind": "REAL_PYPSA_SOLVES_SYNTHETIC_INPUTS_NOT_LEGAL_COMPLIANCE",
        "pypsa_solver_called": True, "solver": "highs",
        "llm_calls": 0, "human_gold_count": 0,
        "rec_certificates_independently_assumed": True,
        "baseline": asdict(base), "generation_proxy": asdict(proxy),
        "cost_increase_usd_synthetic": proxy.objective_usd_synthetic - base.objective_usd_synthetic,
    }
