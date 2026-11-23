# v0.7 — Frozen-source candidate extraction

**Implemented and unit-tested on synthetic text.** Neither a legal gold set nor a real LLM benchmark. Government source locations were checked on 2026-11-22, but complete official text could not be downloaded in the authoring container.

## Official records
- NM investor-owned electric utilities: https://www.srca.nm.gov/parts/title17/17.009.0572.html (rule effective 2023-02-28)
- NM rural electric cooperatives: https://www.srca.nm.gov/wp-content/uploads/2025/06/17.9.571.html (rule effective 2025-06-24)
- Material distinctions: plan-year retail sales definition in 17.9.572.7(P)(2); cooperative RPS target, REC retirement and generation/transmission supplier responsibility in 17.9.571.8.

## Run
1. Capture a permitted primary text snapshot via `scripts/capture_official_sources.py` (requires live network), or save a source-preserving UTF-8 text manually under `outputs/source_snapshots/`.
2. Review formatting and section order: the extractor expects identifiers such as `17.9.571.8` at line starts. It deliberately can miss sections and extract irrelevant text.
3. Run:

```bash
python -m pip install -e .
python scripts/extract_local_candidates.py --snapshot outputs/source_snapshots/NM_RPS_2030_DISTRIBUTION_COOPS.txt --source-id NM_COOP_2025 --source-version 2025-06-24 --output outputs/candidates/NM_COOP_2025.json
python -m unittest discover -s tests -v
```

Each candidate includes a snapshot SHA-256, source version, provision, and exact 0-indexed character offsets. Candidates must stay `candidate_unreviewed` until two human reviewers independently annotate and an adjudicator resolves differences. **Zero adjudicated gold labels** exist at this stage.

No legal compliance calculation or empirical PyPSA claim follows from these candidates. The tool is a provenance-preserving worklist generator only.
