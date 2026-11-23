"""Model-independent prediction import. No API calls or fabricated gold scores.

Input JSONL is generated externally from real model calls. Provenance, prompt,
model version and source IDs are mandatory for audit, but are not proof of truth.
"""
import json
from pathlib import Path

FIELDS = {"target_fraction", "target_date", "obligated_entities", "numerator", "denominator"}
DECISIONS = {"ABSTAIN", "SCENARIO_PROXY", "LEGAL_CONSTRAINT"}


def parse_predictions(lines: list[str]) -> dict:
    records = []
    seen = set()
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at line {number}") from exc
        needed = {"case_id", "model_id", "model_version", "prompt_sha256",
                  "source_id", "predicted_fields", "predicted_decision"}
        if not isinstance(record, dict) or not needed.issubset(record):
            raise ValueError(f"Missing metadata at line {number}")
        if not isinstance(record["predicted_fields"], dict) or not FIELDS.issubset(record["predicted_fields"]):
            raise ValueError(f"Missing required prediction fields at line {number}")
        if record["predicted_decision"] not in DECISIONS:
            raise ValueError(f"Invalid decision at line {number}")
        if not all(isinstance(record[key], str) and record[key].strip() for key in (
                "case_id", "model_id", "model_version", "source_id")):
            raise ValueError(f"Empty metadata at line {number}")
        digest = record["prompt_sha256"]
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError(f"Invalid prompt SHA-256 at line {number}")
        if record["case_id"] in seen:
            raise ValueError("Duplicate case_id")
        seen.add(record["case_id"])
        frac = record["predicted_fields"]["target_fraction"]
        if frac is not None and (isinstance(frac, bool) or not isinstance(frac, (int, float)) or not 0 <= frac <= 1):
            raise ValueError("Invalid target_fraction")
        records.append(record)
    if not records:
        raise ValueError("Empty predictions")
    return {"count": len(records), "case_ids": sorted(seen), "records": records}


def load_predictions(path: str | Path) -> dict:
    return parse_predictions(Path(path).read_text(encoding="utf-8").splitlines())
