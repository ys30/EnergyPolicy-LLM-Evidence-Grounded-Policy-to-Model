"""Source-anchor audit: verified locations are not automatically gold annotations."""
import json
from pathlib import Path

def validate_anchor_catalog(data: dict) -> dict:
    if data.get("schema_version") != "0.6.0":
        raise ValueError("Unsupported anchor catalog version")
    sources = {s["id"]: s for s in data["primary_sources"]}
    if len(sources) != len(data["primary_sources"]):
        raise ValueError("Duplicate source IDs")
    for source in sources.values():
        if not source["url"].startswith("https://www.srca.nm.gov/"):
            raise ValueError("Unexpected or untrusted source domain")
        if not source["effective_date"]:
            raise ValueError("Missing effective date")
    anchors = data["anchors"]
    if not anchors:
        raise ValueError("No evidence anchors")
    ids = set()
    counts = {}
    for a in anchors:
        if a["anchor_id"] in ids:
            raise ValueError("Duplicate anchor ID")
        ids.add(a["anchor_id"])
        if a["source_id"] not in sources:
            raise ValueError("Unknown primary source")
        if a.get("gold_status") != "not_adjudicated":
            raise ValueError("Anchor catalog must never assert gold status")
        if a.get("evidence_status") != "source_section_located":
            raise ValueError("Location has not been checked")
        if not a["provision"].startswith("17.9."):
            raise ValueError("Unexpected provision locator")
        source = a["source_id"]
        counts[source] = counts.get(source, 0) + 1
    return {"sources": len(sources), "section_anchors": len(anchors), "by_source": counts,
            "adjudicated_gold": 0, "research_result": False}

def load_catalog(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)
