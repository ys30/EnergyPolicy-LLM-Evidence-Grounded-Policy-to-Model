"""Fail-closed policy-to-model plan compiler. Does not execute PyPSA or establish compliance."""
from dataclasses import dataclass
from .model_profile import ModelProfile
from .policy_ir import PolicyIR, LegalType, MetricV2

@dataclass(frozen=True)
class CompilationPlan:
    annotation_id: str
    model_profile_id: str
    status: str
    legal_equivalence: bool
    required_data: tuple[str, ...]
    missing_data: tuple[str, ...]
    expression: str | None
    reason: str

def compile_policy(ir: PolicyIR, profile: ModelProfile, allow_proxy: bool = False) -> CompilationPlan:
    required = tuple(sorted(ir.dependencies()))
    missing = profile.missing(ir.dependencies())
    def result(status: str, reason: str, expression: str | None = None, equivalent: bool = False) -> CompilationPlan:
        return CompilationPlan(ir.annotation_id, profile.profile_id, status, equivalent, required,
                               missing, expression, reason)
    if ir.source_ambiguity:
        return result("ABSTAIN", "SOURCE_AMBIGUITY: legal text/cross-reference unresolved")
    if not ir.evidence_verified:
        return result("ABSTAIN", "UNVERIFIED_EVIDENCE: freeze and verify exact legal source")
    if ir.legal_type in {LegalType.DEFINITION, LegalType.RESPONSIBILITY, LegalType.REPORTING,
                         LegalType.ELIGIBILITY, LegalType.PERMISSION, LegalType.ACCOUNTING,
                         LegalType.COST_EXCEPTION}:
        return result("NOT_DIRECTLY_EXECUTABLE", "Supporting semantics or external compliance module; not a standalone percentage LP constraint")
    if ir.entity_id not in profile.entity_ids:
        return result("ABSTAIN", "ENTITY_MISMATCH: obligated entity absent from profile")
    if ir.year not in profile.years:
        return result("ABSTAIN", "YEAR_OUTSIDE_PROFILE")
    if ir.condition_ids:
        return result("ABSTAIN", "CONDITIONAL_TARGET: evidence and trigger interpretation require case-specific independent validation")
    if ir.metric in {MetricV2.RENEWABLE_RETAIL_SALES, MetricV2.ZERO_CARBON_RETAIL_SALES}:
        if not missing and ir.human_adjudicated and profile.reviewed_legal_mapping:
            return result("PLAN_ONLY", "Candidate accounting expression requires implementation and compliance validation",
                          "retired_eligible_MWh[entity,year] >= fraction * retail_sales_MWh[entity,year]")
        if allow_proxy and "local_generation_mwh" in profile.capabilities:
            return result("SCENARIO_PROXY", "Nonlegal generation-share proxy; retail sales/REC semantics NOT preserved",
                          "local_eligible_generation_MWh / local_generation_MWh >= fraction")
        return result("ABSTAIN", "Missing model data or independent legal/model mapping verification")
    if ir.metric == MetricV2.LOCAL_GENERATION_SHARE:
        if not missing and ir.human_adjudicated and profile.reviewed_legal_mapping:
            return result("PLAN_ONLY", "Generation-share equation is a candidate plan; no solver executed",
                          "local_eligible_generation_MWh / local_generation_MWh >= fraction")
        return result("ABSTAIN", "No adjudicated provenance and reviewed model mapping")
    return result("ABSTAIN", "Unsupported metric")
