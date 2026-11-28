"""Explicit regulatory cross-references; suspected legal typos are NOT auto-corrected."""
from dataclasses import dataclass
import re
from .legal_chunker import LegalChunk

REF = re.compile(r"\\b(17\\.9\\.(?:571|572)\\.\\d+)(?:\\(([A-Z])\\))?(?![A-Za-z0-9_])")

@dataclass(frozen=True)
class ReferenceEdge:
    source_chunk_id: str
    target_provision: str
    target_subsection: str | None
    reference_text: str
    evidence_start_char: int
    evidence_end_char: int
    target_present_in_corpus: bool
    ambiguity_flag: str | None

def build_reference_graph(chunks: list[LegalChunk],
                          *, manually_flagged: dict[tuple[str, str], str] | None = None
                          ) -> list[ReferenceEdge]:
    """No correction, inference of target clause or cross-version linking."""
    flagged = manually_flagged or {}
    sections = {c.provision for c in chunks if c.subsection is None}
    edges = []
    # The graph is built on subsection chunks when available, otherwise section.
    child_sections = {c.provision for c in chunks if c.subsection is not None}
    for c in chunks:
        if c.subsection is None and c.provision in child_sections:
            continue
        for m in REF.finditer(c.exact_text):
            target = m.group(1)
            full = m.group(0)
            # Self-references are kept when a subsection differs or statute references itself.
            if target == c.provision and m.group(2) is None:
                continue
            edges.append(ReferenceEdge(c.chunk_id, target, m.group(2), full,
                c.start_char + m.start(), c.start_char + m.end(),
                target in sections,
                flagged.get((c.provision, target))))
    return edges
