"""Completeness audit for lexical policy candidates; not a claim of semantic recall."""
from collections import Counter
import re
from .candidates import SECTION, SIGNAL, extract_candidates

SECTION_REF = re.compile(r"17\.9\.(?:571|572)\.\d+")

def audit_snapshot(text: str, source_id: str, source_version: str) -> dict:
    candidates = extract_candidates(text, source_id, source_version, limit=None)
    sections = list(SECTION.finditer(text))
    # Detect every keyword-bearing physical line, independent of the extractor.
    # A line within a section is expected to be covered by the uncapped extractor.
    line_start = 0
    keyword_lines = 0
    outside = []
    uncovered = []
    for line_number, line in enumerate(text.splitlines(keepends=True), 1):
        if SIGNAL.search(line) and line.strip():
            keyword_lines += 1
            left = line_start + len(line) - len(line.lstrip())
            right = line_start + len(line.rstrip())
            inside = any(m.start() <= left < (sections[i+1].start() if i+1 < len(sections) else len(text))
                         for i, m in enumerate(sections))
            covered = any(c.start_char == left and c.end_char == right for c in candidates)
            if not inside:
                outside.append({"line": line_number, "start": left, "sample": line.strip()[:160]})
            elif not covered:
                uncovered.append({"line": line_number, "start": left, "sample": line.strip()[:160]})
        line_start += len(line)
    by_section = Counter(c.provision for c in candidates)
    # The older 200 cap selected from the start of the document.
    old_count = min(200, len(candidates))
    return {
        "source_id": source_id,
        "candidate_count_uncapped": len(candidates),
        "previous_200_cap_count": old_count,
        "new_candidates_beyond_200": max(0, len(candidates) - 200),
        "keyword_lines_total": keyword_lines,
        "keyword_lines_outside_matched_sections_count": len(outside),
        "keyword_lines_inside_sections_uncovered_count": len(uncovered),
        "keyword_lines_outside_matched_sections": outside,
        "keyword_lines_inside_sections_uncovered": uncovered,
        "matched_section_count": len(sections),
        "matched_section_ids": [m.group(1) for m in sections],
        "referenced_section_ids_anywhere": sorted(set(SECTION_REF.findall(text))),
        "candidates_by_section": dict(sorted(by_section.items())),
        "audit_scope": "keyword-bearing physical lines only; no semantic recall guarantee",
        "requires_manual_review": True,
    }
