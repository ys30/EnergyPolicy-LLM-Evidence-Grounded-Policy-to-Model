# v1.3 — Verified section-boundary repair and annotation-ready review queue

**Audit date:** 2026-11-24

## Verified CI runs

- Final official-corpus run: https://github.com/ys30/EnergyPolicy-LLM-Evidence-Grounded-Policy-to-Model/actions/runs/45443775485 — **success**
- Full repository tests: https://github.com/ys30/EnergyPolicy-LLM-Evidence-Grounded-Policy-to-Model/actions/runs/45443775436 — **success**
- Download the latest [unreviewed corpus + section-level review queues](https://github.com/ys30/EnergyPolicy-LLM-Evidence-Grounded-Policy-to-Model/actions/runs/45443775485/artifacts/14943748446). Expires 2026-12-01 17:01 UTC.

## Actual findings from frozen official law

| Official rule | Keyword-bearing candidate lines | Valid ordered sections | High-priority review sections |
|---|---:|---:|---:|
| NM 17.9.572 (IOU) | 276 | 22 | 4 |
| NM 17.9.571 (cooperatives) | 167 | 14 | 3 |
| **Combined** | **443** | **36** | **7** |

All extracted candidates retain source hashes and exact character offsets. The audit sees zero uncovered keyword-bearing lines inside identified sections and one outside-section document title in each source. **This is not proof of semantic completeness or clause-level recall.**

## Corrected section-boundary problem

A previously reported apparent repeat of section **17.9.572.16** was the phrase `Rule 17.9.572.16 NMAC only exempts...` split across HTML text lines. A premature occurrence of **17.9.572.19** was an inline cross-reference to annual reporting. The earlier section regex erroneously treated both `17.9.572.N NMAC...` as section headings. The corrected regex excludes NMAC continuation text. The verified IOU section list is 17.9.572.1 through 17.9.572.22, in order, without duplicates. The corrected cooperative heading list is 17.9.571.1 through 17.9.571.14, also in order. Earlier apparent .15 was not recognized as a heading under the corrected rule; its legal status remains subject to manual checking.

## Review queues generated

Two `*.review_queue.json` files now accompany the official corpus. Each section has:
- `source_sha256`, rule version label and section number;
- exact section character bounds and **full section text** (in the private-to-runner artifact, not committed in the repository);
- candidate span offsets, candidate count and `unreviewed_requires_independent_annotation` status;
- `high` priority for sections: 17.9.572.7, .10, .17, .19, and 17.9.571.7, .8, .10.

Those are research triage priorities, not legal validity determinations. Human review must verify headings, context, effective-date interpretation, REC accounting and exceptions.

## Research next steps

1. Download and retain the artifact before expiry.
2. Two independent reviewers annotate the seven priority sections, especially exact obligation granularity and source span evidence. Do not conflate candidate lines with distinct legal obligations.
3. Adjudicate differences and establish a frozen gold version.
4. Only then run controlled direct-LLM, evidence-RAG and validator arms, followed by realistic PyPSA error propagation.

No adjudicated gold or real LLM results have been produced in this run; `gold_count=0`.
