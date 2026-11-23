"""Hard gates for a real held-out policy evaluation.

This validates provenance metadata, not the truth of a legal interpretation.
No model and no gold data are created by this module.
"""
from dataclasses import dataclass
from collections import defaultdict
from hashlib import sha256
import re


@dataclass(frozen=True)
class GoldProvenance:
    case_id: str
    instrument_id: str
    jurisdiction: str
    split: str
    snapshot_sha256: str
    source_version: str
    provision: str
    quote: str
    start_char: int
    end_char: int
    annotator_1: str
    annotator_2: str
    adjudicator: str
    adjudicated: bool

    def check(self, frozen_text: str) -> None:
        if not self.adjudicated:
            raise ValueError("Unadjudicated source cannot be used as gold")
        if len({self.annotator_1, self.annotator_2}) != 2 or not all(
            (self.annotator_1, self.annotator_2, self.adjudicator)
        ):
            raise ValueError("Two independently identified annotators and adjudicator required")
        if not self.case_id or not self.instrument_id or not self.jurisdiction:
            raise ValueError("Missing case or grouping identifier")
        if not self.source_version or not self.provision:
            raise ValueError("Missing legal source version/provision")
        if not re.fullmatch(r"[0-9a-f]{64}", self.snapshot_sha256):
            raise ValueError("Invalid SHA-256 identifier")
        if sha256(frozen_text.encode("utf-8")).hexdigest() != self.snapshot_sha256:
            raise ValueError("Document snapshot hash mismatch")
        if not (0 <= self.start_char < self.end_char <= len(frozen_text)):
            raise ValueError("Invalid evidence offsets")
        if frozen_text[self.start_char:self.end_char] != self.quote:
            raise ValueError("Evidence quote differs from frozen text")


def gate_holdout(
    records: list[GoldProvenance],
    frozen_snapshots: dict[str, str],
    heldout_jurisdictions: set[str],
) -> dict:
    """Fail closed on instrument/version and jurisdiction leakage.

    heldout_jurisdictions must match all and only the jurisdictions in the test split.
    Do not call with invented reviewer IDs or fabricated snapshots.
    """
    if not records or not heldout_jurisdictions:
        raise ValueError("Nonempty records and declared held-out jurisdictions required")
    seen_cases = set()
    instrument_splits = defaultdict(set)
    source_splits = defaultdict(set)
    jurisdiction_splits = defaultdict(set)
    for record in records:
        if record.case_id in seen_cases:
            raise ValueError("Duplicate case ID")
        seen_cases.add(record.case_id)
        if record.split not in ("train", "validation", "test"):
            raise ValueError("Invalid split")
        if record.snapshot_sha256 not in frozen_snapshots:
            raise ValueError("Snapshot unavailable: cannot validate evidence")
        record.check(frozen_snapshots[record.snapshot_sha256])
        instrument_splits[record.instrument_id].add(record.split)
        source_splits[record.snapshot_sha256].add(record.split)
        jurisdiction_splits[record.jurisdiction].add(record.split)
    if any(len(s) > 1 for s in instrument_splits.values()):
        raise ValueError("Policy instrument leakage across splits")
    if any(len(s) > 1 for s in source_splits.values()):
        raise ValueError("Document snapshot leakage across splits")
    for jurisdiction, splits in jurisdiction_splits.items():
        if jurisdiction in heldout_jurisdictions:
            if splits != {"test"}:
                raise ValueError("Held-out jurisdiction seen in development split")
        elif "test" in splits:
            raise ValueError("Undeclared jurisdiction present in test split")
    if not any(r.split == "test" for r in records):
        raise ValueError("No held-out test cases")
    if not any(r.split in ("train", "validation") for r in records):
        raise ValueError("No development cases")
    return {"records": len(records), "unique_instruments": len(instrument_splits),
            "heldout_jurisdictions": sorted(heldout_jurisdictions),
            "provenance_validated": True, "legal_truth_guaranteed": False}
