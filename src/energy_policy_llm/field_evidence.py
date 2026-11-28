"""Validate field-level evidence in a frozen-source EvidenceBundle.

Evidence is necessary but never sufficient to prove legal interpretation;
matching only requires an exact quoted span in a retrieved chunk.
"""
from dataclasses import dataclass
from hashlib import sha256
from .evidence_bundle import EvidenceBundle

@dataclass(frozen=True)
class FieldEvidence:
    field_name: str
    proposed_value: str
    chunk_id: str
    start_char: int
    end_char: int
    exact_text: str

@dataclass(frozen=True)
class EvidenceCheck:
    field_name: str
    status: str
    reason: str

def validate_field_evidence(text: str, bundle: EvidenceBundle,
                            fields: list[FieldEvidence]) -> list[EvidenceCheck]:
    if sha256(text.encode("utf-8")).hexdigest() != bundle.source_sha256:
        raise ValueError("Frozen source digest mismatch")
    if not fields:
        raise ValueError("Every attempted field must carry source evidence or be withheld")
    chunks={c.chunk_id:c for c in bundle.evidence_chunks}
    results=[]
    for item in fields:
        if not item.field_name or not item.chunk_id:
            results.append(EvidenceCheck(item.field_name,"REJECT","MISSING_FIELD_OR_CHUNK_ID"))
            continue
        chunk=chunks.get(item.chunk_id)
        if chunk is None:
            results.append(EvidenceCheck(item.field_name,"REJECT","CHUNK_NOT_RETRIEVED"))
        elif not (chunk.start_char<=item.start_char<item.end_char<=chunk.end_char):
            results.append(EvidenceCheck(item.field_name,"REJECT","SPAN_OUTSIDE_RETRIEVED_CHUNK"))
        elif text[item.start_char:item.end_char]!=item.exact_text:
            results.append(EvidenceCheck(item.field_name,"REJECT","QUOTE_MISMATCH"))
        else:
            results.append(EvidenceCheck(item.field_name,"EVIDENCE_MATCHED_NOT_ADJUDICATED",
                                         "Exact source evidence matched; semantic correctness still unverified"))
    return results
