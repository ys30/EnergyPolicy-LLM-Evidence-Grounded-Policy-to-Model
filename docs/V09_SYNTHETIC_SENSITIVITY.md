# v0.9: First executed synthetic sensitivity demonstration

## Scope

This is a mathematical smoke test, NOT a policy impact study, live LLM benchmark, legal compliance engine, or PyPSA simulation.

The existing three-generator toy linear program uses load 100 energy units, solar/wind capacities 45 each, and artificial costs [solar=2, wind=1.5, gas=1] per unit. It treats a renewable generation ratio as a modeling proxy.

## Executed local results (2026-11-22)

| Assumed condition | Synthetic solution cost | Strict semantic decision |
| --- | ---: | --- |
| Unconstrained (0%) | 100.0 | baseline |
| Explicit physical generation share = 60% | 137.5 | RUN |
| Retail-sales RPS mistakenly mapped to generation share = 60% | 137.5 | ABSTAIN |
| Retail-sales RPS mistakenly mapped to generation share = 50% | 127.5 | ABSTAIN |

The 37.5 and 27.5 increases are *arbitrary cost units*, not economic forecasts. This only demonstrates how a semantically wrong constraint can produce a plausible optimizer output.

## Run

```bash
python -m pip install -e .
python -m energy_policy_llm.sensitivity
python -m unittest discover -s tests -v
```

Seven additional synthetic tests were executed locally in a standalone implementation (7/7 passed); repository integration is provided here, but GitHub CI results must be checked independently.

## Scientific limits

The current strict flag uses an explicitly provided denominator mismatch; it is not automatically extracted by an LLM and is not proof of true statute compliance. No human-reviewed real law excerpts exist in the benchmark, and no PyPSA case is run. Next step: paired expert/LLM annotations of source-frozen legal clauses, followed by a controlled Policy-to-Model translation comparison.
