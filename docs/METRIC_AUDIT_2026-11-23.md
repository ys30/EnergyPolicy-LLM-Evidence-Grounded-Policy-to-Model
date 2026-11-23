# Benchmark safety metric audit — 2026-11-23

This is a correction to the evaluation code, not a real LLM experiment.

## Discovered denominator ambiguity
Previously unsafe acceptance was computed only as:
`unsafe_accept_count / all_test_cases`.
This can understate errors when the dataset contains many cases where a legal constraint *is* justified.

We now retain this legacy overall rate **and** additionally report:

- `at_risk_count`: number of gold cases whose reference compiler decision is **not** LEGAL_CONSTRAINT
- `unsafe_accept_rate_at_risk`: number of at-risk cases where the predicted decision is LEGAL_CONSTRAINT, divided by at-risk count
- `unsafe_accept_rate_at_risk = null` if the evaluation has no at-risk records (not 0)

## Synthetic illustrative check
With two synthetic cases, one should abstain but is wrongly accepted, and another is legally mappable and correctly accepted:
- overall unsafe-accept rate = 1 / 2 = 50%
- conditional at-risk unsafe-accept rate = 1 / 1 = 100%

These are **manufactured examples to verify the metric**, not LLM findings.

## Gold/synthetic separation
An evaluation in `allow_synthetic=True` mode now **only** accepts synthetic case labels.
The empirical mode **only** accepts adjudicated labels. The independent provenance gate still needs to be used for actual empirical evaluation; direct use of `benchmark.evaluate` alone cannot prove adjudication took place.

## Required experimental reporting
Report both unsafe rates with numerators and denominators, selective coverage, refusal rate, tool-call execution failure count, and interval estimates clustered by policy instrument. Do not compute an interval for a missing denominator. Never use synthetic results in the paper's empirical Results section.

## Reproduce
```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python scripts/run_gated_evaluation.py --dataset data/fixtures/synthetic_gated_v10.json --synthetic-demo
```
