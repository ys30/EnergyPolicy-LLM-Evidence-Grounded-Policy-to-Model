"""Offline annotation quality gates. Only adjudicated evidence is eligible for gold metrics."""
from dataclasses import dataclass
from hashlib import sha256
from typing import Optional


@dataclass(frozen=True)
class EvidenceSpan:
    document_id: str
    snapshot_sha256: str
    start_char: int
    end_char: int
    quote: str
    source_version: str
    annotator_1: Optional[str] = None
    annotator_2: Optional[str] = None
    adjudicator: Optional[str] = None
    decision: str = "candidate"

    def validate(self, snapshot: str) -> None:
        if not self.document_id or not self.source_version:
            raise ValueError("Missing source identity or version")
        if sha256(snapshot.encode("utf-8")).hexdigest() != self.snapshot_sha256:
            raise ValueError("Snapshot hash mismatch; offsets cannot be trusted")
        if not (0 <= self.start_char < self.end_char <= len(snapshot)):
            raise ValueError("Invalid source offsets")
        if snapshot[self.start_char:self.end_char] != self.quote:
            raise ValueError("Quote does not match exact source span")
        if self.decision not in ("candidate", "disagreement", "adjudicated"):
            raise ValueError("Invalid decision")
        if self.decision == "adjudicated":
            if not all((self.annotator_1, self.annotator_2, self.adjudicator)):
                raise ValueError("Gold requires two annotators and adjudicator")
            if self.annotator_1 == self.annotator_2:
                raise ValueError("Independent annotators must differ")


def gold_ready(span: EvidenceSpan, snapshot: str) -> bool:
    span.validate(snapshot)
    return span.decision == "adjudicated"
