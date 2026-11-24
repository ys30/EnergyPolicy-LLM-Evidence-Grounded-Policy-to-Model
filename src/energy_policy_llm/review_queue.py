"""Section-level policy review queue built from *unreviewed* official snapshots."""
from hashlib import sha256
from .candidates import SECTION, extract_candidates, verify_candidates

PRIORITY = {
    "17.9.572.7": "definitions_and_denominator",
    "17.9.572.10": "renewable_portfolio_standard",
    "17.9.572.17": "rec_tracking",
    "17.9.572.19": "annual_compliance_reporting",
    "17.9.571.7": "entities_and_definitions",
    "17.9.571.8": "rps_and_rec_obligations",
    "17.9.571.10": "reasonable_cost_threshold",
}

def make_review_queue(text: str, source_id: str, source_version: str) -> dict:
    sections = list(SECTION.finditer(text))
    candidates = extract_candidates(text, source_id, source_version)
    verify_candidates(candidates, text)
    output = []
    for i, match in enumerate(sections):
        start = match.start()
        end = sections[i + 1].start() if i + 1 < len(sections) else len(text)
        provision = match.group(1)
        selected = [c for c in candidates if start <= c.start_char < end]
        output.append({
            "review_id": source_id + ":" + provision,
            "source_id": source_id,
            "source_sha256": sha256(text.encode("utf-8")).hexdigest(),
            "source_version": source_version,
            "provision": provision,
            "priority": "high" if provision in PRIORITY else "normal",
            "research_issue": PRIORITY.get(provision),
            "section_start_char": start,
            "section_end_char": end,
            "section_text": text[start:end],
            "candidate_count": len(selected),
            "candidate_spans": [{"start_char": c.start_char, "end_char": c.end_char} for c in selected],
            "status": "unreviewed_requires_independent_annotation",
        })
    return {
        "source_id": source_id,
        "source_sha256": sha256(text.encode("utf-8")).hexdigest(),
        "source_version": source_version,
        "gold_count": 0,
        "section_count": len(output),
        "priority_section_count": sum(r["priority"] == "high" for r in output),
        "sections": output,
    }
