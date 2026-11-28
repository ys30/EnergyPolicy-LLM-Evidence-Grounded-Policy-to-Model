"""Lossless, source-hash-bound legal sections and subsection spans for RAG.

This deterministic chunker does not assume each text line is an atomic obligation.
The original snapshot is immutable and all evidence offsets are end-exclusive.
"""
from dataclasses import dataclass
from hashlib import sha256
import re
from .candidates import SECTION

# Real subsection heads are usually indented A., B., etc, at the start of a line.
# Full section text is always retained to avoid dropping the title/preamble.
SUBSECTION = re.compile(r"(?m)^[ \t\u00a0]+([A-Z])\.[ \t\u00a0]+")
@dataclass(frozen=True)
class LegalChunk:
    chunk_id: str
    source_id: str
    source_sha256: str
    provision: str
    subsection: str | None
    start_char: int
    end_char: int
    exact_text: str
    parent_chunk_id: str | None = None

def chunk_legal_text(text: str, source_id: str, *, include_sections: bool = True) -> list[LegalChunk]:
    if not text or not source_id:
        raise ValueError("Source text and identifier required")
    digest = sha256(text.encode("utf-8")).hexdigest()
    headings = list(SECTION.finditer(text))
    if not headings:
        raise ValueError("No official numbered sections recognized")
    ids = [m.group(1) for m in headings]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate legal section headings")
    result: list[LegalChunk] = []
    for i, head in enumerate(headings):
        start = head.start()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        section_id = head.group(1)
        parent_id = f"{source_id}:{section_id}"
        if include_sections:
            result.append(LegalChunk(parent_id, source_id, digest, section_id,
                                     None, start, end, text[start:end]))
        matches = list(SUBSECTION.finditer(text, head.end(), end))
        # Skip ambiguous duplicate letter markers or accidental prose markers
        # rather than silently manufacturing a subsection tree.
        used = set()
        for j, sub in enumerate(matches):
            label = sub.group(1)
            if label in used:
                continue
            used.add(label)
            sub_end = matches[j+1].start() if j+1 < len(matches) else end
            sub_start = sub.start()
            result.append(LegalChunk(f"{parent_id}:{label}", source_id, digest,
                                     section_id, label, sub_start, sub_end,
                                     text[sub_start:sub_end], parent_id))
    return result

def verify_chunks(text: str, chunks: list[LegalChunk]) -> None:
    digest = sha256(text.encode("utf-8")).hexdigest()
    seen = set()
    for chunk in chunks:
        if chunk.chunk_id in seen:
            raise ValueError("Duplicate chunk ID")
        seen.add(chunk.chunk_id)
        if chunk.source_sha256 != digest:
            raise ValueError("Source hash mismatch")
        if not 0 <= chunk.start_char < chunk.end_char <= len(text):
            raise ValueError("Illegal chunk bounds")
        if text[chunk.start_char:chunk.end_char] != chunk.exact_text:
            raise ValueError("Chunk evidence mismatch")
