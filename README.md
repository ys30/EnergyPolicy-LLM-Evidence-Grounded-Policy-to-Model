# EnergyPolicy-LLM: Evidence-grounded Policy-to-Model

**Status (updated 2026-11-25):** official-source extraction and a ChatGPT-assisted annotation pilot are underway; **not** validated legal compliance, an adjudicated gold benchmark, or a published study.

## Annotation pilot — ChatGPT-assisted prefill (2026-11-24 source queue; 2026-11-26 Excel prefill; review ongoing)

**Date clarification:** November 24 refers to completion of the first source-grounded section review queue; November 26 refers to the subsequent Excel AI field prefill. A separate AI-assisted verification of the 2025 rule was supplied on November 27. These are distinct milestones, **not** independently recorded model API runs.\n\n**What was actually done:** An OpenAI **ChatGPT conversational assistant** was used to help pre-fill candidate policy-obligation fields for **14 initial review tasks** in a working Excel annotation workbook for New Mexico's **2025 distribution-cooperative regulation, 17.9.571 NMAC**. The assistant worked from the source-grounded section review context (14 identified sections and 167 deterministic keyword-candidate lines) to suggest items such as target fraction/date, obligated entity, compliance denominator, REC considerations, exceptions, and preliminary model-mapping decisions. These are **AI-assisted draft annotations, not independently verified LLM predictions or adjudicated gold labels**. The workbook has not been deposited as a versioned GitHub research artifact.

**Model provenance:** The prefill was produced in an OpenAI ChatGPT chat session, **not** by this repository's API pipeline. The **exact backend model ID/version and a reproducible prompt/run log were not recorded** for that session; consequently, assigning a specific GPT model/version would be unsupported. This limitation will be rectified for future formal model runs by preserving model ID, prompt hash, raw outputs and timestamps.

**Progress:** The researcher reports having checked the **2025 rule against the source file**; structured field-level annotation and independent second-reviewer adjudication are **still in progress**. The current independently adjudicated **gold-standard count is 0**. The **14** rows are review tasks/AI-prefilled suggestions, **not** 14 externally executed benchmark calls. The **167** source candidates are regex-extracted text lines, not LLM-generated obligations.

**Important distinction:** The phrase *"used an LLM to pre-fill candidate obligations"* refers to the **manual, ChatGPT-assisted annotation preparation** above. Earlier README statements saying **"no LLM experiments yet"** refer specifically to the absence of **scripted, model-versioned, repeatable LLM/RAG benchmarking and accuracy measurements**. No direct-LLM-vs-RAG comparison, measured LLM accuracy, or empirical PyPSA impact result is claimed.

Related files: [official corpus verification](docs/SECTION_REVIEW_AUDIT_2026-11-24.md) · [annotation research protocol](docs/V03_ANNOTATION_PROTOCOL.md) · [future model output schema](docs/V12_LLM_PREDICTION_HANDOFF.md).

### Annotation correction and PyPSA mapping protocol (2026-11-27)

A follow-up AI review against the frozen NM 2025 statute found **one substantive draft field error** and several correction items: the denominator in NM25-007 must be blank because 17.9.571.8(A) has no standalone ratio; NM25-012 and NM25-014 draft evidence spans must end at **7857** and **10357**, excluding rule-history notes; 8(F)(2) introduces generation-and-transmission-cooperative supply responsibility; 8(F)(1) assigns *renewable energy* rather than a REC; 8(F)(3) is passive voice and does not establish the verifying actor; and the reasonable-cost threshold is a currency/MWh rule, **not** a renewable-share numerator or denominator. The cost test is determined annually by the cooperative, with a separate voluntary higher-cost permission. The definition of plan year alone does not establish a filing window.

**Annotation protocol:** ChatGPT/AI draft judgments should live in a separate `AI_suggestions` sheet. Reviewer A and Reviewer B must independently review a blinded copy, then a real adjudicator must decide final JSON, mapping labels and reasons; do not present copied AI judgments as two independent reviewers. The user's reviewed Excel is a local, uncommitted artifact and the formal **human-adjudicated gold count remains 0**.

**Research mapping:** Separate `legal_semantic_type` (TARGET, DEFINITION, ACCOUNTING, ELIGIBILITY, CONDITIONAL_TARGET, COST_EXCEPTION, PERMISSION, REPORTING), `compilation_role` (ENTITY_MAPPING, PARAMETER, ACCOUNTING_CONSTRAINT, ELIGIBILITY_RULE, CONDITIONAL_LOGIC, REPORTING_ONLY) and `executability` (LEGAL_CONSTRAINT, SCENARIO_PROXY, ABSTAIN / unresolved) rather than applying ABSTAIN to all nonpercentage definitions. Validate model entities, annual retail-sales denominator, REC ownership/retirement/banking, costs and conditions before compiling to PyPSA. The 14 rows are **pilot review tasks, not a sufficient training dataset**.

**Coverage gaps:** 17.9.571.9 (conditional 2050 **100% zero-carbon** standard), 17.9.571.11 (REC ownership, transfers, four-year carry-forward and record retention) and 17.9.571.13 (annual report by **April 30**, reporting fields) require additional review. Initial follow-up queue has 12 topic-level tasks; many require decomposition into atomic obligations. Potential inconsistent internal references in 17.9.571.11(D)/(H) to 17.9.571.13 subsections are flagged as **source ambiguities**, not silently corrected. All new tasks remain AI-prepared and unadjudicated.

## Annotation Codebook v1.3 — Dual LLM + Human Verification (2026-11-27)

The [annotation codebook v1.3](docs/POLICY_TO_PYPSA_ANNOTATION_CODEBOOK_V1.md) specifies two independent tracks: conventional legal/compliance annotation, and a concrete PyPSA input/compilation review. It defines source evidence, normalized legal fields, controlled labels, blinded reviewer/adjudicator workflows, typed intermediate representation, model profiles, source-to-variable bindings, external REC/retail-sales accounting, Linopy compilation routes, and pre-solve/post-solve validation gates. It includes worked source-grounded examples for NM 2025 17.9.571.8–.13 and the annotation status/quality gates. A [literature-grounded v1.2 extension](docs/POLICY_TO_PYPSA_ANNOTATION_CODEBOOK_V1.md#11-literature-grounded-amendments-v12-2026-11-27) adds actor/beneficiary/antecedent/consequent slots, evidence entailment, field-wise agreement, explicit PyPSA-USA RPS/REC-zone baselines, and distinction between aggregate policy proxies and verified certificate ledgers.

**Status:** codebook **proposed (v1.3), with a new dual-LLM comparison and non-gold human-review validation utility but not yet a complete runtime compiler** as the full Python schema/compiler and not yet human adjudicated; 14 original + 12 additional topic-level review tasks are **not 26 gold obligations**. The independently adjudicated gold count remains **0**. Current `schema.py`/`compiler.py` implement a narrower proof-of-concept; actual REC ledger and PyPSA integration are future implementation work.

### Two-AI / one-human pilot protocol (2026-11-27)

**Protocol:** `DUAL_LLM_SINGLE_HUMAN_VERIFICATION`. Two independently executed and model-versioned LLM annotations are compared using [source-checked tooling](src/energy_policy_llm/dual_llm_review.py) and [CLI](scripts/compare_dual_llm_annotations.py). A single real human must inspect **every** record, the full governing source context, missing obligations, and all field/evidence differences. Model agreement **never** automatically promotes a record to a gold label.

Statuses are `AI_AGREED`/`AI_DISAGREED` for AI-only comparison, `HUMAN_VERIFIED` for explicitly signed single-human review, and `EXPERT_REVIEW_REQUIRED` for unresolved matters. The existing [two-independent-human gold gate](src/energy_policy_llm/annotations.py) stays unchanged; `human_verified_reference_count` and `independently_adjudicated_gold_count` are separate. **Current real human-verified count = 0; independent gold count = 0; no two real model inference runs have been executed by these new utilities.** Synthetic unit tests do not count as annotation experiments. Details: [Codebook v1.3 §12](docs/POLICY_TO_PYPSA_ANNOTATION_CODEBOOK_V1.md#12-approved-alternative-pilot-protocol-two-independent-llms--one-human-v13).

## Five-clause Codebook pilot — source-checked AI drafts (2026-11-27)

[Five-clause pilot report](docs/FIVE_CLAUSE_ANNOTATION_PILOT_V1.md) · [versioned AI pilot records](data/policies/nm_coop_five_clause_pilot_v1.json). Five sections of frozen NM cooperative law — **8(B), 8(D), 9(A), 10(A), 11(D)** — have verified exact char offsets and Codebook-v1 semantic tags. The pilot separates source-cited legal extraction, model-specific executability and incomplete/ambiguous cross-references. All 5 remain **AI suggestions, not two independently annotated records**; `gold_count=0`. No PyPSA solve or empirical LLM benchmark is claimed. The review workbook was delivered separately in the conversation; source snapshots remain an expiring GitHub Actions artifact rather than committed full text.

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
- **No LLM API or credentials required** to run this repository. A separate ChatGPT-assisted, **unversioned** prefill produced 14 draft human-review tasks; the committed extraction baseline is deterministic. No formal, reproducible LLM/RAG benchmark has yet been executed.
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

**Annotation-stage clarification (updated 2026-11-25):** A separate ChatGPT conversational prefill later prepared 14 draft policy-review tasks for the 2025 NM cooperative regulation. This did **not** involve this baseline script, and its exact backend model version was not logged. See the prominent [annotation pilot](#annotation-pilot--chatgpt-assisted-prefill-2026-11-24-review-ongoing) section above.

## v1.2 — Official excerpt review + real LLM prediction interface (2026-11-23)

Added [two short official legal excerpts](data/policies/official_excerpt_review_v12.json), [model-prediction JSONL validator](src/energy_policy_llm/prediction_io.py), [CLI](scripts/validate_llm_predictions.py), [8 unit tests](tests/test_prediction_io.py), and [reproducibility protocol](docs/V12_LLM_PREDICTION_HANDOFF.md). This enables storing and checking independently executed LLM outputs; it **does not** invoke an LLM, prove human gold adjudication, or report accuracy. Complete official source snapshots remain blocked by container DNS. Short excerpts are not full-source hashes or gold. CI has been configured and requires independent run confirmation.

## Safety metric correction (2026-11-23)

Fixed a substantive evaluation ambiguity: the original `unsafe_accept_rate` is calculated across all test cases; the new `unsafe_accept_rate_at_risk` conditions on cases where the reference decision is **not** `LEGAL_CONSTRAINT` and is `null` if no such case exists. Added [five regression tests](tests/test_metric_regression.py), strengthened synthetic vs adjudicated label separation, and [documented the metric audit](docs/METRIC_AUDIT_2026-11-23.md). These are software quality improvements, not new LLM findings. Targeted regression tests passed locally; GitHub Actions full status unconfirmed.

## Real government document capture through GitHub Actions (2026-11-23)

A dedicated [official corpus capture workflow](.github/workflows/capture-official-corpus.yml) uses a GitHub-hosted Ubuntu runner to try downloading both New Mexico administrative rules, freeze normalized UTF-8 snapshots, extract hash-bound candidate spans, reject short/error pages, and publish an unreviewed seven-day artifact. Full instructions: [runbook](docs/GITHUB_SOURCE_CAPTURE_RUNBOOK.md). The workflow is manually dispatchable and configured to trigger when first committed. **A successful actual run has NOT yet been verified; do not state that the full texts have been downloaded.** No fabricated text or human gold labels have been introduced. New [offline capture tests](tests/test_capture_corpus_ci.py) use synthetic HTML only.

## Capture workflow failure hotfix — 2026-11-23

After a reported failed capture run, added **per-source diagnostics** (network/parse, invalid content, zero candidates), a persisted failure manifest and a GitHub Actions failure artifact `NM-official-policy-capture-diagnostics`, plus two focused regression tests. The precise cause of the original failure has **not** been confirmed because its job log/run ID was not accessible. This patch is intended to make the next failure actionable; it does not claim a completed official full-text capture or gold dataset. [Capture workflow](.github/workflows/capture-official-corpus.yml) · [Runbook](docs/GITHUB_SOURCE_CAPTURE_RUNBOOK.md).

## Section-level completeness correction (2026-11-24)

The [verified audit](docs/SECTION_REVIEW_AUDIT_2026-11-24.md) fixed false heading matches caused by wrapped references like `17.9.572.16 NMAC`. Both official snapshots now pass distinct ordered section checks: **22 IOU + 14 cooperative sections**, with **276 + 167 = 443** unreviewed keyword-bearing candidate lines. Two source-hash-linked `*.review_queue.json` files contain complete section context (36 review units, 7 high-priority) in the [successful GitHub Actions artifact](https://github.com/ys30/EnergyPolicy-LLM-Evidence-Grounded-Policy-to-Model/actions/runs/45443775485/artifacts/14943748446). The [capture run](https://github.com/ys30/EnergyPolicy-LLM-Evidence-Grounded-Policy-to-Model/actions/runs/45443775485) and [repository CI](https://github.com/ys30/EnergyPolicy-LLM-Evidence-Grounded-Policy-to-Model/actions/runs/45443775436) both succeeded. These are **not 443 distinct legal obligations or adjudicated gold labels**; additional legal review is required.
