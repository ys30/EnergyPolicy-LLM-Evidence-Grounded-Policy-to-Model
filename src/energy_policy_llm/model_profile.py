"""Immutable capabilities of a *specific* model; never infer legal equivalence from a bus."""
from dataclasses import dataclass
from typing import FrozenSet

@dataclass(frozen=True)
class ModelProfile:
    profile_id: str
    model_kind: str
    entity_ids: FrozenSet[str]
    years: FrozenSet[int]
    capabilities: FrozenSet[str]
    reviewed_legal_mapping: bool = False

    def __post_init__(self):
        if not self.profile_id or not self.model_kind or not self.entity_ids or not self.years:
            raise ValueError("Profile requires identity, entities and time domain")
        unknown = self.capabilities - frozenset({
            "retail_sales_mwh", "rec_ledger", "rec_retirement",
            "eligible_technology_map", "zero_carbon_resource_map",
            "condition_evidence", "cost_usd_per_mwh", "cpi_index",
            "local_generation_mwh",
        })
        if unknown:
            raise ValueError("Unknown capability: " + ", ".join(sorted(unknown)))

    def missing(self, required: FrozenSet[str]) -> tuple[str, ...]:
        return tuple(sorted(required - self.capabilities))


def synthetic_profile(*, full: bool = False) -> ModelProfile:
    """Synthetic fixtures only; full capabilities do NOT prove a real legal mapping."""
    caps = {"local_generation_mwh"}
    if full:
        caps.update({"retail_sales_mwh", "rec_ledger", "rec_retirement",
                     "eligible_technology_map", "zero_carbon_resource_map",
                     "condition_evidence", "cost_usd_per_mwh", "cpi_index"})
    return ModelProfile("SYNTHETIC_NM_COOP_V1", "synthetic_not_pypsa",
                        frozenset({"distribution_cooperative"}), frozenset({2025, 2030, 2050}),
                        frozenset(caps), reviewed_legal_mapping=False)
