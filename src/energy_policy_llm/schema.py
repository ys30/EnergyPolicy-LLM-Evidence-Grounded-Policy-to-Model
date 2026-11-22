from dataclasses import dataclass
from enum import Enum


class Metric(str, Enum):
    RETAIL_SALES_SHARE = "eligible_renewables_retail_sales_share"
    GENERATION_SHARE = "eligible_renewables_generation_share"
    CLEAN_RETAIL_SALES_SHARE = "clean_resources_retail_sales_share"


@dataclass(frozen=True)
class PolicyTarget:
    case_id: str
    state: str
    target_year: int
    fraction: float
    metric: Metric
    covered_entities: str
    source_url: str
    legal_review: str = "needs_clause_review"

    def __post_init__(self):
        if not (0.0 <= self.fraction <= 1.0):
            raise ValueError("fraction must lie in [0, 1]")
        if self.target_year < 1900 or self.target_year > 2200:
            raise ValueError("target year out of supported range")
        if not self.source_url.startswith("https://"):
            raise ValueError("a secure source URL is required")
