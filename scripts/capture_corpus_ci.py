"""Capture two primary New Mexico regulations on a GitHub-hosted runner.

Do not commit frozen full text automatically. The artifact contains candidates,
snapshots, and an audit manifest, all tagged UNREVIEWED.
"""
import json
import re
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from energy_policy_llm.sources import fetch_official_html, html_to_text
from energy_policy_llm.candidates import extract_candidates, verify_candidates, export_candidates

SOURCES = (
    ("NM_IOU_2023", "https://www.srca.nm.gov/parts/title17/17.009.0572.html",
     "17.9.572.10", "2023-02-28"),
    ("NM_COOP_2025", "https://www.srca.nm.gov/wp-content/uploads/2025/06/17.9.571.html",
     "17.9.571.8", "2025-06-24"),
)

def capture(output: Path):
    output.mkdir(parents=True, exist_ok=True)
    manifest = {"schema_version": "1.3.0", "status": "unreviewed_source_capture",
                "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                "sources": [], "gold_count": 0, "llm_calls": 0}
    for source_id, url, required_section, version in SOURCES:
        html = fetch_official_html(url)
        text = html_to_text(html)
        # Prevent uploading an error page disguised as official law
        if len(text) < 1200 or required_section not in text:
            raise RuntimeError(f"{source_id}: incomplete or unexpected regulatory page")
        if not re.search(r"RENEWABLE\s+(?:PORTFOLIO|ENERGY)", text, re.I):
            raise RuntimeError(f"{source_id}: missing expected regulatory subject")
        snapshot = output / f"{source_id}.txt"
        if snapshot.exists():
            raise FileExistsError(snapshot)
        snapshot.write_text(text, encoding="utf-8")
        candidates = extract_candidates(text, source_id, version)
        verify_candidates(candidates, text)
        if len(candidates) == 0:
            raise RuntimeError(f"{source_id}: zero candidates; inspect HTML normalization")
        candidate_path = output / f"{source_id}.candidates.json"
        export_candidates(candidates, candidate_path)
        manifest["sources"].append({
            "source_id": source_id, "official_url": url, "rule_version": version,
            "normalized_text_sha256": sha256(text.encode("utf-8")).hexdigest(),
            "normalized_characters": len(text), "candidate_count": len(candidates),
            "required_section": required_section, "gold_status": "unreviewed",
            "snapshot_file": snapshot.name, "candidate_file": candidate_path.name
        })
    (output / "capture_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return manifest

if __name__ == "__main__":
    capture(Path("outputs/official_corpus"))
