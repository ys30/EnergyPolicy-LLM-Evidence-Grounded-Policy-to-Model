"""Deliberately narrow, NON-LLM extraction baseline for synthetic test sentences."""
import re
from typing import Optional


def extract_percent_year(text: str) -> Optional[tuple[float, int]]:
    match = re.search(r"(?P<pct>\d+(?:\.\d+)?)\s*%\s+(?:by|no later than)\s+(?P<year>20\d{2})\b", text, flags=re.I)
    if not match:
        return None
    return (float(match.group('pct')) / 100.0, int(match.group('year')))
