"""Read already-frozen official source files; verify RAG spans and legal section coverage.

This is a deterministic retrieval smoke check; do NOT score model accuracy/gold.
"""
import json
from pathlib import Path
from energy_policy_llm.legal_chunker import chunk_legal_text, verify_chunks
from energy_policy_llm.reference_graph import build_reference_graph
from energy_policy_llm.retrievers import BM25LegalRetriever
from energy_policy_llm.evidence_bundle import assemble_evidence

def audit(root: Path):
    manifest=json.loads((root/"capture_manifest.json").read_text(encoding="utf-8"))
    reports=[]
    queries={"NM_COOP_2025":"renewable portfolio standard certificates",
             "NM_IOU_2023":"renewable portfolio standard annual compliance report"}
    for source in manifest["sources"]:
        text=(root/source["snapshot_file"]).read_text(encoding="utf-8")
        chunks=chunk_legal_text(text,source["source_id"])
        verify_chunks(text,chunks)
        subsections=[c for c in chunks if c.subsection is not None]
        docs=subsections or [c for c in chunks if c.subsection is None]
        retriever=BM25LegalRetriever(docs)
        edges=build_reference_graph(chunks,manually_flagged={
            ("17.9.571.11","17.9.571.13"): "suspected statutory cross-reference mismatch"})
        bundle=assemble_evidence(queries[source["source_id"]],source["source_id"],
                                 retriever,chunks,edges,top_k=3)
        count=sum(c.subsection is None for c in chunks)
        assert count == source["review_sections"]
        assert bundle.source_sha256 == source["normalized_text_sha256"]
        reports.append({"source_id":source["source_id"],
                        "source_sha256":bundle.source_sha256,
                        "sections":count,
                        "subsection_chunks":len(subsections),
                        "reference_edges":len(edges),
                        "query":bundle.query,
                        "retrieved_ids":list(bundle.retrieval_hits),
                        "context_ids":list(bundle.graph_expanded_chunks),
                        "ambiguous_reference_count":sum(bool(e.ambiguity_flag) for e in edges),
                        "status":"deterministic_retrieval_smoke_not_gold"})
    output=root/"rag_audit.json"
    output.write_text(json.dumps({"gold_count":0,"llm_calls":0,"reports":reports},
                                 indent=2)+"\n",encoding="utf-8")
    print(json.dumps(reports,indent=2))
    return reports

if __name__=="__main__":
    audit(Path("outputs/official_corpus"))
