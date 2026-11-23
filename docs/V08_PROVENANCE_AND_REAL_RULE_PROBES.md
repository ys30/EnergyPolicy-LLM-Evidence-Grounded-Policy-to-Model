# v0.8 — Hard evidence gate and real-law risk probes

Date: 2026-11-22

## Deliverables
- A fail-closed, source-hash-bound *pre-evaluation gate* in `src/energy_policy_llm/research_gate.py` requiring exact snapshot offsets, evidence text equality, two independently identified annotators, adjudicator, explicit source version, instrument-group split integrity, and a complete held-out jurisdiction.
- A small catalog of **10 manually paraphrased prompts** tied to New Mexico's official 2023/2025 rules, identifying denominator, entity, REC, eligibility and exception risks. These are **real-source-grounded review prompts, not gold labels or actual model outputs**.
- Synthetic unit tests for the gate's failure behavior and an offline metadata checker.

## Official source pages
- IOU: https://www.srca.nm.gov/parts/title17/17.009.0572.html
- Cooperatives: https://www.srca.nm.gov/wp-content/uploads/2025/06/17.9.571.html

## Data integrity caveats
The tool validates hashes and review metadata; it **cannot independently prove reviewer identities, adjudication quality or legal correctness**. The primary-source pages were inspected online, but complete frozen source snapshots were unavailable to the authoring container. Do not declare any gold data based only on these probes.

## Check
```bash
python -m pip install -e .
python scripts/check_real_rule_probes.py
python -m unittest discover -s tests -v
```

## Next research milestone
Capture and freeze at least 10 real excerpts with offsets; independently annotate and adjudicate; only then benchmark a specific named LLM against regex/RAG baselines. Track prompts, versions, temperature, exact sources and prediction JSON. Do not overstate software tests as empirical findings.
