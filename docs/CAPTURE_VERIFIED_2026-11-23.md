# Official New Mexico policy corpus — verified capture

Capture run: https://github.com/ys30/EnergyPolicy-LLM-Evidence-Grounded-Policy-to-Model/actions/runs/45282578108
Date (UTC): 2026-11-23T22:45
Result: **SUCCESS**; both download and exact-byte candidate verification passed.

| Source ID | Source version label | Normalized characters | Candidates | SHA-256 (normalized snapshot) |
|---|---|---:|---:|---|
| NM_IOU_2023 | 2023-02-28 | 51254 | 200 (limit reached) | 56a166bfe2114513c9f4e79d2f330d5b700af64d913368637cd7b692894e0274 |
| NM_COOP_2025 | 2025-06-24 | 25245 | 13 | 6900b1e110734e66a29f66cd915a88d3349fc36a72331a031eeac7b23e1d6039 |

Source URLs:
- https://www.srca.nm.gov/parts/title17/17.009.0572.html
- https://www.srca.nm.gov/wp-content/uploads/2025/06/17.9.571.html

Evidence artifact: [NM-official-policy-corpus-unreviewed](https://github.com/ys30/EnergyPolicy-LLM-Evidence-Grounded-Policy-to-Model/actions/runs/45282578108/artifacts/14869252560), retained until 2026-11-30 22:45 UTC.

Original reported failure: https://github.com/ys30/EnergyPolicy-LLM-Evidence-Grounded-Policy-to-Model/actions/runs/45278375520.
Root observable error: `ValueError: Hash mismatch or forbidden status promotion` during `Validate manifest and offsets`, after successful source capture.
Fix: canonicalize CRLF/CR newlines to LF before hashing and candidate extraction, serialize snapshots as UTF-8 bytes and check the saved bytes/hash in CI. The new run passed.

**IMPORTANT**: 213 outputs are unreviewed candidate spans, NOT 213 independent laws or human-annotated gold records. The 200 IOU candidates are truncated at the extractor limit. No LLM model inference or PyPSA run has yet been performed. Rule version labels are registry metadata and still need legal-version review. Snapshots are an unreviewed original-text archive, not a license to redistribute the complete texts publicly.
