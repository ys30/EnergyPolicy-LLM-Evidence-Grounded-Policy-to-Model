# v1.0 — Provenance-gated held-out evaluation

**Date:** 2026-11-22. This release provides an executable evaluation entry point, but **no validated legal gold corpus, LLM calls, or PyPSA empirical results**.

## Reproducible synthetic demonstration

```bash
python -m pip install -e .
python scripts/run_gated_evaluation.py --dataset data/fixtures/synthetic_gated_v10.json --synthetic-demo
python -m unittest discover -s tests -v
```

The synthetic test split includes a deliberate mismatch: the gold policy denominator is retail sales, but the naive model prediction substitutes local generation and requests a LEGAL_CONSTRAINT. The evaluator must flag exactly one unsafe acceptance. This is a pipeline test, **not an observed LLM error rate**.

## Empirical contract (future)

Without `--synthetic-demo`, the evaluator requires `dataset_kind=human_adjudicated`, an entry for each gold record containing `provenance` fields accepted by `GoldProvenance`, a `--snapshots` JSON object mapping source SHA-256 hashes to exact frozen document text, separate prediction objects matched by case_id, and a declared fully held-out test jurisdiction. Hashes, source character offsets, quotation, annotators, instrument grouping and jurisdiction holdout must validate. The gate checks metadata consistency, **not** the real identity of annotators or the legal truth of their decisions. Store copyrighted full documents outside the public repo unless redistribution is permitted.

## Reading outputs
The only published numerical result here is for synthetic input: one test case, one intentionally unsafe decision, denominator exact match zero. No model comparisons or policy outcomes are claimed. Real-source pages may be read online, but local full-document download remains blocked. Source locations in v0.6/v0.8 are not gold annotations.

## Limitations and next work
- Obtain reproducible source snapshots and evidence offsets
- Independently adjudicate the first 10–15 clauses; extend to 50+
- Run named LLM variants and an evidence-controlled baseline against exactly the same test set
- Evaluate uncertainty and clustered interval estimates over policy instruments
- Add physical and accounting-aware PyPSA constraints only after legal semantics are established
