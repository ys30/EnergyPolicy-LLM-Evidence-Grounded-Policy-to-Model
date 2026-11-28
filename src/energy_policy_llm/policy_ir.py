"""Intermediate legal representation; explicit provenance, not raw LLM output."""
from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet
import math

class LegalType(str, Enum):
    TARGET = "TARGET"
    CONDITIONAL_TARGET = "CONDITIONAL_TARGET"
    ACCOUNTING = "ACCOUNTING"
    COST_EXCEPTION = "COST_EXCEPTION"
    DEFINITION = "DEFINITION"
    ELIGIBILITY = "ELIGIBILITY"
    RESPONSIBILITY = "RESPONSIBILITY"
    PERMISSION = "PERMISSION"
    REPORTING = "REPORTING"

class MetricV2(str, Enum):
    RENEWABLE_RETAIL_SALES = "ELIGIBLE_RENEWABLE_RETAIL_SALES"
    ZERO_CARBON_RETAIL_SALES = "ZERO_CARBON_RETAIL_SALES"
    LOCAL_GENERATION_SHARE = "LOCAL_GENERATION_SHARE"
    NONE = "NONE"

@dataclass(frozen=True)
class PolicyIR:
    annotation_id: str
    source_sha256: str
    provision: str
    legal_type: LegalType
    metric: MetricV2
    entity_id: str
    year: int | None = None
    target_fraction: float | None = None
    condition_ids: tuple[str, ...] = ()
    condition_operator: str = "NONE"
    evidence_verified: bool = False
    human_adjudicated: bool = False
    source_ambiguity: bool = False

    def __post_init__(self):
        if not self.annotation_id or len(self.source_sha256) != 64 or not self.provision or not self.entity_id:
            raise ValueError("IR identity, valid digest, provision and entity required")
        if self.target_fraction is not None and (
            not math.isfinite(self.target_fraction) or not 0 <= self.target_fraction <= 1):
            raise ValueError("target_fraction must be finite within 0..1")
        if self.metric != MetricV2.NONE and (self.year is None or self.target_fraction is None):
            raise ValueError("Target metric requires year and fraction")
        if self.legal_type == LegalType.CONDITIONAL_TARGET and (
            not self.condition_ids or self.condition_operator != "ALL"):
            raise ValueError("Conditional target requires explicit conjunction of conditions")
        if self.condition_operator not in {"NONE", "ALL", "ANY"}:
            raise ValueError("Invalid condition operator")

    def dependencies(self) -> FrozenSet[str]:
        if self.metric == MetricV2.RENEWABLE_RETAIL_SALES:
            base = {"retail_sales_mwh", "rec_ledger", "rec_retirement", "eligible_technology_map"}
        elif self.metric == MetricV2.ZERO_CARBON_RETAIL_SALES:
            base = {"retail_sales_mwh", "zero_carbon_resource_map", "rec_ledger", "rec_retirement"}
        elif self.metric == MetricV2.LOCAL_GENERATION_SHARE:
            base = {"local_generation_mwh", "eligible_technology_map"}
        else:
            base = set()
        if self.condition_ids:
            base.add("condition_evidence")
        if self.legal_type == LegalType.COST_EXCEPTION:
            base.update({"cost_usd_per_mwh", "cpi_index"})
        return frozenset(base)
