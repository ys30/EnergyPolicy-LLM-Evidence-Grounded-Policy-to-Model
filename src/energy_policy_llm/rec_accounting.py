"""Independent, deterministic synthetic REC accounting; NOT an NM legal compliance opinion.

Uses unique indivisible certificate batches (MWh) with explicit owner and retirement.
No automatic legal rules for eligibility, vintage, banking or transfers are assumed.
"""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Certificate:
    certificate_id: str
    owner_id: str
    vintage_year: int
    mwh: float
    eligible: bool
    retired_by: str | None = None
    retired_for_year: int | None = None

    def __post_init__(self):
        if not self.certificate_id or not self.owner_id:
            raise ValueError("Certificate ID and owner required")
        if not isinstance(self.vintage_year,int) or isinstance(self.vintage_year,bool):
            raise ValueError("Invalid certificate vintage")
        if not isfinite(self.mwh) or self.mwh <= 0:
            raise ValueError("Certificate amount must be positive and finite")
        if (self.retired_by is None) != (self.retired_for_year is None):
            raise ValueError("Retirement entity and year must both be present or absent")

@dataclass(frozen=True)
class AnnualRetailSales:
    entity_id: str
    year: int
    mwh: float

    def __post_init__(self):
        if not self.entity_id or not isinstance(self.year,int) or isinstance(self.year,bool):
            raise ValueError("Invalid entity/year")
        if not isfinite(self.mwh) or self.mwh < 0:
            raise ValueError("Retail sales must be finite and nonnegative")

@dataclass(frozen=True)
class IllustrativeLedgerResult:
    entity_id: str
    year: int
    retail_sales_mwh: float
    eligible_retired_mwh: float
    illustrative_target_mwh: float
    illustrative_shortfall_mwh: float
    credited_certificate_ids: tuple[str, ...]
    excluded_certificate_ids: tuple[str, ...]
    legally_validated: bool = False

def validate_ledger(certificates: list[Certificate]) -> None:
    ids = [c.certificate_id for c in certificates]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate certificate ID: could double-count MWh")

def illustrative_annual_balance(sales: AnnualRetailSales,
                                certificates: list[Certificate],
                                target_fraction: float,
                                *, max_vintage_age_years: int | None = None
                                ) -> IllustrativeLedgerResult:
    """Checks a synthetic accounting balance, NOT NM statutory compliance.

    Vintage-age restriction is disabled unless explicitly set by caller. A
    supplied value is a scenario assumption, NOT the legal banking rule.
    """
    if not isfinite(target_fraction) or not 0 <= target_fraction <= 1:
        raise ValueError("Target fraction outside 0..1")
    if max_vintage_age_years is not None and (
        not isinstance(max_vintage_age_years,int) or isinstance(max_vintage_age_years,bool)
        or max_vintage_age_years < 0):
        raise ValueError("Invalid scenario vintage-age setting")
    validate_ledger(certificates)
    credited, excluded = [], []
    for c in certificates:
        vintage_ok = c.vintage_year <= sales.year and (
            max_vintage_age_years is None or sales.year - c.vintage_year <= max_vintage_age_years)
        # Retirement, not mere issuance or ownership, is required in this fixture.
        if (c.eligible and vintage_ok and c.owner_id == sales.entity_id
            and c.retired_by == sales.entity_id and c.retired_for_year == sales.year):
            credited.append(c)
        else:
            excluded.append(c)
    actual = sum(c.mwh for c in credited)
    target = sales.mwh * target_fraction
    return IllustrativeLedgerResult(
        sales.entity_id, sales.year, sales.mwh, actual, target,
        max(0.0, target-actual),
        tuple(c.certificate_id for c in credited),
        tuple(c.certificate_id for c in excluded))

def illustrative_multi_entity_balances(
    sales_rows: list[AnnualRetailSales], certificates: list[Certificate],
    targets: dict[tuple[str, int], float]) -> list[IllustrativeLedgerResult]:
    """Reject duplicate annual sales rows and missing targets. Cert IDs are global."""
    validate_ledger(certificates)
    keys = [(r.entity_id, r.year) for r in sales_rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate entity/year retail sales")
    if set(keys) != set(targets):
        raise ValueError("Targets and retail sales must cover identical entity/year keys")
    return [illustrative_annual_balance(row, certificates, targets[(row.entity_id, row.year)])
            for row in sales_rows]
