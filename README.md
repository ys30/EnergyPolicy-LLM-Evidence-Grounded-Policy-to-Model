# EnergyPolicy-LLM: Evidence-grounded Policy-to-Model

**Status (2026-11-22):** research starter / proof of concept, **not** validated legal compliance or a published study.

## Research question
Can clean-energy policy language be converted into auditable, executable energy-system scenarios without silently changing its legal meaning?

Three evaluation layers: (1) evidence-grounded extraction, (2) semantic compatibility and compiler abstention, (3) downstream quantitative sensitivity to translation errors.

## What runs now
- Versioned policy case registry (`data/policies/cases.json`) with source URLs and independent review status.
- Deterministic baseline extractor for clearly stated percentage/year statements; intentionally limited.
- Strict compiler that **rejects** a retail-sales / certificate-based compliance obligation when asked to map it to a generation-share constraint.
- A separately flagged **illustrative proxy** mode, run with a synthetic 3-technology 1-year linear program (SciPy), to show error propagation. This is NOT a compliance model or PyPSA simulation.
- Python unit tests for the core semantic safety behavior.

## Run
```bash
python -m pip install -e '.[test]'
python -m unittest discover -s tests -v
energy-policy-demo --mode strict
energy-policy-demo --mode proxy

# Offline alternative (when scipy is already installed):
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m energy_policy_llm.cli --mode strict
PYTHONPATH=src python -m energy_policy_llm.cli --mode proxy
```

The `strict` command intentionally reports `ABSTAIN` for both CA and NM (retail sales are not the same as generation). `proxy` reports an artificial cost comparison, explicitly labeled a scenario proxy, not a legally faithful estimate.

## Scope / caveats
- **No LLM API or credentials required** yet. The baseline is a deterministic extractor; an actual LLM/RAG experiment is a planned workstream, not a completed result.
- Do not interpret example summaries as authoritative legal text. Legal targets require line-level primary document confirmation and definition of eligible resources, obligated entities, credit accounting, and compliance periods.
- No empirical generation or load data yet. Synthetic demonstration is non-publishable and not a PyPSA computation.
- Cross-model integration to a *new, frozen* PyPSA test model is a next step; avoid changing existing PyPSA research repos.

## Repository map
- `src/energy_policy_llm/schema.py` — typed, auditable policy records
- `src/energy_policy_llm/extract.py` — simple baseline extractor
- `src/energy_policy_llm/compiler.py` — compatibility checks and abstention
- `src/energy_policy_llm/toy_lp.py` — synthetic optimization sensitivity demo
- `src/energy_policy_llm/cli.py` — entry point
- `data/policies/cases.json` — initial case registry
- `docs/RESEARCH_PLAN.md` — questions, benchmarks, evaluation and milestones
- `docs/SOURCE_AUDIT.md` — primary links and limitations

## Citation
Sources are URLs in case registry and SOURCE_AUDIT. A complete clause-level annotated corpus is not yet created. Record repository commit hashes, document retrieval dates, legal versions, and annotator decisions when extending this corpus.

## v0.2 — Evidence schema & semantic audit (2026-11-22)

The current repository includes [three provisional regulatory cases](data/policies/evidence_registry_v02.json), a typed [evidence-aware compiler](src/energy_policy_llm/evidence.py), [nine additional unit tests](tests/test_evidence.py), an [offline registry validator](scripts/validate_evidence_registry.py), a [pre-annotation research protocol](docs/V02_PROTOCOL.md), and [GitHub Actions CI](.github/workflows/ci.yml).

The separate New Mexico distribution-cooperative case prevents treating all obligated entities as one legal class. All records remain `human_review_pending`; no exact legal excerpts or gold-standard annotation were fabricated. The evidence compiler rejects unsupported retail-sales → local-generation equivalence, except explicitly labeled nonlegal scenario proxies.

Run:
```bash
python -m pip install -e .
python scripts/validate_evidence_registry.py
python -m unittest discover -s tests -v
```

**Verification:** new files were committed to GitHub. CI was configured but its passing status has not yet been independently confirmed. This repository has no current LLM benchmark or empirical PyPSA run.
