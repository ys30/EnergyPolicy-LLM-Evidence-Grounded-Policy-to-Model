"""Deliberately conservative text baseline. NOT an LLM or legal parser."""
import re

PERCENT = re.compile(r"(?<![\w.])(?P<value>\d{1,3}(?:\.\d+)?)\s*(?:%(?![\w])|percent\b)", re.I)
YEAR = re.compile(r"\b(?:20\d{2}|19\d{2})\b")

def extract_clause(fragment: str) -> dict:
    percentages = [float(m.group("value")) / 100 for m in PERCENT.finditer(fragment)]
    years = [int(m.group()) for m in YEAR.finditer(fragment)]
    if any(x > 1 for x in percentages):
        raise ValueError("Invalid percentage")
    s = fragment.lower()
    if "retail sales" in s or "retail energy sales" in s:
        denominator = "retail_sales"
    elif "generation" in s or "electricity generated" in s:
        denominator = "generation_mentioned_unresolved"
    else:
        denominator = "unresolved"
    return {
        "target_fraction": percentages[0] if len(percentages) == 1 else None,
        "target_year": years[0] if len(years) == 1 else None,
        "denominator": denominator,
        "decision": "ABSTAIN",
        "flags": ["fragment_only", "legal_scope_unverified"],
    }
