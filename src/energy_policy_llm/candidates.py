"""Extract traceable unreviewed candidates from locally frozen policy text."""
from dataclasses import dataclass, asdict
from hashlib import sha256
from pathlib import Path
import json
import re

SECTION = re.compile(r"(?m)^\s*(17\.9\.(?:571|572)\.\d+)\s+([A-Z][^\n]{2,100})")
SIGNAL = re.compile(r"\b(?:percent|percentage|renewable|portfolio|certificate|retail|cost|compliance|cooperative|public utility)\b", re.I)

@dataclass(frozen=True)
class Candidate:
    source_id: str
    source_sha256: str
    source_version: str
    provision: str
    start_char: int
    end_char: int
    exact_text: str
    status: str = "candidate_unreviewed"

def extract_candidates(text: str, source_id: str, source_version: str, limit: int | None = None) -> list[Candidate]:
    if not source_id or not source_version or (limit is not None and (not isinstance(limit, int) or isinstance(limit, bool) or limit < 1)):
        raise ValueError("Source identity/version and positive limit required")
    digest = sha256(text.encode("utf-8")).hexdigest()
    matches = list(SECTION.finditer(text))
    found = []
    for i, match in enumerate(matches):
        end = matches[i+1].start() if i + 1 < len(matches) else len(text)
        offset = match.start()
        for line in text[match.start():end].splitlines(keepends=True):
            clean = line.strip()
            if clean and SIGNAL.search(clean) and len(clean) >= 12:
                start = offset + len(line) - len(line.lstrip())
                stop = offset + len(line.rstrip())
                if stop > start:
                    found.append(Candidate(source_id, digest, source_version, match.group(1), start, stop, text[start:stop]))
                    if limit is not None and len(found) >= limit:
                        return found
            offset += len(line)
    return found

def verify_candidates(candidates: list[Candidate], text: str) -> None:
    digest = sha256(text.encode("utf-8")).hexdigest()
    for c in candidates:
        if c.source_sha256 != digest or c.status != "candidate_unreviewed":
            raise ValueError("Hash mismatch or forbidden status promotion")
        if not (0 <= c.start_char < c.end_char <= len(text)):
            raise ValueError("Invalid source offsets")
        if text[c.start_char:c.end_char] != c.exact_text:
            raise ValueError("Source excerpt does not match snapshot")

def export_candidates(candidates: list[Candidate], output: str | Path) -> None:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError("Refusing to overwrite candidate file")
    path.write_text(json.dumps([asdict(c) for c in candidates], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
