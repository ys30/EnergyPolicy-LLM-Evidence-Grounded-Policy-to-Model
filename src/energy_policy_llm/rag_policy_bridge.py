"""Fail-closed evidence-bound draft → PolicyIR; NEVER creates human Gold.

This is a validation boundary, not an LLM predictor or legal semantic checker.
A matched quotation proves the text exists, not that an extracted value is true.
"""
from dataclasses import dataclass
from .evidence_bundle import EvidenceBundle
from .field_evidence import FieldEvidence,validate_field_evidence
from .policy_ir import PolicyIR, LegalType, MetricV2

@dataclass(frozen=True)
class ProposedPolicyFields:
    annotation_id: str
    provision: str
    legal_type: str
    metric: str
    entity_id: str
    year: int | None
    target_fraction: float | None
    condition_ids: tuple[str,...] = ()
    condition_operator: str = "NONE"
    field_evidence: tuple[FieldEvidence,...] = ()

@dataclass(frozen=True)
class DraftBridgeResult:
    status: str
    reasons: tuple[str,...]
    policy_ir: PolicyIR | None
    checked_fields: tuple[str,...]
    human_gold: bool = False

def validate_proposed_policy(text: str, bundle: EvidenceBundle,
                             candidate: ProposedPolicyFields,
                             *, required_field_names: tuple[str,...] | None = None
                             ) -> DraftBridgeResult:
    """Validate exact citations, required-field coverage and scope.

    Assumes the evidence bundle itself came from a trusted snapshot verifier;
    supplied source text SHA and exact field quote are rechecked here.
    No conversion asserts legal or numerical correctness and no automatic
    "evidence_verified=True" or "human_adjudicated=True" is allowed.
    """
    problems=[]
    if not candidate.annotation_id or not candidate.provision or not candidate.entity_id:
        problems.append("MISSING_POLICY_IDENTITY")
    if not any(c.provision == candidate.provision for c in bundle.evidence_chunks):
        problems.append("PROVISION_NOT_IN_EVIDENCE_BUNDLE")
    if bundle.unresolved_references:
        problems.append("UNRESOLVED_CROSS_REFERENCES")
    if bundle.source_ambiguities:
        problems.append("SOURCE_AMBIGUITY")

    fields=list(candidate.field_evidence)
    if not fields:
        return DraftBridgeResult("ABSTAIN",tuple(problems+["NO_FIELD_CITATIONS"]),None,())
    names=[f.field_name for f in fields]
    if len(names)!=len(set(names)):
        problems.append("DUPLICATE_FIELD_CITATIONS")
    required=set(required_field_names or
                 ("legal_type","metric","entity_id","year","target_fraction"))
    # Structural requirements depend on target and optional non-target class.
    try:
        legal=LegalType(candidate.legal_type)
        metric=MetricV2(candidate.metric)
    except (ValueError, TypeError):
        return DraftBridgeResult("ABSTAIN",tuple(problems+["UNKNOWN_CONTROLLED_LABEL"]),None,tuple(names))
    if metric == MetricV2.NONE:
        required={"legal_type","entity_id"}
    if legal == LegalType.CONDITIONAL_TARGET:
        required.update(("condition_ids","condition_operator"))
    absent=sorted(required-set(names))
    if absent:
        problems.append("MISSING_FIELD_EVIDENCE:"+",".join(absent))
    try:
        checks=validate_field_evidence(text,bundle,fields)
    except ValueError as exc:
        return DraftBridgeResult("ABSTAIN",tuple(problems+["SOURCE_INTEGRITY:"+str(exc)]),None,tuple(names))
    problems.extend(ch.field_name+":"+ch.reason for ch in checks if ch.status=="REJECT")
    if problems:
        return DraftBridgeResult("ABSTAIN",tuple(problems),None,tuple(names))
    try:
        ir=PolicyIR(annotation_id=candidate.annotation_id,
            source_sha256=bundle.source_sha256,provision=candidate.provision,
            legal_type=legal,metric=metric,entity_id=candidate.entity_id,
            year=candidate.year,target_fraction=candidate.target_fraction,
            condition_ids=candidate.condition_ids,
            condition_operator=candidate.condition_operator,
            evidence_verified=False,human_adjudicated=False,
            source_ambiguity=False)
    except (ValueError,TypeError) as exc:
        return DraftBridgeResult("ABSTAIN",("IR_SCHEMA:"+str(exc),),None,tuple(names))
    return DraftBridgeResult(
        "EVIDENCE_MATCHED_AI_DRAFT_NEEDS_SEMANTIC_REVIEW",
        ("EXACT_QUOTATIONS_MATCH_BUT_MEANING_UNADJUDICATED",),ir,tuple(names))
