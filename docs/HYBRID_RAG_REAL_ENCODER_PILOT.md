# Real Hybrid RAG benchmark harness — official NM statutes (2026-11-28)

**Purpose:** Execute a genuine, version-resolved sentence-transformer model against frozen legal source chunks, comparing retrieval ranking from BM25, embedding-only, RRF hybrid, and lexical retrieval expanded by literal statutory cross references. This is a **diagnostic harness, not a formally adjudicated accuracy benchmark**.

## Frozen-source experiment contract

- **Inputs:** the same official `NM_COOP_2025` and `NM_IOU_2023` captured by `scripts/capture_corpus_ci.py`; checked against source SHA-256 and exact frozen subsection bounds before model inference.
- **Encoder:** `sentence-transformers/all-MiniLM-L6-v2` is a lightweight English pilot, loaded at an immutable Hugging Face model commit resolved by `model_info`. The report stores both name and commit. This is not a domain-specific legal encoder.
- **Retrieval arms:** (1) BM25, (2) embedding-only cosine, (3) hybrid Reciprocal Rank Fusion with `rrf_k=60`, (4) BM25 + original-source reference-graph evidence bundling.
- **Probe set:** five provision-seeded NM cooperative queries: 8(B), 8(D), 9(A), 10(A), 11(D). These are authored smoke checks with known subsection IDs, **not human relevance labels or representative held-out benchmark questions**.
- **Output:** `outputs/official_corpus/hybrid_rag_diagnostic.json` records per-arm ranked chunk IDs, source SHA hashes, resolved encoder commit and probe outcomes. Results are explicitly named `diagnostic_probe_seed_hits_not_formal_accuracy`; no `gold` field is promoted.
- **Cross references:** 11(D) suspected references into .13 are flagged in the source graph and never silently rewritten.

## Reproduction

[GitHub Actions workflow](../.github/workflows/hybrid-rag-real-embeddings.yml) installs project, sentence-transformers and Hugging Face Hub, then captures the official documents, audits source bounds, runs the encoder and uploads metadata. The workflow requires access to the official New Mexico rules and the public Hugging Face model; a network/model download failure is an environmental or data-access failure, not proof of retrieval performance.

```bash
python -m pip install -e .
python -m pip install 'sentence-transformers>=3.4,<6' 'huggingface_hub>=0.28,<2'
python scripts/capture_corpus_ci.py
python scripts/audit_official_rag.py
python scripts/run_official_hybrid_rag.py --top-k 5
```

## Interpretation limitations and next gate

With only five AI-created, provision-anchored probes, the per-mode matched-section count is a *smoke diagnostic*, not a retrieval generalization result. Structural expansion can add parent chapter context and therefore uses a larger evidence budget than the other top-k ranked lists; it must not be compared as equivalent to a top-k retrieval ranking without a common token budget. Sentence transformers may truncate long statutory subsections; track chunk lengths, revise segmentation and validate exceptions before claiming recall gains. Retrieval is not model compilation, so absent actual field-extraction predictions and human Gold, no claim of improved semantic accuracy or legal compliance can be made.

For a scientific evaluation: (i) freeze group-level train/dev/test splits by statute/policy family, (ii) obtain independent human-adjudicated *relevant evidence sets*, (iii) match retrieval token budgets, (iv) record extraction-model IDs/prompt hashes and (v) report dependency completeness, selective risk, unsupported citation/field rates, and downstream compiler/PyPSA error propagation.
