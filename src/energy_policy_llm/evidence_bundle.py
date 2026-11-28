"""Deterministic evidence bundling; retrieval is not human adjudication."""
from dataclasses import asdict, dataclass
from .legal_chunker import LegalChunk
from .reference_graph import ReferenceEdge
from .retrievers import BM25LegalRetriever

@dataclass(frozen=True)
class EvidenceBundle:
    query: str
    source_id: str
    source_sha256: str
    evidence_chunks: tuple[LegalChunk, ...]
    retrieval_hits: tuple[str, ...]
    graph_expanded_chunks: tuple[str, ...]
    unresolved_references: tuple[str, ...]
    source_ambiguities: tuple[str, ...]
    status: str = "UNREVIEWED_RETRIEVAL_EVIDENCE_NOT_GOLD"

def assemble_evidence(query: str, source_id: str,
                      retriever: BM25LegalRetriever,
                      chunks: list[LegalChunk], edges: list[ReferenceEdge],
                      *, top_k: int = 3, max_chunks: int = 10) -> EvidenceBundle:
    if top_k < 1 or max_chunks < 1:
        raise ValueError("Positive limits required")
    hits = retriever.search(query, top_k, source_id=source_id)
    if not hits:
        raise ValueError("No matching evidence; abstain rather than hallucinate")
    by_id = {c.chunk_id: c for c in chunks if c.source_id == source_id}
    sections = {c.provision: c for c in chunks if c.source_id == source_id and c.subsection is None}
    chosen, seen, expanded, unresolved, ambiguous = [], set(), [], [], []
    def add(c: LegalChunk, graph: bool = False):
        if c.chunk_id in seen or len(chosen) >= max_chunks:
            return
        seen.add(c.chunk_id)
        chosen.append(c)
        if graph:
            expanded.append(c.chunk_id)
    for hit in hits:
        if hit.chunk.chunk_id not in by_id:
            raise ValueError("Inconsistent source corpus")
        add(hit.chunk)
    # Preserve parent section for context before expanding external references.
    for hit in hits:
        c = hit.chunk
        if c.parent_chunk_id and c.parent_chunk_id in by_id:
            add(by_id[c.parent_chunk_id], graph=True)
    # Expand only literal explicit references located inside matched evidence.
    for edge in edges:
        if edge.source_chunk_id not in seen:
            continue
        if edge.ambiguity_flag:
            ambiguous.append(edge.reference_text + ": " + edge.ambiguity_flag)
            # Never silently follow a structurally suspicious source reference.
            continue
        target = sections.get(edge.target_provision)
        if target is None:
            unresolved.append(edge.reference_text)
            continue
        add(target, graph=True)
    digest = hits[0].chunk.source_sha256
    if any(c.source_sha256 != digest for c in chosen):
        raise ValueError("Mixed source versions")
    return EvidenceBundle(query, source_id, digest, tuple(chosen),
                          tuple(h.chunk.chunk_id for h in hits),
                          tuple(expanded), tuple(sorted(set(unresolved))),
                          tuple(sorted(set(ambiguous))))

def serializable_bundle(bundle: EvidenceBundle) -> dict:
    return asdict(bundle)
