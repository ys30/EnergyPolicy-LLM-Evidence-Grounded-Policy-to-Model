# Legal RAG v1 — frozen evidence, BM25, cross-reference graph, guarded evaluation

**2026-11-28 | Status:** deterministic retrieval prototype; **not** semantic-vector RAG, not an LLM experiment, not human adjudication. This release does not invoke embeddings or reranking. `gold_count=0`.

## Implemented

- [legal_chunker.py](../src/energy_policy_llm/legal_chunker.py): legal section and subsection chunks linked to the frozen UTF-8 text with exact Python character offsets (end-exclusive) and source SHA-256. Parent sections remain available even for chunks split by subsection.
- [retrievers.py](../src/energy_policy_llm/retrievers.py): repeatable zero-network BM25 baseline with explicit source filter, ranking and query scoring.
- [reference_graph.py](../src/energy_policy_llm/reference_graph.py): literal statutory cross-references with source-char positions and manual ambiguity flags. No unsupported correction of mistaken references.
- [evidence_bundle.py](../src/energy_policy_llm/evidence_bundle.py): query result snippets, parent section and explicit referenced sections, with an immutable source digest and an unreviewed-evidence status.
- [rag_evaluation.py](../src/energy_policy_llm/rag_evaluation.py): Recall@k and reference-set-completeness under explicitly supplied relevant chunks; formal evaluation refuses non-adjudicated references.
- [audit_official_rag.py](../scripts/audit_official_rag.py): smoke test against actual frozen NM IOU/cooperative snapshots **inside** the official-corpus GitHub Action, verifying section count, digest and source-span integrity, and uploading a `rag_audit.json` artifact.

## Retrieval protocol

Freeze a source snapshot; extract full sections and likely subsections, preserving exact spans. Index **subsections** as primary retrievable units and retain parent sections. BM25 first ranks, a graph expands only literal cross-references and records suspicious citations such as `17.9.571.11(D)` → `17.9.571.13(E)` as ambiguities, not auto-corrected statutes. The bundle includes original exact text and full provenance. A missing query match raises an explicit error instead of guessing.

The current `SUBSECTION` rule is a heuristic: not every lowercase/numbered nested paragraph is separately chunked and subsection layouts vary. A manual check of chunk segmentation and reference-link semantics is still required; the CI verifies offsets, not guaranteed legal obligation recall.

## Research questions and controlled arms

1. No retrieval (same LLM, no evidence).
2. Deterministic BM25 + LLM.
3. Hybrid lexical + embeddings + reranker (future).
4. Structure-aware cross-reference expansion + LLM (prototype graph now).
5. Same retrieval + evidence validator + safe compiler v2 (prototype interface, no model calls).

Include an **oracle evidence** diagnostic with human-verified complete dependencies to separate retrieval failure from model reasoning failure. Set document/policy-family split and evaluate held-out clauses only *after* real adjudicated gold exists. Preferred metrics: Recall@5/10, dependency-closure recall, exact-span citation support, legal field accuracy, conditional/exception preservation, unsafe acceptance (at risk) and PyPSA cost/feasibility error propagation.

## Precise limitations

- All RAG modules operate on frozen local text and are dependency-free; no vector database, embeddings, reranker or LLM API runs.
- A reference to an existing chapter can still be legally wrong. The graph is lexical, not authoritative legal interpretation.
- `confidence`/BM25 score is not a legal truth value. A retrieved citation does not constitute human Gold.
- Codebook v1.x is a proposed annotation specification. Neither compiler v2 nor the PyPSA synthetic experiment establishes NM statutory compliance.
- Normal lightweight CI exercises synthetic fixtures; the official corpus CI checks two actual frozen sources after download and uploads audit output when successful.

## Commands

```bash
python -m pip install -e .
python -m unittest tests.test_legal_rag_v1 tests.test_rag_evaluation_v1 -v
# Only after official corpus capture:
python scripts/audit_official_rag.py
```

**Follow-up:** add curated semantic embeddings and reciprocal rank fusion; implement a legal source-version and clause-dependency relevance gold set; measure evidence completeness before training a policy-extraction LLM.
