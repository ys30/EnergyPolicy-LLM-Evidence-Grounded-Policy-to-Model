# Policy-to-PyPSA compiler v2 — capability-gated synthetic prototype

**Status:** Code prototype only. **No PyPSA execution, actual LLM model call, independently adjudicated legal annotation, or valid compliance claim.** Gold count remains 0.

## New modules

- `model_profile.py`: immutable, explicit model entity/year/capability profile. The included profiles are **synthetic**, `model_kind=synthetic_not_pypsa`.
- `policy_ir.py`: typed intermediate representation with one primary legal semantic type, obligor, year/fraction, exact-source SHA and conditional conjuncts.
- `compiler_v2.py`: semantic safety gate that reports required data, missing data and decision (`ABSTAIN`, `SCENARIO_PROXY`, `NOT_DIRECTLY_EXECUTABLE`, or `PLAN_ONLY`).
- `scripts/demo_compiler_v2.py`: fully synthetic demonstration requiring neither the frozen statute nor network access.

Run:

```bash
python -m pip install -e .
python -m unittest tests.test_policy_to_model_v2 -v
python scripts/demo_compiler_v2.py
```

## Why the safety rules matter

The NMAC RPS target counts eligible renewable energy against **New Mexico retail electricity sales**, with REC compliance and obligated-entity allocation. A local `renewable_generation / local_generation` share is not equivalent. The compiler therefore:

1. Refuses unverified legal evidence, unresolved source ambiguities and nonexistent entity/year mappings.
2. Refuses missing REC retirement, retail sales, eligible technology mapping or other dependencies in strict mode.
3. Permits `SCENARIO_PROXY` only with **explicit opt-in**; never claims legal equivalence.
4. Treats definitions, reporting, accounting and cost exceptions as **supporting semantics** rather than meaningless errors.
5. Refuses conditional targets until trigger conditions and their legal meaning have been independently resolved.
6. Emits only an **expression plan**, not executed PyPSA constraints, even if both `human_adjudicated=True` and `reviewed_legal_mapping=True` are explicitly supplied.

The flags in the type definitions are caller-supplied, **not** independent cryptographic proof of adjudication. A production compiler must use the existing provenance gate and adjudicated records before enabling a strict mode.

## Results to expect from the synthetic script

| Mode | Expected outcome | Explanation |
|---|---|---|
| Minimal data, strict | `ABSTAIN` | No legal retail sales or REC capabilities |
| Minimal data, allow proxy | `SCENARIO_PROXY` | Illustration using local generation only; not legal compliance |
| All synthetic capabilities, no adjudication | `ABSTAIN` | Data capability alone does not prove legal interpretation |

## Before a real PyPSA adapter

Define source-grounded and adjudicated legal input, utility-to-bus/load ownership, compliant annual retail sales, REC issuances/transfers/retirements and certificate eligibility, conditional zero-carbon pathways, CPI-adjusted cost rules, and proof that the optimization variables correspond to the intended legal compliance accounting. Then implement an optional PyPSA + linopy adapter with a separate REC-compliance layer and frozen deterministic tests. No PyPSA solver has been invoked by this work.
