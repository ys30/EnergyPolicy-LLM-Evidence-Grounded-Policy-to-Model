# v0.6: Official-source section anchors — not gold annotations

As of 2026-11-22, official state rule pages were read and a set of **14 source-section locations** across **two primary documents** was prepared. These are independently traceable section pointers and editorial paraphrases, **not verbatim legal excerpts**, exact-text offsets, independent annotator agreement, a completed human gold set, or LLM performance results.

The source pages are:
1. New Mexico 17.9.572 (effective 2023-02-28): https://www.srca.nm.gov/parts/title17/17.009.0572.html
2. New Mexico 17.9.571 (effective 2025-06-24): https://www.srca.nm.gov/wp-content/uploads/2025/06/17.9.571.html

### What these anchors establish

- The 2030 target for each category is 50%, but regulatory subjects differ.
- Investor-owned public utilities exclude rural co-ops and municipalities for this rule.
- Plan-year retail sales differ from local electric generation and require attention to adjustment definitions.
- RECs, delivery/assignment, and qualifying-resource rules matter.
- Distribution co-ops are distinct from generation/transmission co-ops, which have specified energy-supply responsibilities.
- Exemptions / cost thresholds must not be lost when compiling optimization constraints.

### Offline reproducibility

```bash
python -m pip install -e .
python scripts/audit_source_anchors.py
python -m unittest discover -s tests -v
```

The audit script checks internal registry integrity; it does **not** verify the internet sources in real time. Full source download was not available in the execution environment used for authoring this version. `scripts/capture_official_sources.py` remains a user-executable network-based capture command. No complete frozen source snapshots have been committed.

### Critical next milestone

Finish 10–15 real source-span annotations *against frozen primary text*, then obtain independent double review and adjudication. Afterwards run genuine LLM and retrieval baselines on a held-out test corpus. Do not report current catalog counts as accuracy metrics or use legal constraints in PyPSA without independently verified accounting assumptions.
