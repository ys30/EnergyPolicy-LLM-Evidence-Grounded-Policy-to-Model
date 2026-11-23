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

## v0.3 — Auditable annotation pilot (2026-11-22)

New: [annotation integrity gate](src/energy_policy_llm/annotations.py), [seven tests](tests/test_annotations.py), [offline candidate queue](scripts/create_annotation_queue.py) and [review protocol](docs/V03_ANNOTATION_PROTOCOL.md). Candidate policy descriptions are **not** gold labels. Exact-source snapshots and double human adjudication are required before benchmark metrics. No LLM or empirical PyPSA benchmark has yet been run.

Run `python scripts/create_annotation_queue.py` to generate a local worklist (3 rows, 0 gold labels); the generated CSV is intentionally ignored under `outputs/`.

## v0.4 — Offline benchmark evaluator (2026-11-22)

Added a [group-aware evaluator](src/energy_policy_llm/benchmark.py), [synthetic evaluation fixture](data/fixtures/synthetic_benchmark_v04.json), [evaluation smoke test](scripts/evaluate_fixture.py), [eight tests](tests/test_benchmark.py), and [protocol](docs/V04_BENCHMARK_PROTOCOL.md). **All fixture data are synthetic; no real LLM accuracy or legal-compliance metric is claimed.** The evaluation helper refuses unadjudicated records in empirical mode and blocks policy-instrument train/test leakage. Run `python scripts/evaluate_fixture.py` after installing the project. GitHub Actions checks were configured; their results require separate confirmation.

## v0.5 — Official source capture and NM legal review queue (2026-11-22)

Added a [source capture utility](src/energy_policy_llm/sources.py), [explicit capture command](scripts/capture_official_sources.py), [source validation tests](tests/test_sources.py), [12 targeted New Mexico review tasks](data/policies/review_tasks_v05.json) and [source capture protocol](docs/V05_SOURCE_CAPTURE.md). Source snapshots are written to ignored local outputs and never automatically promoted to gold labels. **No actual source downloads, human adjudications or LLM experiments are claimed for this release.**

Example: `python scripts/capture_official_sources.py --case NM_RPS_2030_PUBLIC_UTILITIES`. Source capturing requires network access and may be blocked by publisher protections. CI does not crawl government websites.
