# Evidence-grounded RAG → Policy IR bridge v1

**Status 2026-11-28:** implemented a deterministic validation boundary; no LLM generated predictions or human adjudications have been performed. Human Gold: **0**.

## Actual semantic-model diagnostic (verified successful)

[GitHub Actions run 46169063494](https://github.com/ys30/EnergyPolicy-LLM-Evidence-Grounded-Policy-to-Model/actions/runs/46169063494) succeeded: official source capture, RAG audit, actual `sentence-transformers/all-MiniLM-L6-v2` embeddings loaded at immutable revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`, retrieval diagnostics and artifact upload. Across **130 legal subsection chunks** and **five AI provision-seeded probes**, the intended subsection was present in the top-five BM25 results in 5/5 cases, embedding-only 5/5, hybrid RRF 5/5, and BM25 structure-expanded bundle 5/5. **These are target-informed smoke checks, not a held-out or human-Gold retrieval accuracy estimate.** None showed superiority on this tiny, easy probe set.

## New evidence-to-IR boundary

[`rag_policy_bridge.py`](../src/energy_policy_llm/rag_policy_bridge.py) defines `ProposedPolicyFields` + `DraftBridgeResult`. The caller supplies proposed structured fields and a separate exact quotation for every required label. Validation checks:

1. Provided frozen original text hashes to the same source as the retrieval `EvidenceBundle`.
2. `provision` actually appears in the retrieved bundle.
3. Every required field has a citation, unique field names, and each exact quotation sits within a returned source chunk (correct end-exclusive offsets).
4. The controlled Codebook semantic type and PolicyIR metric are recognized; condition targets require explicit `ALL` conditions in PolicyIR.
5. Unresolved source references and flagged original-law ambiguities force `ABSTAIN`.
6. Even passing an exact quote returns **`EVIDENCE_MATCHED_AI_DRAFT_NEEDS_SEMANTIC_REVIEW`** and creates a PolicyIR with **`evidence_verified=False` and `human_adjudicated=False`**. Therefore the strict compiler v2 cannot mistake this result for verified legal provenance.

The test fixture intentionally cites `New Mexico` as evidence for an inferred `distribution_cooperative` entity; the quote is *verifiably present* but **not sufficient semantic support for the specific entity claim**. This illustrates the important difference between *exact citation matching* and *legal entailment*.

**What this code does not do:** query an LLM, decide whether quoted text entails a numeric / legal field, cross-check all semantically necessary subsections, or certify an actual legal compliance interpretation. A model could quote a valid but irrelevant phrase; an additional semantic entailment gate, calibrated human review, and provenance-adjudication workflow remain required.

## Reproduce

```bash
python -m pip install -e .
python -m unittest tests.test_rag_policy_bridge -v
python -m unittest discover -s tests -v
```

## Recommended next step

Build **field-level claim entailment and contradiction tests** using manually adjudicated text spans (e.g. eligible REC vs generated MWh; 80% conditional targets vs unconditional claims; G&T responsibility; 11(D) ambiguous references). Compare Direct LLM, BM25, true Embedding-only, RRF and Structure-Aware evidence using frozen policy-family splits; include oracle retrieved contexts. Only then connect *adjudicated* PolicyIR to safe policy compiler decisions and measure downstream PyPSA cost and feasibility propagation.
