"""Policy evidence contract v0.2: fail-closed, stdlib-only.
This schema is deliberately stricter than simple percent/year extraction.
It does NOT judge legal truth; status must come from human review.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class EvidenceStatus(str, Enum):
    DISCOVERED = "discovered"
    HUMAN_REVIEW_PENDING = "human_review_pending"
    CLAUSE_VERIFIED = "clause_verified"


class Decision(str, Enum):
    ABSTAIN = "ABSTAIN"
    SCENARIO_PROXY = "SCENARIO_PROXY"
    LEGAL_CONSTRAINT = "LEGAL_CONSTRAINT"


@dataclass(frozen=True)
class Evidence:
    document_url: str
    provision: str
    document_version: str
    observed_on: str
    status: EvidenceStatus
    exact_text: Optional[str] = None

    def validate(self) -> None:
        if not self.document_url.startswith("https://"):
            raise ValueError("Evidence requires an https document URL")
        if not self.provision.strip() or not self.document_version.strip():
            raise ValueError("Provision and document version are required")
        if self.status == EvidenceStatus.CLAUSE_VERIFIED and not self.exact_text:
            raise ValueError("Verified evidence requires preserved exact text")


@dataclass(frozen=True)
class PolicyObligation:
    case_id: str
    jurisdiction: str
    obligated_entities: str
    target_fraction: float
    target_date: str
    numerator: str
    denominator: str
    accounting: str
    evidence: Evidence

    def validate(self) -> None:
        self.evidence.validate()
        if not 0 <= self.target_fraction <= 1:
            raise ValueError("Target must be between zero and one")
        if not self.target_date or not self.obligated_entities.strip():
            raise ValueError("Target date and obligated entities required")
        if not self.numerator.strip() or not self.denominator.strip():
            raise ValueError("Numerator and denominator required")


def determine_generation_mapping(
    policy: PolicyObligation,
    requested_denominator: str = "local_generation",
    allow_illustrative_proxy: bool = False,
) -> tuple[Decision, str]:
    """Never claim a retail-sales target is equivalent to local generation.

    LEGAL_CONSTRAINT is reserved for an independently audited exact match,
    not for generic regional renewable percentage matching.
    """
    policy.validate()
    if requested_denominator != "local_generation":
        return Decision.ABSTAIN, "This compiler only supports local_generation requests."
    if policy.denominator != "local_generation":
        if allow_illustrative_proxy and policy.numerator == "eligible_renewables":
            return Decision.SCENARIO_PROXY, (
                "Illustrative generation-share proxy only: retail-sales accounting, "
                "certificates, imports and eligible-resource definitions unresolved."
            )
        return Decision.ABSTAIN, "Denominator mismatch: legal obligation is not local generation."
    if policy.evidence.status != EvidenceStatus.CLAUSE_VERIFIED:
        return Decision.ABSTAIN, "Independent clause-level legal review is required."
    if policy.accounting != "physical_generation_no_credits":
        return Decision.ABSTAIN, "Accounting model is not a validated physical generation constraint."
    if policy.numerator != "eligible_renewables":
        return Decision.ABSTAIN, "Resource eligibility is not supported."
    return Decision.LEGAL_CONSTRAINT, "Reviewed, explicit generation-share constraint."
