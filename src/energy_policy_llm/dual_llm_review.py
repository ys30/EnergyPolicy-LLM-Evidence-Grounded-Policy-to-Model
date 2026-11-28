"""Dual-LLM + single-human verification queue. No model calls or gold promotion.

The compared records must be independently generated and preserve model provenance.
Agreement is a triage signal only; every case still requires human source review.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

REQUIRED = ("case_id", "source_id", "model_id", "model_version", "prompt_sha256",
            "source_sha256", "predicted_fields", "evidence_spans")
REVIEW_DECISIONS = {"ACCEPT", "CORRECT", "REJECT", "UNCERTAIN"}
CRITICAL_FIELDS = ("obligation_holder", "legal_semantic_type", "normative_force",
                   "target_fraction", "target_date", "numerator_metric",
                   "denominator_metric", "antecedent_conditions",
                   "rec_accounting", "source_ambiguity")


def load_jsonl(path: str | Path) -> list[dict]:
    rows = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        raise ValueError("Empty model prediction file")
    return rows


def validate_prediction(row: dict, source_texts: dict[str, str] | None = None) -> None:
    if not isinstance(row, dict) or not all(k in row for k in REQUIRED):
        raise ValueError("Incomplete model provenance or prediction")
    for field in ("case_id", "source_id", "model_id", "model_version", "prompt_sha256", "source_sha256"):
        v = row[field]
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Empty provenance: " + field)
    for field in ("prompt_sha256", "source_sha256"):
        v = row[field]
        if len(v) != 64 or any(ch not in "0123456789abcdef" for ch in v):
            raise ValueError("Invalid SHA-256: " + field)
    if not isinstance(row["predicted_fields"], dict):
        raise ValueError("predicted_fields must be an object")
    if not isinstance(row["evidence_spans"], list) or not row["evidence_spans"]:
        raise ValueError("At least one evidence span is required")
    fraction = row["predicted_fields"].get("target_fraction")
    if fraction is not None and (isinstance(fraction, bool) or not isinstance(fraction, (int, float)) or not 0 <= fraction <= 1):
        raise ValueError("Invalid target fraction")
    source = None
    if source_texts is not None:
        if row["source_id"] not in source_texts:
            raise ValueError("Missing frozen source snapshot")
        source = source_texts[row["source_id"]]
        if sha256(source.encode("utf-8")).hexdigest() != row["source_sha256"]:
            raise ValueError("Source hash mismatch")
    for span in row["evidence_spans"]:
        if not isinstance(span, dict) or not all(k in span for k in ("start_char", "end_char", "exact_text")):
            raise ValueError("Invalid evidence span")
        a, b, quote = span["start_char"], span["end_char"], span["exact_text"]
        if not isinstance(a, int) or isinstance(a, bool) or not isinstance(b, int) or isinstance(b, bool) or not 0 <= a < b:
            raise ValueError("Invalid evidence offsets")
        if source is not None and (b > len(source) or source[a:b] != quote):
            raise ValueError("Evidence does not match frozen source")


def create_comparison_queue(a: list[dict], b: list[dict], source_texts: dict[str, str] | None = None) -> dict:
    for row in a + b:
        validate_prediction(row, source_texts)
    ai = {r["case_id"]: r for r in a}
    bi = {r["case_id"]: r for r in b}
    if len(ai) != len(a) or len(bi) != len(b) or set(ai) != set(bi):
        raise ValueError("Duplicate or mismatched case IDs")
    output = []
    for case_id in sorted(ai):
        x, y = ai[case_id], bi[case_id]
        if x["source_id"] != y["source_id"] or x["source_sha256"] != y["source_sha256"]:
            raise ValueError("Different source snapshots for case " + case_id)
        if x["model_id"] == y["model_id"] and x["model_version"] == y["model_version"]:
            raise ValueError("Two annotators must have distinct pinned model identities")
        keys = sorted(set(x["predicted_fields"]) | set(y["predicted_fields"]))
        differences = [
            {"field": key, "a": x["predicted_fields"].get(key), "b": y["predicted_fields"].get(key)}
            for key in keys if x["predicted_fields"].get(key) != y["predicted_fields"].get(key)
        ]
        span_agreement = x["evidence_spans"] == y["evidence_spans"]
        output.append({
            "case_id": case_id, "source_id": x["source_id"], "source_sha256": x["source_sha256"],
            "ai_a": x, "ai_b": y, "field_disagreements": differences,
            "evidence_span_agreement": span_agreement,
            "critical_field_disagreements": [d["field"] for d in differences if d["field"] in CRITICAL_FIELDS],
            "triage_status": "AI_AGREED" if not differences and span_agreement else "AI_DISAGREED",
            "human_review_required": True, "human_review": None,
            "reference_status": "NOT_HUMAN_VERIFIED", "gold_eligible": False,
        })
    count = Counter(r["triage_status"] for r in output)
    return {
        "protocol": "DUAL_LLM_SINGLE_HUMAN_VERIFICATION",
        "case_count": len(output),
        "ai_agreed": count["AI_AGREED"], "ai_disagreed": count["AI_DISAGREED"],
        "human_verified": 0, "gold_count": 0, "records": output,
    }


def register_human_review(item: dict, review: dict, source_text: str) -> dict:
    """Register a real human's full source inspection; never auto-label as independent-human gold."""
    if item.get("human_review") is not None:
        raise ValueError("Review already submitted; keep immutable history")
    required = {"reviewer_id", "decision", "reviewed_all_fields", "reviewed_full_source_context",
                "final_fields", "rationale", "reviewed_evidence_spans"}
    if not isinstance(review, dict) or not required.issubset(review):
        raise ValueError("Incomplete human-review record")
    if not isinstance(review["reviewer_id"], str) or not review["reviewer_id"].strip():
        raise ValueError("Human reviewer ID required")
    if review["decision"] not in REVIEW_DECISIONS:
        raise ValueError("Invalid human decision")
    if review["reviewed_all_fields"] is not True or review["reviewed_full_source_context"] is not True:
        raise ValueError("Human must explicitly review all fields and source context")
    if not isinstance(review["rationale"], str) or not review["rationale"].strip():
        raise ValueError("Review rationale required")
    if not isinstance(review["final_fields"], dict):
        raise ValueError("Final fields must be an object")
    if review["decision"] in ("ACCEPT", "CORRECT") and not review["final_fields"]:
        raise ValueError("Accepted/corrected review must include full final fields")
    validate_prediction({
        **item["ai_a"], "predicted_fields": review["final_fields"],
        "evidence_spans": review["reviewed_evidence_spans"],
    }, {item["source_id"]: source_text})
    return {
        **item,
        "human_review": review,
        "reference_status": "HUMAN_VERIFIED" if review["decision"] in ("ACCEPT", "CORRECT") else "EXPERT_REVIEW_REQUIRED",
        "gold_eligible": False,
    }
