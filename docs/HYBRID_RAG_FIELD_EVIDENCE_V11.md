# Hybrid Legal RAG v1.1 — fusion and field-level provenance

**2026-11-28.** Deterministic source-anchored baseline extended with optional **real semantic embeddings** through an explicit `SentenceTransformerEncoder(model_id)` interface, Reciprocal Rank Fusion (RRF) of BM25 and semantic rankings, and mandatory exact-source quotation checks. The code never silently replaces missing vector embeddings with purported semantic results.

## New components

- [hybrid_retrieval.py](../src/energy_policy_llm/hybrid_retrieval.py): BM25 plus optional semantic cosine ranking. The encoder is an injected callable; its exact `encoder_id` must be recorded. When no encoder is supplied, this is **BM25-only**. RRF scores are fusion ranks, **not** confidence/probabilities.
- [field_evidence.py](../src/energy_policy_llm/field_evidence.py): field-level quote, exact start/end offsets, retriever chunk membership and frozen UTF-8 SHA-256 checks. A field with matching text returns `EVIDENCE_MATCHED_NOT_ADJUDICATED`; it **does not** establish semantic truth.
- [test_hybrid_field_evidence.py](../tests/test_hybrid_field_evidence.py): lexical-only, mock-vector RRF, embedding provenance guard and failed-evidence checks. **Mock vectors do not constitute real semantic retrieval experiments.**

### Optional genuine local semantic encoder

Requires an external download/cache of the exact selected model and locally installed `sentence-transformers` (not included in core package dependencies). Example:

```python
from energy_policy_llm.hybrid_retrieval import HybridRetriever, SentenceTransformerEncoder
from energy_policy_llm.legal_chunker import chunk_legal_text
text = open("NM_COOP_2025.txt", encoding="utf-8").read()
chunks = [c for c in chunk_legal_text(text, "NM_COOP_2025") if c.subsection]
model_id = "sentence-transformers/all-MiniLM-L6-v2"  # example; pin commit/revision for study
retriever = HybridRetriever(chunks, encoder=SentenceTransformerEncoder(model_id), encoder_id=model_id)
hits = retriever.search("2030 renewable target retail sales", k=5, source_id="NM_COOP_2025")
```

The example above is **an illustration, not a record of a completed model download or inference**. For formal comparisons, pin model repository revision, text normalization, batching, run environment and index/source version. Never leak withheld test text through training-time examples.

## Formal experiment contract

1. Freeze the official legal snapshots, retrieved evidence chunks and policy-family train/dev/test splits.
2. Record lexical baseline, actual semantic model ID+revision, RRF parameters and top-k budgets.
3. Compare BM25, embeddings-only, hybrid RRF, structure-aware expansion, and oracle evidence. Hold LLM and token budgets fixed.
4. Evaluate `evidence_recall@k` and dependency closure against **human-adjudicated** relevant clause sets. Use the new field evidence gate to reject quoted text outside retrieved sources, but also evaluate whether the cited span truly supports the predicted field.
5. Couple extraction to PolicyIR and Compiler v2; separately track legal misinterpretation, invalid model mapping and PyPSA cost/feasibility errors.

**No human Gold, true semantic benchmark, LLM evaluation or legal-equivalent PyPSA run is claimed.** The next step is to run a pinned encoder on the frozen official chunks and inspect whether BM25+embedding+graph improves dependency closure over lexical-only.
