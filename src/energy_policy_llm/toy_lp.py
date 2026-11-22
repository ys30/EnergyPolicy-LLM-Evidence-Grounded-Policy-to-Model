"""Artificial single-period LP; explicitly not a grid/retail compliance or PyPSA model."""
from dataclasses import dataclass
from scipy.optimize import linprog


@dataclass(frozen=True)
class ToyResult:
    renewable_share: float
    total_cost_arbitrary_units: float
    solar_units: float
    wind_units: float
    gas_units: float


def solve_proxy(renewable_min_share: float) -> ToyResult:
    if not (0 <= renewable_min_share <= 1):
        raise ValueError("share must be between 0 and 1")
    # Completely artificial: demand=100 energy units; max solar=45, wind=45, gas=100.
    # Costs are unitless (gas=1, wind=1.5, solar=2) and have no empirical interpretation.
    res = linprog(c=[2.0, 1.5, 1.0], A_ub=[[-1, -1, 0]], b_ub=[-100 * renewable_min_share],
                  A_eq=[[1, 1, 1]], b_eq=[100], bounds=[(0, 45), (0, 45), (0, 100)], method="highs")
    if not res.success:
        raise ValueError(f"Toy optimization infeasible: {res.message}")
    solar, wind, gas = res.x
    return ToyResult(renewable_min_share, float(res.fun), float(solar), float(wind), float(gas))
