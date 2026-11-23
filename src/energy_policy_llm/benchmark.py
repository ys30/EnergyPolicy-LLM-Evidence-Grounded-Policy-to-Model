"""Deterministic, audit-friendly evaluation utilities. Standard library only.

Gold labels require external human adjudication; this module never invents them.
Synthetic fixtures may test evaluator correctness but are never research scores.
"""
from dataclasses import dataclass
from collections import defaultdict
from typing import Optional


FIELDS = ("target_fraction", "target_date", "obligated_entities", "denominator", "numerator")
DECISIONS = ("ABSTAIN", "SCENARIO_PROXY", "LEGAL_CONSTRAINT")


@dataclass(frozen=True)
class Case:
    case_id: str
    instrument_id: str
    jurisdiction: str
    split: str
    gold_status: str
    gold_fields: dict
    gold_decision: str
    predicted_fields: dict
    predicted_decision: str

    def validate(self, allow_synthetic: bool = False) -> None:
        if self.split not in ("train", "validation", "test"):
            raise ValueError("Unknown split")
        expected = "synthetic" if allow_synthetic else "adjudicated"
        if self.gold_status != expected:
            raise ValueError(f"Expected {expected} labels for this evaluation mode")
        if self.gold_decision not in DECISIONS or self.predicted_decision not in DECISIONS:
            raise ValueError("Unknown compiler decision")
        if not self.case_id or not self.instrument_id or not self.jurisdiction:
            raise ValueError("Missing group identifier")
        if not all(field in self.gold_fields for field in FIELDS):
            raise ValueError("Missing gold field")
        if not isinstance(self.predicted_fields, dict):
            raise ValueError("Predictions must be a JSON object")


def validate_splits(cases: list[Case]) -> None:
    """Disallow data leakage across amendments, clauses or versions of same policy."""
    seen_ids, group_splits, jurisdiction_splits = set(), defaultdict(set), defaultdict(set)
    for item in cases:
        if item.case_id in seen_ids:
            raise ValueError(f"Duplicate case_id {item.case_id}")
        seen_ids.add(item.case_id)
        group_splits[item.instrument_id].add(item.split)
        jurisdiction_splits[item.jurisdiction].add(item.split)
    leaks = [key for key, splits in group_splits.items() if len(splits) > 1]
    if leaks:
        raise ValueError(f"Instrument/version leakage: {leaks}")
    # Jurisdiction holdouts are specified by experiment, not universally mandated.
    return None


def evaluate(cases: list[Case], allow_synthetic: bool = False) -> dict:
    if not cases:
        raise ValueError("Cannot evaluate an empty collection")
    validate_splits(cases)
    for item in cases:
        item.validate(allow_synthetic=allow_synthetic)
    n = len(cases)
    fields = {}
    for key in FIELDS:
        correct = sum(item.predicted_fields.get(key) == item.gold_fields[key] for item in cases)
        fields[key] = {"correct": correct, "total": n, "exact_match": correct / n}
    exact = sum(all(item.predicted_fields.get(key) == item.gold_fields[key] for key in FIELDS) for item in cases)
    at_risk = [item for item in cases if item.gold_decision != "LEGAL_CONSTRAINT"]
    unsafe = sum(item.predicted_decision == "LEGAL_CONSTRAINT" for item in at_risk)
    abstain = sum(item.predicted_decision == "ABSTAIN" for item in cases)
    correct_decisions = sum(item.predicted_decision == item.gold_decision for item in cases)
    return {
        "n": n, "dataset_status": "synthetic_fixture" if allow_synthetic else "human_adjudicated",
        "field_metrics": fields,
        "all_fields_exact_match": exact / n,
        "compiler_decision_accuracy": correct_decisions / n,
        "unsafe_accept_count": unsafe,
        "unsafe_accept_rate": unsafe / n,
        "at_risk_count": len(at_risk),
        "unsafe_accept_rate_at_risk": unsafe / len(at_risk) if at_risk else None,
        "abstention_rate": abstain / n,
        "note": "At-risk excludes reference LEGAL_CONSTRAINT cases; null conditional rate means no at-risk records. Legal truth requires independent review.",
    }
