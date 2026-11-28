"""Retrieval metrics against explicit relevance sets; cannot manufacture gold."""
from dataclasses import dataclass
from .retrievers import BM25LegalRetriever

@dataclass(frozen=True)
class RetrievalCase:
    query_id: str
    query: str
    relevant_chunk_ids: frozenset[str]
    source_id: str
    reference_status: str = "SYNTHETIC"

    def __post_init__(self):
        if not self.query_id or not self.query or not self.source_id or not self.relevant_chunk_ids:
            raise ValueError("Retrieval case requires query and known relevant IDs")
        if self.reference_status not in {"SYNTHETIC","HUMAN_ADJUDICATED"}:
            raise ValueError("Do not mark AI suggestions as adjudicated reference")

def evaluate_retrieval(retriever: BM25LegalRetriever,
                       cases: list[RetrievalCase], *,
                       k: int = 5, require_human_gold: bool = False) -> dict:
    if not cases or k < 1:
        raise ValueError("Cases and positive k required")
    if require_human_gold and any(c.reference_status != "HUMAN_ADJUDICATED" for c in cases):
        raise ValueError("Formal metrics require independent human-adjudicated relevance")
    per_case = []
    for case in cases:
        retrieved = [h.chunk.chunk_id for h in retriever.search(case.query, k, source_id=case.source_id)]
        relevant = set(case.relevant_chunk_ids)
        hits = len(set(retrieved) & relevant)
        per_case.append({"query_id":case.query_id,"retrieved":retrieved,
                         "relevant_total":len(relevant),"relevant_found":hits,
                         "recall_at_k":hits/len(relevant),
                         "all_references_found":hits == len(relevant),
                         "reference_status":case.reference_status})
    return {"k":k,"case_count":len(cases),"mean_recall_at_k":
            sum(r["recall_at_k"] for r in per_case)/len(per_case),
            "all_references_found_rate":
            sum(r["all_references_found"] for r in per_case)/len(per_case),
            "formal_human_gold":all(c.reference_status=="HUMAN_ADJUDICATED" for c in cases),
            "cases":per_case}
