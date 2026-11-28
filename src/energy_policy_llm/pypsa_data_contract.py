"""Boundary between PyPSA energy simulation and independent retail-sales/REC accounting.

This module inspects *provided* values. It never infers retail sales from
PyPSA generation or asserts that nodes/buses equal legal entities.
"""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class EntityMapping:
    legal_entity_id: str
    model_profile_id: str
    bus_ids: tuple[str, ...]
    verified: bool = False

    def __post_init__(self):
        if not self.legal_entity_id or not self.model_profile_id or not self.bus_ids:
            raise ValueError("Mapping requires legal entity, profile and explicit buses")
        if len(set(self.bus_ids)) != len(self.bus_ids):
            raise ValueError("Repeated bus ID")

@dataclass(frozen=True)
class SimulatedAnnualEnergy:
    entity_id: str
    year: int
    generation_mwh: float
    renewable_generation_mwh: float
    data_origin: str = "SYNTHETIC"

    def __post_init__(self):
        if not self.entity_id or not isinstance(self.year,int) or isinstance(self.year,bool):
            raise ValueError("Invalid entity/year")
        if not all(isfinite(v) for v in (self.generation_mwh, self.renewable_generation_mwh)):
            raise ValueError("Nonfinite energy")
        if self.generation_mwh < 0 or not 0 <= self.renewable_generation_mwh <= self.generation_mwh:
            raise ValueError("Invalid simulated generation amounts")
        if self.data_origin not in {"SYNTHETIC","PYPSA_EXPORT"}:
            raise ValueError("Unknown data origin")

def illustrative_generation_share(row: SimulatedAnnualEnergy) -> float | None:
    """Nonlegal proxy only. Does not calculate REC credits or retail sales."""
    return row.renewable_generation_mwh / row.generation_mwh if row.generation_mwh else None

def require_verified_mapping(mapping: EntityMapping) -> None:
    if not mapping.verified:
        raise ValueError("Unverified utility-to-model-bus mapping")
