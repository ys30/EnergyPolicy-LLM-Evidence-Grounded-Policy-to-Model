# v1.2: First official excerpts and external LLM prediction handoff

**Status 2026-11-23**: Two short official excerpts, sourced from original state rule pages, are now in `data/policies/official_excerpt_review_v12.json`. They are not complete source snapshots and not gold annotations; no frozen text SHA-256 or character offsets were obtained.

Official pages:
- https://www.srca.nm.gov/wp-content/uploads/2025/06/17.9.571.html — 17.9.571.8(C)
- https://www.srca.nm.gov/parts/title17/17.009.0572.html — 17.9.572.2

## Reproducible model comparison contract

1. Freeze permitted source text locally using `scripts/capture_official_sources.py` or a manually preserved UTF-8 primary source, record SHA-256, date and version.
2. Prepare an evidence-bound model prompt: *Extract only explicitly supported legal fields; return null for ambiguity; do not equate retail sales and local generation; cite source ID, version, provision and character offsets. If compliance cannot be mapped legally to modeled generation, respond ABSTAIN.*
3. Run an externally chosen, pinned LLM (model ID/version, prompt, temperature, document access, invocation logs and cost) over the same held-out clauses. Do not embed credentials in GitHub.
4. Record one JSON object per line. Required keys: case_id, model_id, model_version, prompt_sha256, source_id, predicted_fields, predicted_decision. `predicted_fields` must contain target_fraction, target_date, obligated_entities, numerator, denominator. See `prediction_io.py`.
5. Run `python scripts/validate_llm_predictions.py --predictions PATH.jsonl` to validate format. This does **not** score model accuracy.
6. Separately create independent, adjudicated gold with `GoldProvenance` and run the gated held-out evaluation. Only then compare models.

**Current blocker**: Full official HTML cannot be retrieved by the execution container (DNS resolution). Web-accessible excerpts are short evidence pointers, not a complete corpus. There are currently zero independently reviewed gold clauses and zero executed actual LLM calls.
