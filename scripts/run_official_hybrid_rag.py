"""Diagnostic: genuine sentence-transformer vs BM25 on frozen official NM text.

No legal extraction is called. Provisional provision queries are NOT human gold.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
from energy_policy_llm.hybrid_retrieval import HybridRetriever, SentenceTransformerEncoder
from energy_policy_llm.legal_chunker import chunk_legal_text, verify_chunks
from energy_policy_llm.retrievers import BM25LegalRetriever
from energy_policy_llm.reference_graph import build_reference_graph
from energy_policy_llm.evidence_bundle import assemble_evidence

# Queries are researcher-/AI-authored smoke tests tied to known provision IDs,
# NOT gold relevance sets or held-out retrieval evaluation.
PROBES = [
    ("NM_COOP_2025","17.9.571.8","B","2025 forty percent renewable retail sales"),
    ("NM_COOP_2025","17.9.571.8","D","2050 eighty percent feasibility reliability affordability"),
    ("NM_COOP_2025","17.9.571.9","A","2050 one hundred percent zero carbon electricity"),
    ("NM_COOP_2025","17.9.571.10","A","cooperative sixty dollars per megawatt hour reasonable cost"),
    ("NM_COOP_2025","17.9.571.11","D","WREGIS registration of renewable energy certificates"),
]

def make_report(root: Path, output: Path, model_id: str, revision: str | None, top_k: int):
    from huggingface_hub import model_info
    info=model_info(model_id,revision=revision)
    resolved=info.sha
    # Resolve immutable model commit before loading; never use drifting defaults.
    encoder=SentenceTransformerEncoder(model_id, revision=resolved)
    manifest=json.loads((root/"capture_manifest.json").read_text(encoding="utf-8"))
    corpora={}
    all_subsections=[]
    for src in manifest["sources"]:
        sid=src["source_id"]
        blob=(root/src["snapshot_file"]).read_bytes()
        digest=sha256(blob).hexdigest()
        if digest!=src["normalized_text_sha256"]:
            raise ValueError(f"Snapshot mismatch: {sid}")
        text=blob.decode("utf-8")
        chunks=chunk_legal_text(text,sid)
        verify_chunks(text,chunks)
        subsections=[c for c in chunks if c.subsection is not None]
        all_subsections.extend(subsections)
        corpora[sid]={"chunks":chunks,"text":text,"source_sha256":digest}
    hybrid=HybridRetriever(all_subsections,encoder=encoder,encoder_id=f"{model_id}@{resolved}")
    lexical=BM25LegalRetriever(all_subsections)
    records=[]
    for sid,provision,subsection,query in PROBES:
        expected=f"{sid}:{provision}:{subsection}"
        if expected not in {c.chunk_id for c in corpora[sid]["chunks"]}:
            raise ValueError(f"Missing expected source chunk: {expected}")
        bm=[h.chunk.chunk_id for h in lexical.search(query,top_k,source_id=sid)]
        emb=[h.chunk.chunk_id for h in hybrid.semantic_search(query,top_k,source_id=sid)]
        fused=[h.chunk.chunk_id for h in hybrid.search(query,top_k,source_id=sid)]
        edges=build_reference_graph(corpora[sid]["chunks"],
            manually_flagged={("17.9.571.11","17.9.571.13"):"suspected source cross-reference mismatch"})
        # Use lexical baseline for structure-aware context-expansion smoke diagnostics.
        structure=assemble_evidence(query,sid,lexical,corpora[sid]["chunks"],edges,top_k=top_k,
                                    max_chunks=24)
        records.append({
            "source_id":sid,"query":query,"expected_provision_chunk_id_AI_PROVISION_SEED":expected,
            "BM25":{"top_ids":bm,"contains_seed":expected in bm},
            "embedding_only":{"top_ids":emb,"contains_seed":expected in emb},
            "hybrid_rrf":{"top_ids":fused,"contains_seed":expected in fused},
            "structure_bm25":{"retrieval_ids":list(structure.retrieval_hits),
               "evidence_bundle_ids":[c.chunk_id for c in structure.evidence_chunks],
               "contains_seed":expected in {c.chunk_id for c in structure.evidence_chunks},
               "ambiguities":list(structure.source_ambiguities)},
        })
    report={
        "research_status":"DIAGNOSTIC_AI_SEEDED_NO_HUMAN_GOLD",
        "formal_retrieval_accuracy_reported":False,
        "gold_count":0,"llm_calls":0,"pypsa_solver_called":False,
        "model_id":model_id,"model_revision":resolved,
        "retrieval_parameters":{"top_k":top_k,"rrf_k":hybrid.rrf_k},
        "source_sha256s":{sid:c["source_sha256"] for sid,c in corpora.items()},
        "subsection_count":len(all_subsections),
        "probes":records
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "model_id":model_id,"model_revision":resolved,
        "subsection_count":len(all_subsections),"probe_count":len(records),
        "diagnostic_probe_seed_hits_not_formal_accuracy":{
            mode:sum(bool(r[mode]["contains_seed"]) for r in records)
            for mode in ["BM25","embedding_only","hybrid_rrf","structure_bm25"]},
        "output":str(output)},indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-root",type=Path,default=Path("outputs/official_corpus"))
    p.add_argument("--output",type=Path,default=Path("outputs/official_corpus/hybrid_rag_diagnostic.json"))
    p.add_argument("--model-id",default="sentence-transformers/all-MiniLM-L6-v2")
    p.add_argument("--revision",default=None)
    p.add_argument("--top-k",type=int,default=5)
    a=p.parse_args()
    make_report(a.source_root,a.output,a.model_id,a.revision,a.top_k)
