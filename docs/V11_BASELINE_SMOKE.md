# v1.1 — An executed conservative text-baseline smoke test

**2026-11-23** — official rule locations verified, but no full frozen official source snapshot. The source-inspired sentences in the fixture are **researcher paraphrases** and are NOT gold annotations, quotations, or randomized legal clauses. No LLM was run.

Official sources:
- https://www.srca.nm.gov/parts/title17/17.009.0572.html (17.9.572.2)
- https://www.srca.nm.gov/wp-content/uploads/2025/06/17.9.571.html (17.9.571.8(A), 17.9.571.8(C))

## Local reproduction
```bash
python -m pip install -e .
python scripts/run_paraphrase_baseline.py
python -m unittest discover -s tests -v
```
The regex baseline extracts numeric percentages and 4-digit years, detects explicit retail-sales denominator mentions, and always abstains from legal-compliance modeling. It intentionally does **not** infer word-numbers (e.g. *fifty percent*), entity obligations, REC mechanics, or legal exceptions. On the three hand-written paraphrases, the 2030 year and retail-sales token are detected in the target case, but its spelled-out fraction is unresolved. The scope and REC cases do not yield numerical targets.

Five focused tests passed in a local standalone copy. Full repository CI status must still be checked independently; these are code tests, not real-world accuracy measures.

## Critical next empirical steps
1. Freeze full official text in a versioned, hash-checked corpus with source permissions reviewed.
2. Have two independent humans annotate and adjudicate real clauses.
3. Run identical test cases through regex, direct LLM, evidence-RAG LLM, and grounded+validator.
4. Only then calculate accuracy, unsafe acceptance, and error propagation to independently pinned PyPSA scenarios.
