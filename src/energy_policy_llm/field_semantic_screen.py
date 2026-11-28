"""Conservative field-level contradiction / insufficiency screen for AI legal drafts.

This module NEVER certifies legal entailment. Its checks detect a narrow,
auditable set of known semantic failure modes and flag everything else for
independent review. The exact-quote validator remains a separate prerequisite.
"""
from dataclasses import dataclass
import re
from .field_evidence import FieldEvidence
from .policy_ir import MetricV2

@dataclass(frozen=True)
class SemanticFlag:
    field_name: str
    code: str
    severity: str
    explanation: str

_PERCENT_WORDS = {
    0.4: ("forty percent", "40 percent", "40%"),
    0.5: ("fifty percent", "50 percent", "50%"),
    0.8: ("eighty percent", "80 percent", "80%"),
    1.0: ("one hundred percent", "100 percent", "100%"),
}
_ENTITY_PHRASES = {
    "distribution_cooperative": ("distribution cooperative", "distribution cooperatives"),
    "generation_transmission_cooperative": (
        "generation and transmission cooperative",
        "generation and transmission cooperatives",
        "generation-transmission cooperative"),
    "cooperative": ("cooperative", "cooperatives"),
}
_CONDITION_WORDS = {
    "technical": ("technical", "technically", "feasibility", "feasible"),
    "reliability": ("reliable", "reliability"),
    "affordability": ("affordable", "affordability", "cost"),
}

def screen_field_semantics(candidate, *, evidence_text_by_field: dict[str,str]) -> tuple[SemanticFlag,...]:
    """Detect unsupported shortcuts, not positive legal validity.

    A legal entity may be supported by an external definition or cross-reference:
    absence of an entity phrase in the cited span is flagged for human examination,
    not asserted as a definitive legal contradiction.
    """
    flags=[]
    def flag(field, code, explanation):
        flags.append(SemanticFlag(field,code,"REVIEW_REQUIRED",explanation))
    entity=evidence_text_by_field.get("entity_id","").lower()
    known=_ENTITY_PHRASES.get(candidate.entity_id)
    if known and not any(phrase in entity for phrase in known):
        flag("entity_id","ENTITY_SUPPORT_NOT_VISIBLE",
             "Cited entity quote does not name claimed legal entity; inspect definitions and responsibility cross-references")
    fraction=evidence_text_by_field.get("target_fraction","").lower()
    if candidate.target_fraction is not None and fraction:
        expected=_PERCENT_WORDS.get(round(candidate.target_fraction,6))
        if expected is None:
            flag("target_fraction","FRACTION_NOT_CHECKED_BY_RULES",
                 "Nonstandard percentage requires independent numeric interpretation")
        elif not any(v in fraction for v in expected):
            flag("target_fraction","FRACTION_QUOTE_MISMATCH",
                 "Cited percentage text does not explicitly match proposed fraction")
    year=evidence_text_by_field.get("year","")
    if candidate.year is not None and year and not re.search(rf"(?<!\d){candidate.year}(?!\d)",year):
        flag("year","YEAR_QUOTE_MISMATCH","Cited date does not explicitly contain the proposed year")
    metric=evidence_text_by_field.get("metric","").lower()
    if candidate.metric in (MetricV2.RENEWABLE_RETAIL_SALES.value,
                            MetricV2.ZERO_CARBON_RETAIL_SALES.value):
        if metric and not ("retail" in metric or "sales" in metric):
            flag("metric","RETAIL_DENOMINATOR_NOT_SUPPORTED",
                 "Cited metric does not mention retail/sales; local generation is not retail sales")
        if "generation share" in metric or "total generation" in metric:
            flag("metric","GENERATION_RETAIL_CONFLATION",
                 "Cited metric uses generation-share terminology for a retail-sales claim")
    if candidate.legal_type == "CONDITIONAL_TARGET":
        if candidate.condition_operator != "ALL" or not candidate.condition_ids:
            flag("condition_operator","CONDITIONS_INCOMPLETE",
                 "Conditional target requires explicit list and ALL conjunction for this pilot")
        cited=evidence_text_by_field.get("condition_ids","").lower()
        for name in candidate.condition_ids:
            synonyms=_CONDITION_WORDS.get(name)
            if synonyms is not None and not any(w in cited for w in synonyms):
                flag("condition_ids","CONDITION_SUPPORT_NOT_VISIBLE:"+name,
                     "Condition absent from cited span; inspect full provision before compilation")
    if candidate.provision.startswith("17.9.571.11") and any(
        "17.9.571.13(" in x.lower() for x in evidence_text_by_field.values()):
        flag("source","SUSPECT_CROSS_REFERENCE",
             "Literal reference from section 11 to section 13 requires explicit ambiguity review")
    return tuple(flags)
