"""Provenance-gated evaluation: synthetic demo is never an empirical research score."""
import json
from pathlib import Path
from .benchmark import Case, evaluate
from .research_gate import GoldProvenance, gate_holdout

REQUIRED_FIELDS = ("target_fraction", "target_date", "obligated_entities", "denominator", "numerator")

def run_verified_evaluation(payload: dict, snapshots: dict, *, synthetic: bool = False) -> dict:
    if not isinstance(payload, dict) or not isinstance(snapshots, dict):
        raise ValueError("Payload/snapshots must be objects")
    if synthetic:
        if payload.get("dataset_kind") != "synthetic_fixture":
            raise ValueError("Synthetic flag requires labeled synthetic dataset")
        if snapshots:
            raise ValueError("Synthetic demo must not masquerade as real snapshots")
    elif payload.get("dataset_kind") != "human_adjudicated":
        raise ValueError("Empirical mode requires human_adjudicated dataset")
    gold = payload.get("gold_records", [])
    predictions = payload.get("predictions", [])
    if not gold or len(gold) != len(predictions):
        raise ValueError("Nonempty one-to-one gold and prediction records required")
    heldouts = payload.get("heldout_jurisdictions")
    if not isinstance(heldouts, list) or not heldouts or len(set(heldouts)) != len(heldouts):
        raise ValueError("Explicit unique held-out jurisdictions required")
    pred_by_id = {}
    for p in predictions:
        if p["case_id"] in pred_by_id:
            raise ValueError("Duplicate prediction")
        pred_by_id[p["case_id"]] = p
    gold_ids = [g["case_id"] for g in gold]
    if set(gold_ids) != set(pred_by_id) or len(gold_ids) != len(set(gold_ids)):
        raise ValueError("Predictions must match gold case IDs exactly")
    if synthetic:
        if any(g.get("gold_status") != "synthetic" for g in gold):
            raise ValueError("Synthetic mode requires synthetic gold_status")
        if not any(g["split"] in ("train", "validation") for g in gold):
            raise ValueError("Synthetic demo also requires development examples")
        if {g["jurisdiction"] for g in gold if g["split"] == "test"} != set(heldouts):
            raise ValueError("Declared holdout differs from test jurisdictions")
        if any(g["jurisdiction"] in heldouts for g in gold if g["split"] != "test"):
            raise ValueError("Held-out jurisdiction leaked into development")
    else:
        records = [GoldProvenance(**g["provenance"]) for g in gold]
        for g, r in zip(gold, records):
            if (g["case_id"], g["instrument_id"], g["jurisdiction"], g["split"]) != (r.case_id, r.instrument_id, r.jurisdiction, r.split):
                raise ValueError("Gold label mismatches evidence identity")
        gate_holdout(records, snapshots, set(heldouts))
    cases = []
    for g in gold:
        p = pred_by_id[g["case_id"]]
        if not all(k in g["gold_fields"] for k in REQUIRED_FIELDS):
            raise ValueError("Missing gold fields")
        cases.append(Case(g["case_id"], g["instrument_id"], g["jurisdiction"], g["split"],
                          "synthetic" if synthetic else "adjudicated", g["gold_fields"],
                          g["gold_decision"], p["predicted_fields"], p["predicted_decision"]))
    evaluate(cases, allow_synthetic=synthetic)  # enforces instrument-group isolation across all splits
    test = [c for c in cases if c.split == "test"]
    if not test:
        raise ValueError("No held-out test records")
    return {
        "dataset_kind": payload["dataset_kind"], "evaluation_scope": "test_only",
        "n_development": len(cases) - len(test), "n_test": len(test),
        "heldout_jurisdictions": sorted(heldouts),
        "test_metrics": evaluate(test, allow_synthetic=synthetic),
        "publication_ready": False if synthetic else "requires_manual_methods_review"
    }

def load_and_run(dataset_path: str, *, synthetic: bool = False, snapshots_path: str | None = None) -> dict:
    payload = json.loads(Path(dataset_path).read_text(encoding="utf-8"))
    snapshots = {} if snapshots_path is None else json.loads(Path(snapshots_path).read_text(encoding="utf-8"))
    return run_verified_evaluation(payload, snapshots, synthetic=synthetic)
