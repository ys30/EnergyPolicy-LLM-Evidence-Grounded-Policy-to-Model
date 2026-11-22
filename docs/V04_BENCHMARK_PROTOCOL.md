# v0.4 Benchmark harness (2026-11-22)

**Implemented:** offline scoring, group leakage protection, unsafe acceptance count, abstention and exact field-match metrics, small synthetic fixture and automated tests.

**Not implemented:** actual model API calls, human-adjudicated labels, production retrieval pipeline, primary-document snapshots, real power-system experiments. The synthetic fixture demonstrates evaluator behavior only, not model accuracy. The fixture is NOT policy law.

## Data split and leakage
- One policy instrument (including all amendments, sections, paraphrases and versions) must remain in one split.
- For out-of-state tests, hold out a complete jurisdiction. The current helper enforces instrument grouping; experiment configuration must enforce jurisdiction holdout.
- Human gold requires exact evidence span + two independent reviewers and adjudication according to V03 protocol.

## Minimal prediction contract
Each model writes JSON with `case_id`, `predicted_fields` keys:
`target_fraction`, `target_date` (ISO date), `obligated_entities`,
`numerator`, `denominator`, and `predicted_decision` among
`ABSTAIN`, `SCENARIO_PROXY`, `LEGAL_CONSTRAINT`.
Future versions add evidence offsets, resource eligibility, credit accounting and exceptions.

## Evaluation rules
- Each field uses strict canonical exact matching. Incomplete predictions count wrong.
- Report macro aggregate over instruments, stratified by state, version and policy subtype (future code).
- Unsafe acceptance numerator = legal constraint predicted where reference decision is not LEGAL_CONSTRAINT; rate divided by ALL evaluated cases. Also separately report at-risk subset rate in manuscript.
- Abstention rate is predicted ABSTAIN / total; assess coverage against usefulness and safety.
- A model cannot promote its own annotations into gold.
- Metric names are diagnostic; reference status depends on independent human review, not adjudication by the tested LLM.

## Run
```bash
python -m pip install -e .
python scripts/evaluate_fixture.py
python -m unittest discover -s tests -v
```

## Next scientifically necessary step
Create verified source snapshots, run human annotation pilot, freeze policy instrument/state holdouts, then execute true LLM/RAG methods. Do not publish fixture scores as research findings.
