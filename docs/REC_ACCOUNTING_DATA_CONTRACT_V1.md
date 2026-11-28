# REC accounting + PyPSA output data contract v1

**Status:** Synthetic software prototype. No PyPSA or linopy solver executed; no legal-compliance opinion, no independently adjudicated gold, no actual LLM model benchmark. Separate statutory verification from simulation and compliance accounting.

## Modules and provenance

- [`rec_accounting.py`](../src/energy_policy_llm/rec_accounting.py): finite nonnegative retail sales by legal entity/year; unique REC certificate IDs; owner, vintage, eligible flag, retirement beneficiary and compliance year; a synthetic annual REC-balance calculation. The code rejects duplicate certificate identifiers and invalid values.
- [`pypsa_data_contract.py`](../src/energy_policy_llm/pypsa_data_contract.py): explicit legal-entity → model-profile → buses mapping with an independent `verified` flag. A model export provides annual local generation and eligible renewable generation, **not** retail sales nor retired RECs.
- [`demo_rec_accounting.py`](../scripts/demo_rec_accounting.py): toy illustration. Annual retail sales = 100 MWh, hypothetical target fraction = 0.50; eligible retired certificates = 45 MWh; **illustrative shortfall = 5 MWh**. Simulated local renewable generation is 70/100 MWh (**70%**) yet cannot close the independent REC compliance shortfall.

These example numbers are completely fabricated for testing and are not an estimate of an actual cooperative's legal obligation.

## Calculation contract

Given explicit legal entity/year pair and a separately justified target fraction, only unique eligible certificate batches **owned by that entity and retired by it for that same compliance year** count in the toy calculation. Do not infer eligibility from technology alone; `eligible=True` is an externally supplied test fixture flag, not legal verification. The optional `max_vintage_age_years` is deliberately a scenario assumption, not a verified rule for NM 17.9.571.11.

```text
illustrative_target_mwh = annual_retail_sales_mwh * target_fraction
illustrative_retired_mwh = sum(eligible, owned, retired, correct-period RECs)
illustrative_shortfall_mwh = max(0, target - retired)
```

The simplified accounting design does not model REC transfers, partial retirements, serial ranges, banking after lifecycle events, G&T distribution/cooperative responsibility or other legal exceptions. Do **not** label it a verified NM compliance engine.

## Proposed eventual PyPSA adapter

- Read solved PyPSA network data, time snapshot weights and annual generator dispatch by renewable eligibility and mapped buses.
- Preserve independently sourced retail sales by obligated cooperative; validate purchases/imports/exports and entity overlap.
- Match physically/generated REC issuance to **registered** certificate IDs and transfer/retirement lifecycle; prevent double use of the same serial.
- Implement legally adjudicated conditions (2050 RPS 80%, zero-carbon 100%, cost thresholds/exception logic), rather than hardcoding them into a dispatch share.
- Add `model_profile_id`, `pypsa_version`, dataset fingerprints, input timestamps, solution status and source versions to each run.

## Test

```bash
python -m pip install -e .
python -m unittest tests.test_rec_accounting_and_data_contract -v
python scripts/demo_rec_accounting.py
```

The numeric fixture is a **safety demonstration**: 70% renewable generation can coexist with a synthetic 5-MWh REC-based shortfall, illustrating why compiler v2 abstains without legal-to-model validation.
