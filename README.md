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

## v0.6 — Source-grounded legal section anchors (2026-11-22)

Read two official New Mexico administrative rules and registered [14 section-specific source anchors](data/policies/source_anchors_v06.json) with source URLs, effective dates, and **paraphrased** review notes. Added [registry integrity checks](src/energy_policy_llm/provenance.py), [five tests](tests/test_provenance.py), [an audit command](scripts/audit_source_anchors.py), and [documentation](docs/V06_REAL_SOURCE_ANCHORS.md). Run `python scripts/audit_source_anchors.py` after installation.

**No source snapshots were successfully acquired in the execution container. No human-adjudicated gold clauses or actual LLM/PyPSA results exist yet.** Source section anchors do not count as an extraction benchmark. CI check status must be verified independently.

## v0.7 — Snapshot-bound policy candidate extraction (2026-11-22)

Added [candidate extractor](src/energy_policy_llm/candidates.py), [local CLI](scripts/extract_local_candidates.py), [six synthetic unit tests](tests/test_candidates.py), and [protocol](docs/V07_LOCAL_CANDIDATE_EXTRACTION.md). Exact text spans, local snapshot hashes and legal section references are preserved. This is a **candidate worklist only**: no official full-text snapshots, human-gold annotations or LLM model scores have been obtained. The tool was locally smoke-tested on synthetic legal-style text; repository CI remains independently unconfirmed.

## v0.8 — Legal provenance gate and source-grounded risk probes (2026-11-22)

[Research gate](src/energy_policy_llm/research_gate.py) now checks frozen snapshot hashes, exact evidence offsets, declared independent review metadata and an entire held-out test jurisdiction (plus instrument/version isolation). [Ten official-section-grounded risk prompts](data/policies/real_rule_probes_v08.json) are manually paraphrased **research review prompts**, not human-adjudicated gold or LLM predictions. [Nine synthetic tests](tests/test_research_gate.py), [probe audit script](scripts/check_real_rule_probes.py), and [protocol](docs/V08_PROVENANCE_AND_REAL_RULE_PROBES.md) were added. **Zero empirical accuracy claims.** The provenance checker does not independently verify identity or substantive legal review; a formal gold corpus remains necessary.

## v0.9 — Executed synthetic sensitivity (2026-11-22)

The [toy translation experiment](src/energy_policy_llm/sensitivity.py) demonstrates that a retail-sales requirement miscast as a local generation-share constraint can yield a plausible optimization solution even though the semantic compiler should abstain. On the synthetic model, a 60% generation proxy cost is 137.5 vs 100 unconstrained (arbitrary units). [Seven extra unit tests](tests/test_sensitivity.py) and [results/limitations](docs/V09_SYNTHETIC_SENSITIVITY.md) are included. This is **not** a real policy impact or LLM accuracy result; real source-frozen expert labels are the next scientific bottleneck.

Run `python -m energy_policy_llm.sensitivity`. CI is configured but its status was not independently confirmed.

## v1.0 — First integrated held-out evaluation workflow (2026-11-22)

The [evaluation entry point](scripts/run_gated_evaluation.py) connects [provenance, frozen-source and jurisdiction gates](src/energy_policy_llm/validated_eval.py) to the existing [benchmark metrics](src/energy_policy_llm/benchmark.py). The checked-in [synthetic integration fixture](data/fixtures/synthetic_gated_v10.json) deliberately predicts local generation instead of retail sales and wrongly accepts a legal constraint. Its held-out test output must show 1/1 unsafe acceptance, 0 denominator matches, and `publication_ready=false`. Those are **fabricated demonstration outcomes**, NOT empirical accuracy results or measured LLM behavior. New tests and [protocol](docs/V10_GATED_EVALUATION.md) are included. Official source text snapshots and independently adjudicated gold labels remain unavailable; no real model benchmark has run.

Run `python scripts/run_gated_evaluation.py --dataset data/fixtures/synthetic_gated_v10.json --synthetic-demo`.

## v1.1 — Executed conservative paragraph baseline (2026-11-23)

[Baseline extractor](src/energy_policy_llm/real_text_baseline.py), [three official-section-inspired *paraphrases*](data/fixtures/official_section_paraphrases_v11.json), [runner](scripts/run_paraphrase_baseline.py), [five focused tests](tests/test_real_text_baseline.py), and [limits/next steps](docs/V11_BASELINE_SMOKE.md) have been added. The local standalone test passed 5/5. The deterministic baseline detects numeric percentages and years but correctly abstains from automatically creating legal constraints, and fails to parse spelled-out *fifty percent*. **These hand-written paraphrases are neither gold labels nor original full legal text, and no LLM performance result is claimed.**

Run `python scripts/run_paraphrase_baseline.py`. Full GitHub Actions status is not yet independently confirmed.

## v1.2 — Official excerpt review + real LLM prediction interface (2026-11-23)

Added [two short official legal excerpts](data/policies/official_excerpt_review_v12.json), [model-prediction JSONL validator](src/energy_policy_llm/prediction_io.py), [CLI](scripts/validate_llm_predictions.py), [8 unit tests](tests/test_prediction_io.py), and [reproducibility protocol](docs/V12_LLM_PREDICTION_HANDOFF.md). This enables storing and checking independently executed LLM outputs; it **does not** invoke an LLM, prove human gold adjudication, or report accuracy. Complete official source snapshots remain blocked by container DNS. Short excerpts are not full-source hashes or gold. CI has been configured and requires independent run confirmation.

## Safety metric correction (2026-11-23)

Fixed a substantive evaluation ambiguity: the original `unsafe_accept_rate` is calculated across all test cases; the new `unsafe_accept_rate_at_risk` conditions on cases where the reference decision is **not** `LEGAL_CONSTRAINT` and is `null` if no such case exists. Added [five regression tests](tests/test_metric_regression.py), strengthened synthetic vs adjudicated label separation, and [documented the metric audit](docs/METRIC_AUDIT_2026-11-23.md). These are software quality improvements, not new LLM findings. Targeted regression tests passed locally; GitHub Actions full status unconfirmed.

## Real government document capture through GitHub Actions (2026-11-23)

A dedicated [official corpus capture workflow](.github/workflows/capture-official-corpus.yml) uses a GitHub-hosted Ubuntu runner to try downloading both New Mexico administrative rules, freeze normalized UTF-8 snapshots, extract hash-bound candidate spans, reject short/error pages, and publish an unreviewed seven-day artifact. Full instructions: [runbook](docs/GITHUB_SOURCE_CAPTURE_RUNBOOK.md). The workflow is manually dispatchable and configured to trigger when first committed. **A successful actual run has NOT yet been verified; do not state that the full texts have been downloaded.** No fabricated text or human gold labels have been introduced. New [offline capture tests](tests/test_capture_corpus_ci.py) use synthetic HTML only.

## Capture workflow failure hotfix — 2026-11-23

After a reported failed capture run, added **per-source diagnostics** (network/parse, invalid content, zero candidates), a persisted failure manifest and a GitHub Actions failure artifact `NM-official-policy-capture-diagnostics`, plus two focused regression tests. The precise cause of the original failure has **not** been confirmed because its job log/run ID was not accessible. This patch is intended to make the next failure actionable; it does not claim a completed official full-text capture or gold dataset. [Capture workflow](.github/workflows/capture-official-corpus.yml) · [Runbook](docs/GITHUB_SOURCE_CAPTURE_RUNBOOK.md).
