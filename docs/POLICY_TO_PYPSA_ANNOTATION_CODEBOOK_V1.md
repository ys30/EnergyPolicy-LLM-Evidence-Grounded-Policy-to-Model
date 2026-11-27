# Policy-to-PyPSA Annotation Codebook v1.1

**Updated:** 2026-11-27 (v1.1) | **Status:** PROPOSED — draft human-annotation protocol, **not** an adjudicated gold standard.

**Project:** EnergyPolicy-LLM — Evidence-Grounded Policy-to-Model  
**Current source materials:** Frozen `NM_COOP_2025.txt` (17.9.571 NMAC; source SHA-256 `673f60931b4a2ba68c2de2c67601097bc292da8998536bdb38b3d014acfdea01`) and `NM_2025_Policy_to_PyPSA_Reviewed_AI_Draft_Blind_Annotation.xlsx`.  
**Scope:** **14 original review tasks plus 12 newly identified preliminary tasks**. These are **not 26 confirmed atomic legal obligations**. Fourteen legal sections and 167 keyword-matched candidate lines represent different units of analysis. Independent human Reviewer A/B annotation and adjudication have not yet been completed; `gold_count=0`.

> **Reading sequence:** (1) Units and evidence → (2) Legal semantics → (3) PyPSA compilation → (4) Quality and disagreements → (5) Workflow → (6) Examples. **Never populate human Reviewer A/B or final adjudication fields with AI-generated suggestions.**

## 1. Annotation units and segmentation

| Unit | Definition | Identifier | Suitable as a training/evaluation instance? |
|---|---|---|---|
| Source snapshot | Frozen official source text with legal version, retrieval date, and complete SHA-256 | `source_id + sha256` | Evidence source |
| Section | A numbered regulatory section (e.g., 17.9.571.8), possibly comprising several subsections, cross-references, and historical notes | `source_id + section` | Retrieval and grouping unit only |
| Candidate line | A physical text line located by regex/keyword search (167 for this source) | Character offsets | **Not automatically a gold label** |
| Review task | An initial clause/topic to inspect (26 at present) | `Case_ID` | Worklist unit, not necessarily one obligation |
| **Atomic legal proposition** | Smallest independently judgeable legal duty, permission, definition, or condition, preserving its qualifications and cross-references | `annotation_id` | Eligible for gold **only after independent human annotation and actual adjudication** |
| Model-mapping candidate | Proposed translation into PyPSA or a separate accounting component for a specified `model_profile_id` | `annotation_id + model_profile_id` | Compilation evaluation only; not a substitute for legal annotation |

**Segmentation rule:** Separate different regulated entities, actions, percentages, deadlines, responsibility assignments, exceptions, REC ownership/transfer/retirement, and reporting duties. Preserve every qualification applicable to each atomic proposition. Cross-provision combinations require `depends_on_annotation_ids`. A line, a section, or a numerical percentage is **not** itself proof of an independently complete legal obligation.

## 2. Field dictionary: identity, primary-source evidence, and provenance

| Field | Type / allowed values | Definition and decision rule |
|---|---|---|
| `annotation_id` | Unique string, e.g., `NM25-008-TARGET` | One per atomic proposition; preserve links to the original review task |
| `parent_case_id` | Existing `NM25-001...026` identifiers | Traceability to the spreadsheet; append identifiers for split obligations |
| `source_id` / `rule_version` | `NM_COOP_2025` / official version information | Do not confuse annotation date with the effective/amendment date |
| `source_sha256` | 64-character SHA-256 | Must match the frozen UTF-8 source text |
| `provision` / `subsection` | E.g., `17.9.571.8`, `B`, `F(2)` | Identify the smallest reliably distinguishable subsection; never silently repair a source cross-reference |
| `start_char`, `end_char` | Nonnegative integers; **zero-based, end-exclusive** | Python character offsets; `text[start:end] == exact_text` must hold; exclude unrelated regulatory history notes |
| `exact_text` | Verbatim string | Exact evidence, not a paraphrase; retain line breaks and whitespace from the frozen text |
| `evidence_role` | `PRIMARY`, `DEFINITION`, `CROSS_REFERENCE`, `CONDITION`, `EXCEPTION` | Multiple spans may be recorded in `evidence_spans[]` |
| `source_verification` | `MATCHED`, `MISMATCH`, `NOT_CHECKED` | Source-text agreement **does not** establish adjudicated legal meaning |
| `annotation_origin` | `AI_SUGGESTION`, `HUMAN_A`, `HUMAN_B`, `ADJUDICATED` | Label origin must remain explicit in every export; do not blend AI and human judgments |
| `field_status` | `VERIFIED`, `REQUIRES_CORRECTION`, `INSUFFICIENT_EVIDENCE`, `NOT_APPLICABLE` | **Missing is not zero**; use null with `NOT_APPLICABLE` where appropriate |

**Known source-review corrections:** The legacy NM25-012 and NM25-014 evidence spans should end at **7857** and **10357**, respectively, excluding rule-history notes. Legacy NM25-007 points to 17.9.571.8(A), which does not itself specify a ratio, so `denominator=null`. Revalidate source substring equality after every span edit.

## 3. Legal-semantic annotation (independent of any model configuration)

| Field | Allowed values / format | Definition and instructions |
|---|---|---|
| `legal_semantic_type` | Primary label from §3.1 | Main legal function; split compound obligations; use secondary types only when needed |
| `normative_force` | `MUST`, `MUST_NOT`, `MAY`, `DEFINITION`, `CONDITIONAL_MUST`, `REPORTS`, `UNKNOWN` | Distinguish obligations, permissions, conditional requirements, and definitions; never turn MAY into MUST |
| `obligated_entity` | `cooperative`, `distribution_cooperative`, `generation_transmission_cooperative`, `utility`, `other`, `UNKNOWN` | Use the controlled vocabulary. Preserve the G&T responsibility cross-references in 8(F)(2) and 9(B) rather than conflating entity roles |
| `regulated_action` | Controlled action with supporting free text | Examples: meet RPS, retire REC, determine annual costs, submit report, retain records |
| `target_fraction` | Decimal 0–1 or null | `0.40`, `0.50`, `0.80`, `1.00` (not 40, 50, etc.); null for provisions without percentage targets |
| `target_date` | ISO date `YYYY-MM-DD` or null | Distinguish compliance deadlines, rule versions, filing dates, and applicable periods |
| `date_role` | `DEADLINE`, `PERIOD_START`, `ANNUAL_FILING_DUE`, `HISTORICAL_CUTOFF`, `EFFECTIVE_DATE`, `UNKNOWN` | A date's legal meaning matters; publication date is not automatically the target date |
| `compliance_period` | `CALENDAR_YEAR`, `PLAN_YEAR`, `MULTIYEAR`, `UNKNOWN`, null | Assign only with direct text or justified cross-reference evidence. Defining “plan year” alone **does not establish a filing window** |
| `numerator_metric` | `ELIGIBLE_RENEWABLE_ENERGY_MWH`, `ZERO_CARBON_ELECTRICITY_MWH`, `QUALIFYING_RECS_MWH_EQUIV`, `OTHER`, null | Capture eligibility and REC accounting conditions; 8(A) supplies no independent ratio |
| `denominator_metric` | `NM_TOTAL_RETAIL_SALES_MWH`, `NM_RETAIL_ELECTRICITY_SUPPLIED_MWH`, `GENERATION_MWH`, `OTHER`, null | Do not equate different statutory terms without an evidenced normalization rule |
| `rec_accounting` | Multiselect: `RETIREMENT`, `OWNERSHIP`, `TRANSFER`, `BANKING`, `TRACKING`, `NONE`, `UNKNOWN` | Record REC treatment separately for 8(A) and the more detailed provisions in §11 |
| `eligibility_conditions` | Structured conditions or null | Capture resource qualifications, temporal eligibility, ownership, and exclusions; do not simply write “compliant” |
| `condition_logic` | `ALL`, `ANY`, `IF_THEN`, `NONE`, `UNKNOWN` plus condition records | Preserve all three jointly required conditions for the 2050 provisions; do not compile unconditional 80%/100% targets |
| `exceptions` | `exception_type` and supporting clause spans | Document exemptions and reasonable-cost limitations individually |
| `monetary_threshold` | Amount, `USD/MWh`, base year | For example, 60 USD/MWh with the specified inflation update and cost basis; never populate RPS numerator/denominator with a cost measure |
| `decision_maker` | Explicitly identified legal actor or `UNKNOWN` | Under 10(A), the cooperative makes its annual cost determination; passive voice elsewhere cannot establish an unstated verifying actor |
| `source_ambiguity` | `NONE`, `CROSS_REFERENCE_MISMATCH`, `UNDEFINED_TERM`, `TEMPORAL_AMBIGUITY`, `OTHER` | Flag potential miscitation in 11(D)/(H) to §13. Preserve the literal reference rather than rewriting it as §11 |

### 3.1 Primary legal-semantic labels

| Label | Operational definition | Positive example from NM 17.9.571 | Exclusions and warnings |
|---|---|---|---|
| `DEFINITION` | Defines a term, entity class, or accounting concept without independently imposing a numerical target | §7: distribution-cooperative terminology | Lack of a standalone optimization constraint does not make the definition irrelevant |
| `TARGET` | Specifies a binding numerical, percentage, and/or time-bound objective | 8(B): 40% by 2025; 8(C): 50% by 2030 | 8(A) is an accounting/compliance mechanism, not a separate percentage |
| `CONDITIONAL_TARGET` | Establishes an objective subject to explicit prerequisites | 8(D): 80% in 2050; 9(A): 100% zero-carbon electricity in 2050 | Never produce unconditional hard constraints |
| `ACCOUNTING` | Specifies compliance measurement, REC retirement, bookkeeping, transfer, or carry-forward | 8(A), §11 | Not equivalent to a simple installed-capacity or local-generation requirement |
| `ELIGIBILITY` | Determines which entities, resources, or historical facilities can count | 8(E): pre-2008 resources subject to the rule's criteria | Do not infer that all existing resources qualify |
| `RESPONSIBILITY` | Allocates legal duties between cooperatives, including G&T and distribution cooperatives | 8(F)(1)–(3), 9(B) | 8(F)(1) assigns *renewable energy*, not necessarily RECs |
| `COST_EXCEPTION` | Establishes cost-triggered exceptions or limitations | 10(A): 60 USD/MWh subject to required adjustment | Not a renewable-energy share; preserve cooperative's annual determination |
| `PERMISSION` | Permits, but does not mandate, an action | 10(B): voluntarily bear costs above the threshold | MAY ≠ MUST |
| `REPORTING` | Imposes report content, retention, or filing duties | 13(A): April 30 annual filing concerning the prior calendar year | A filing date is not an RPS achievement deadline |
| `OTHER` | A genuine provision not adequately covered by the above classes | Explain in writing | Do not use this label simply to bypass difficult interpretation |

## 4. PyPSA compilation labels (separate from legal meaning)

### 4.1 `compilation_roles[]` (multilabel)

| Label | Definition | Example | Expected artifact |
|---|---|---|---|
| `ENTITY_MAPPING` | Links a legally responsible entity to model utility/BA/bus/load sets | G&T responsibility for member distribution cooperatives | Traceable `entity_map`, not automatically a percentage constraint |
| `PARAMETER` | Supplies a target percentage, date, price, or technological parameter | 50%, 2030, 60 USD/MWh | Typed parameter with units and scope |
| `OPTIMIZATION_CONSTRAINT` | Can be expressed using verified model variables as a direct LP/MILP constraint | An explicitly defined capacity bound, where supported | Equation, units, scope, and temporal resolution |
| `ACCOUNTING_CONSTRAINT` | Requires an external/extended compliance-accounting relation | Retail electricity sales, REC retirement | Retail-sales and REC ledger components; not local generation |
| `ELIGIBILITY_RULE` | Selects qualifying technologies, facilities, or certificates | 8(E) resource grandfathering | Supported eligible-resource set |
| `CONDITIONAL_LOGIC` | Activates or relaxes a requirement only when specified conditions hold | Conditional targets in 8(D) and 9(A) | Structured condition dependencies and activation rule |
| `COST_EXCEPTION_LOGIC` | Computes and applies cost thresholds or exceptions | 10(A) | Base year, CPI adjustment, eligible costs, decision-making actor |
| `REPORTING_ONLY` | Requires compliance-report output but not a direct optimization constraint | 13(A) | Compliance reporting artifact |
| `DEPENDENCY_ONLY` | Informs interpretation of another provision, without standalone compilation | Definitions in §7 | Ontology and dependency mapping |
| `UNRESOLVED` | Translation or dependencies remain materially uncertain | Conflicting cross-reference, missing REC data | Block automatic legal-equivalent deployment |

**Compilation role is not executability.** A definition may be both `ENTITY_MAPPING` and `DEPENDENCY_ONLY` while being `NOT_DIRECTLY_EXECUTABLE` as an individual constraint.

### 4.2 Executability and safety decisions (require a model profile)

| `executability` | Criteria | `legal_equivalence` |
|---|---|---|
| `LEGAL_CONSTRAINT` | Human-adjudicated meaning; entity, denominator, REC, period and required variables supported; a demonstrably semantically equivalent executable implementation | true **only with evidence of equivalence** |
| `SCENARIO_PROXY` | Explicit, defensible approximation with documented differences, assumptions, and interpretation limits | **false** |
| `ABSTAIN` | Legal ambiguity, missing critical inputs, or unmet/undeterminable conditions preclude automatic constraint generation | false |
| `NOT_DIRECTLY_EXECUTABLE` | Definition, report, or allocation of responsibility is not itself a single optimization constraint but may support downstream work | null / not applicable |
| `UNASSESSED` | `model_profile_id` is not defined or compilation has not yet been evaluated | null |

**Record all of:** `model_profile_id`, `compiler_version`, `missing_dependencies[]`, `mapping_assumptions[]`, and `equivalence_rationale`. Legal meaning should be stable across model configurations, while the executable decision can change. Never overwrite the legal label with `SCENARIO_PROXY`.

### 4.3 Illustrative compliance-accounting expression (not an approved legal-equivalence claim)

For a reviewed regulated entity `u` and compliance year `y`, a *candidate conceptual* RPS constraint is:

```text
retired_eligible_REC_MWh_equivalent[u,y] >= target_fraction[y] * NM_retail_sales_MWh[u,y]
```

Before implementing it, review the legal relationship among retired certificates and qualifying electricity, supply responsibility, banking, certificate eligibility, exceptions, and compliance periods. **This expression is not yet a verified or directly deployable PyPSA constraint.** Never silently replace it with `local_renewable_generation / local_total_generation >= target`. The latter can at most be an explicitly labeled `SCENARIO_PROXY` when justified.

### 4.4 Two independent review tracks: legal compliance and model compilation (v1.1 extension)

**Track L — conventional legal/compliance review, independent of PyPSA.** The reviewer first checks the authoritative source, effective/version dates, scope and obligated entity, normative force, defined metrics, denominator, time basis, eligibility, certification/REC ownership and retirement, cost exceptions, conditions, cross-references, and reporting obligations. The result is a **semantic annotation** and a reviewer-specific interpretation, not yet model code. Conflicts or source errors must be flagged, not silently repaired.

**Track M — PyPSA feasibility and compilation review, explicitly conditioned on `model_profile_id`.** A separate reviewer inventories the network, time resolution, variables, datasets, external accounting modules, mathematical feasibility, solver and numerical behavior. The result is a **model-mapping evaluation**, never a retroactive alteration of the legal meaning.

| Gate | Mandatory question | PASS | FAIL / UNKNOWN |
|---|---|---|---|
| L1 Source | Is the exact original clause/version/offset reproducible? | Verified snapshot and evidence spans | Hold for source correction |
| L2 Legal meaning | Are actor, obligation, calculation base, time and cross-provisions documented? | All relevant legal fields supported | `LEGAL_REVIEW_REQUIRED` |
| L3 Conditions | Are permissions, cost thresholds and 2050 conditions preserved? | Explicit Boolean/temporal clauses | `SOURCE_AMBIGUITY` or `LEGAL_REVIEW_REQUIRED` |
| M1 Network | Does the selected PyPSA network represent the actors, nodes, components and periods? | Concrete network and entity map | `MODEL_INPUT_MISSING` |
| M2 Accounting | Are legal retail sales, REC eligibility, ownership, banking and retirement represented when necessary? | Verified external or integrated accounting system | `ACCOUNTING_MODULE_REQUIRED` |
| M3 Equation | Does the intended equation use dimensionally compatible model symbols and preserve the legal metric? | Reviewed symbolic IR and variable map | `SEMANTIC_MISMATCH` |
| M4 Execution | Does the test model build, solve and satisfy residual and unit checks? | Recorded test, solver status and tolerances | `SOLVE_FAILED` / `VALIDATION_FAILED` |
| M5 Equivalence | Are L1–L3 and M1–M4 passed with no unsupported assumptions? | Candidate `LEGAL_CONSTRAINT` after review | Otherwise `SCENARIO_PROXY`, `ABSTAIN`, or `NOT_DIRECTLY_EXECUTABLE` |

For annotation, keep `legal_review_status` and `model_validation_status` **separate**. A legally correct clause may be impossible to implement in a given network. A feasible optimization is **not proof of statutory compliance**.

### 4.5 PyPSA input contract: model data and missing legal data

Use a versioned `ModelProfile` manifest before making any `executability` decision. The table below describes practical inputs, not a claim that every model needs every component.

| Input requirement | Typical PyPSA object / variable | Unit and temporal checks | When required / frequent mismatch |
|---|---|---|---|
| Network identity | `pypsa_version`, network `.nc` or built model, network hash | Version, topology and model revision | Always; model must be reproducible |
| Topology and entity geography | `n.buses`, `n.lines`, `n.links`, `n.transformers`; external `utility_to_bus_map` | Actor→bus membership, multi-area boundaries, imports | Entity/scope requirements; **BA is not automatically a retail seller or cooperative** |
| Carriers and eligibility | `n.carriers`, `n.generators.carrier`; external certified eligible-resource table | Eligible renewable vs zero-carbon taxonomy; plant ID and certification vintage | RPS, zero-carbon, historical resources; generic `carrier='wind'` is insufficient legal eligibility proof |
| Demand and retail sales | `n.loads`, `n.loads_t.p_set`; **external `retail_sales_mwh[entity,year]`** | MW load vs MWh billed retail sales; losses, behind-the-meter, exports and ownership | Retail-sales denominator; dispatch load is **not automatically** statutory retail sales |
| Dispatch and capacity | `n.generators`, `n.generators_t`, Linopy `Generator-p`, `Generator-p_nom` where applicable | MW vs MWh, fixed vs extendable capacity, availability `p_max_pu` | Energy-share proxy and capacity rules; dispatch does not identify who owns or retires RECs |
| Storage and conversion | `n.storage_units`, `n.stores`, `n.links` and relevant dispatch variables | Round-trip losses, energy balance, charge/discharge double counting | Renewable/zero-carbon accounting must avoid treating storage discharge as new generation |
| Time indexing | `n.snapshots`, `n.snapshot_weightings`; multi-period `investment_period_weightings` where relevant | Time zone; leap year; representative hours; MW × weighted hours = MWh; annual obligation vs model period | Required for every energy sum; do not confuse objective weights, generator energy weights and investment-year weights |
| Price and costs | `capital_cost`, `marginal_cost`, network objective; **external CPI and statutory cost-basis fields** | Currency year, real vs nominal, USD/MWh denominator and recoverable cost | §10 reasonable-cost threshold cannot be inferred from optimization objective alone |
| REC compliance ledger | **External or newly implemented** REC issue/owner/transfer/retirement/bank tables | MWh equivalence, vintage, location, double-count prevention, carry-forward limits | §8/§11 requirements; **not a native REC ownership/retirement ledger in an ordinary PyPSA network** |
| Conditions and exception decisions | **External evidence/structured Boolean conditions** | Each condition's source, evaluation year, deciding authority and UNKNOWN state | §8(D), §9(A), §10; absent evidence must not silently become true |
| Report obligation | External reporting record and compliance outputs; PyPSA results as supporting data | Reporting deadline vs target deadline; prior-year reference | §13; generally not a hard dispatch constraint |

PyPSA components and optimization details are documented at:
- [PyPSA network design and components](https://docs.pypsa.org/latest/user-guide/design/)
- [PyPSA network optimization](https://docs.pypsa.org/latest/user-guide/network-optimization/)
- [PyPSA custom constraints (Linopy)](https://docs.pypsa.org/latest/user-guide/optimization/custom-constraints/)
- [Network.optimize API and extra_functionality](https://docs.pypsa.org/stable/api/networks/optimize/)
- [PyPSA statistics and energy aggregation](https://docs.pypsa.org/latest/api/networks/statistics/)

**Critical version check:** `Generator-p` and `Generator-p_nom` are indicative Linopy variable names and availability depends on network/model construction. Verify actual `n.model.variables` and component/coordinate names at runtime; never generate speculative code by relying on fixed names without checking.

### 4.6 Required new compilation annotation fields

| Field | Type / controlled values | Definition and reviewer instruction |
|---|---|---|
| `compilation_target` | `NATIVE_COMPONENT`, `LINOPY_CUSTOM_CONSTRAINT`, `EXTERNAL_ACCOUNTING`, `POSTPROCESSING`, `NO_DIRECT_COMPILATION`, `UNDETERMINED` | Actual destination of an atomic rule; multistage mappings may list several targets |
| `model_profile_id` | Immutable versioned ID | Identifies concrete PyPSA version, network, data coverage, solver, and available compliance modules |
| `model_scope` | entity IDs, buses, year(s), investment periods | The model coverage to which the rule is applied, not the statute's whole jurisdiction |
| `policy_metric_id` | `NM_RETAIL_SALES_RPS`, `NM_ZERO_CARBON_RETAIL`, `REC_RETIREMENT`, `COST_USD_PER_MWH`, `REPORTING`, `OTHER` | Controlled legal metric. Must preserve renewable vs zero-carbon distinction |
| `input_bindings[]` | list of `{symbol,source_object_or_dataset,dimension,unit,aggregation,provenance}` | Every symbolic term must resolve to an actual model variable or verified external table |
| `missing_dependencies[]` | `RETAIL_SALES`, `ENTITY_MAP`, `REC_LEDGER`, `RESOURCE_ELIGIBILITY`, `CPI`, `COST_BASIS`, `CONDITION_EVIDENCE`, `TIME_COVERAGE`, `NONE`, `OTHER` | Specific blockers, not generic “data missing” |
| `constraint_ir` | reviewed symbolic JSON/DSL or null | Typed equation with `lhs`, `sense`, `rhs`, `units`, `index_sets`; no raw LLM-produced executable Python |
| `aggregation_method` | `FULL_HOURLY`, `WEIGHTED_SNAPSHOTS`, `YEARLY_EXTERNAL`, `MULTI_INVESTMENT_PERIOD`, `NOT_APPLICABLE` | How temporal or spatial aggregation is performed |
| `constraint_class` | `LINEAR`, `MIXED_INTEGER`, `NONLINEAR_UNSUPPORTED`, `POSTPROCESS_ONLY`, `NOT_APPLICABLE` | Distinguish feasible LP/MILP from operations requiring other formulations |
| `compile_readiness` | `READY`, `READY_PROXY_ONLY`, `BLOCKED_LEGAL`, `BLOCKED_INPUT`, `BLOCKED_FORMULATION`, `NOT_APPLICABLE`, `UNASSESSED` | Pre-solve readiness. Do **not** imply the optimization was actually run |
| `validation_status` | `NOT_RUN`, `BUILD_PASSED`, `SOLVED`, `INFEASIBLE`, `SOLVER_ERROR`, `RESIDUAL_FAILED` | Evidence about actual execution; separately retain solver termination, objective, numerical tolerance |
| `legal_equivalence` | true / false / null | True only after legal and computational acceptance gates; absent model verification → null |
| `error_risk_type[]` | `WRONG_DENOMINATOR`, `WRONG_ENTITY`, `WRONG_ELIGIBILITY`, `REC_DOUBLE_COUNT`, `WRONG_YEAR`, `MISSED_CONDITION`, `COST_MISINTERPRETATION`, `SOURCE_AMBIGUITY`, `OTHER` | Mechanism for controlled policy-translation error experiments |
| `human_compiler_review` | reviewer ID, date, rationale | Separate from legal Reviewer A/B; no fabricated approvals |

Prefer **two separate decisions**: `compile_readiness` before model execution, and `validation_status` after execution. Treat `LEGAL_CONSTRAINT` as a stringent eventual result, not a synonym for “a constraint can be written.”

### 4.7 Compilation pipeline: legal review → typed IR → PyPSA → verification

1. **Standard legal review** produces atomic evidence-bound records, with legal entity, normative force, percentage/date, conditions, exceptions, legal source ambiguity and cross-reference edges.
2. **Typed intermediate representation (IR)** encodes each operation without any PyPSA API calls. Examples: `share_minimum`, `certificate_retirement`, `eligibility_filter`, `conditional_activation`, `reporting_deadline`. Preserve `UNKNOWN` explicitly.
3. **Input binding** checks exact entity keys, units and dataset identifiers. A legal retail-sales denominator requires external retail-sales data or a proven equivalent dataset. REC counting requires a designated accounting layer.
4. **Static compilation** chooses `NATIVE_COMPONENT`, `LINOPY_CUSTOM_CONSTRAINT`, `EXTERNAL_ACCOUNTING`, `POSTPROCESSING` or `NO_DIRECT_COMPILATION`. Reject unsupported or non-linear formulations in the chosen LP workflow.
5. **Solver execution** uses a pinned PyPSA/Linopy/solver environment. PyPSA documents either `n.optimize(extra_functionality=callback)` or `n.optimize.create_model(); n.model.add_constraints(...); n.optimize.solve_model()`. The callback signature is `callback(n, snapshots)`. Generated constraint names and mathematical residuals must be inspected.
6. **Postsolve verification** recomputes policy quantities from solution/output and external ledgers, checks consistency and numerical tolerances, and records feasibility. Report `LEGAL_CONSTRAINT` only if conventional legal review and computational checks both support it.
7. **Counterfactual evaluation** compares baseline vs policy runs on the *same* model/data and isolates policy-translation errors from unrelated scenario changes. Track objective cost, capacity, dispatch, curtailment, emissions, compliance gap, and infeasibility. Do not describe these as empirical findings until actually run.

### 4.8 Decision examples for the NM 2025 pilot

| Provision | Track L (conventional review) | Track M (model input / formulation) | Recommended pre-execution label |
|---|---|---|---|
| 8(A), REC retirement | Confirm certificate retirement and entity obligations | `EXTERNAL_ACCOUNTING`; REC ledger absent in ordinary dispatch-only PyPSA | `BLOCKED_INPUT` unless ledger supplied |
| 8(C), 2030 50% | Confirm retail-sales denominator, qualifying REC accounting, supply responsibility 8(F)(2) | Requires `retail_sales_mwh`, entity map, REC eligible/retired quantities, annual coverage | `BLOCKED_INPUT`; explicit generation-share scenario can instead be `READY_PROXY_ONLY` |
| 8(D), 2050 conditional 80% | Three jointly required conditions | Structured condition evidence + 2050 model data + REC and retail-sales coverage | `BLOCKED_INPUT` or `BLOCKED_LEGAL` if unresolved meaning |
| 9(A), 2050 100% zero-carbon | Preserve zero-carbon ≠ renewable and three conditions | Zero-carbon resource eligibility table independent of renewable label | `BLOCKED_INPUT` until eligibility/conditions available |
| 10(A), $60/MWh | Cooperative annually decides applicability; inflation and statutory cost metric | CPI and true cost basis; optimization objective alone is insufficient | `BLOCKED_INPUT`; do not generate arbitrary cost cap |
| 11(D)/(H), suspect cross-reference | Preserve literal source reference and `CROSS_REFERENCE_MISMATCH` | Do not automatically reroute to §11 | `BLOCKED_LEGAL` for the affected relation |
| 13(A), April 30 filing | Report covers prior calendar year | `POSTPROCESSING` output + filing metadata | `NOT_APPLICABLE` for standalone LP constraint; reporting task remains valid |

### 4.9 Machine-readable example of a **proposed** intermediate representation

```json
{
  "annotation_id": "NM25-009-TARGET",
  "legal_review_status": "PENDING_HUMAN_ADJUDICATION",
  "policy_metric_id": "NM_RETAIL_SALES_RPS",
  "ir": {
    "operator": "share_minimum",
    "scope": "regulated_entity_and_compliance_year",
    "target_fraction": 0.50,
    "year": 2030,
    "denominator": {"symbol": "NM_retail_sales_MWh", "source": "EXTERNAL_UNBOUND"},
    "numerator": {"symbol": "eligible_retired_REC_MWh_equivalent", "source": "EXTERNAL_UNBOUND"},
    "depends_on_provisions": ["17.9.571.8(A)", "17.9.571.8(F)(2)", "17.9.571.11"]
  },
  "compilation_target": ["EXTERNAL_ACCOUNTING", "LINOPY_CUSTOM_CONSTRAINT"],
  "model_profile_id": "UNSET",
  "missing_dependencies": ["RETAIL_SALES", "ENTITY_MAP", "REC_LEDGER", "RESOURCE_ELIGIBILITY"],
  "compile_readiness": "BLOCKED_INPUT",
  "validation_status": "NOT_RUN",
  "legal_equivalence": null,
  "annotation_status": "AI_DRAFT",
  "gold_eligible": false
}
```

The IR intentionally contains **no executable Python**. `LINOPY_CUSTOM_CONSTRAINT` is a *potential* integration path only after verifying every binding and accounting decision. This is a design specification, not an implemented PyPSA compiler or executed test.

## 5. Quality labels, independent blinded review, and gold-standard freeze

| Field | Allowed values | Application |
|---|---|---|
| `annotation_status` | `AI_DRAFT`, `READY_FOR_BLIND_REVIEW`, `A_COMPLETE`, `B_COMPLETE`, `DISAGREEMENT`, `ADJUDICATED`, `BLOCKED_SOURCE_AMBIGUITY` | `ADJUDICATED` requires actual independent human A/B review and a real resolution |
| `reviewer_a_id`, `reviewer_b_id` | Two distinct real reviewer identifiers | AI may not impersonate two independent reviewers |
| `review_a_labels`, `review_b_labels` | Complete separately entered legal and evidence labels | Review independently without seeing the AI draft or the other reviewer's answers |
| `adjudicator_id` | Actual adjudicator identifier | Must document why an interpretation was accepted or rejected |
| `disagreement_type` | `NONE`, `SPAN`, `ENTITY`, `METRIC`, `DATE`, `MODALITY`, `CONDITION`, `REC`, `COMPILATION`, `OTHER` | May be multiselect; record specific disagreements |
| `confidence` | `HIGH`, `MEDIUM`, `LOW` | Triage only; not a calibrated probability or substitute for adjudication |
| `gold_eligible` | `true`, `false` | Requires source validation, independent reviewers, adjudication, evidence, and persisted provenance |
| `split_group_id` | Regulatory document/instrument/amendment-family identifier | Keep near duplicates and related provisions together across train/test partitions to prevent leakage |

**Blinded workflow:** (1) Export source evidence without `AI建议_非人工` or AI opinions and without the other annotator's answers. (2) Reviewers A/B independently label legal meaning and evidence. (3) Record disagreements. (4) A genuine adjudicator resolves them against the source. (5) A separate compilation review evaluates executability against a documented model profile. (6) Freeze versions and held-out groups before model evaluation. The researcher's earlier verification that the frozen text matches the source allows `source_verification=MATCHED`, **not** `annotation_status=ADJUDICATED`.

## 6. Worked annotation examples (all are AI-authored instructional examples, **not human gold**)

| Provision | Atomic proposition / key field | Semantic type | Compilation role | Critical considerations |
|---|---|---|---|---|
| **8(A)** | Distribution cooperatives demonstrate RPS compliance by retiring RECs; **no standalone percentage denominator** | ACCOUNTING | ACCOUNTING_CONSTRAINT | Legacy NM25-007 requires `denominator=null` |
| **8(B)** | 40% of New Mexico retail electricity sales, target date 2025-01-01 | TARGET | PARAMETER + ACCOUNTING_CONSTRAINT | Cross-reference G&T supply responsibility under 8(F)(2); local generator dispatch is different |
| **8(C)** | 50% of New Mexico retail electricity sales, target date 2030-01-01 | TARGET | PARAMETER + ACCOUNTING_CONSTRAINT | Preserve retail sales and REC compliance accounting |
| **8(D)** | 80% target at 2050-01-01, subject to **three jointly required conditions** | CONDITIONAL_TARGET | PARAMETER + CONDITIONAL_LOGIC | Do not hard-code an unconditional 80% requirement |
| **8(F)(1)** | G&T cooperative assigns **renewable energy** to member distribution cooperatives | RESPONSIBILITY | ENTITY_MAPPING + ACCOUNTING_CONSTRAINT | Do not silently change the assigned object to RECs |
| **8(F)(3)** | A verification/responsibility statement in passive voice | RESPONSIBILITY | ACCOUNTING_CONSTRAINT | “Verified by G&T” would be an inference unless independently evidenced |
| **9(A)** | Conditional 100% zero-carbon electricity for NM retail customers by 2050 | CONDITIONAL_TARGET | PARAMETER + CONDITIONAL_LOGIC | **Zero-carbon is not identical to renewable**; do not merge the 80% and 100% rules |
| **10(A)** | Cooperative determines a reasonable-cost threshold annually; 60 USD/MWh benchmark with the prescribed post-2020 inflation adjustment | COST_EXCEPTION | COST_EXCEPTION_LOGIC + PARAMETER | Dedicated monetary field; `numerator=null`, `denominator=null` |
| **10(B)** | Cooperative may voluntarily incur costs exceeding the reasonable-cost threshold | PERMISSION | CONDITIONAL_LOGIC | MAY is not MUST |
| **§11** | REC ownership, contractual transfers, banking, and tracking should be split into separate propositions | ACCOUNTING / ELIGIBILITY | ACCOUNTING_CONSTRAINT / ELIGIBILITY_RULE | Flag possible §11(D)/(H) references to §13 with `CROSS_REFERENCE_MISMATCH` |
| **13(A)** | File an annual report by April 30 addressing the preceding calendar year | REPORTING | REPORTING_ONLY | `date_role=ANNUAL_FILING_DUE`, not an RPS achievement date |

**Terminology:** Use **distribution cooperative**, never the Chinese mistranslation “分配合作社.” The legal RPS denominator relates to NM retail sales; do not substitute `electric_energy_supply_portfolio` or local generation without an explicit supported interpretation.

## 7. Example JSON record (draft, not gold)

```json
{
  "annotation_id": "NM25-009-TARGET",
  "parent_case_id": "NM25-009",
  "source_id": "NM_COOP_2025",
  "source_sha256": "673f60931b4a2ba68c2de2c67601097bc292da8998536bdb38b3d014acfdea01",
  "provision": "17.9.571.8(C)",
  "legal_semantic_type": "TARGET",
  "normative_force": "MUST",
  "obligated_entity": "distribution_cooperative",
  "target_fraction": 0.50,
  "target_date": "2030-01-01",
  "date_role": "DEADLINE",
  "numerator_metric": "ELIGIBLE_RENEWABLE_ENERGY_MWH",
  "denominator_metric": "NM_TOTAL_RETAIL_SALES_MWH",
  "rec_accounting": ["RETIREMENT"],
  "depends_on_provisions": ["17.9.571.8(A)", "17.9.571.8(F)(2)", "17.9.571.11"],
  "compilation_roles": ["PARAMETER", "ACCOUNTING_CONSTRAINT", "ENTITY_MAPPING"],
  "model_profile_id": "UNSET",
  "executability": "UNASSESSED",
  "legal_equivalence": null,
  "annotation_origin": "AI_SUGGESTION",
  "annotation_status": "AI_DRAFT",
  "gold_eligible": false
}
```

**Example caveats:** The numerator metric is a proposed normalized semantic representation, and dependency references are suggestions requiring source review. Neither has yet been independently adjudicated. Derive `start_char`, `end_char`, and `exact_text` from the frozen source, not by guessing offsets.

## 8. Workbook mapping and current implementation compatibility

- **Existing `政策标注主表` (14 tasks):** Columns A–P hold draft evidence and fields; Q–AB are reserved for real human review and adjudication, and must remain blank until performed.
- **Existing `AI建议_非人工` sheet:** Keep for draft analysis only; **exclude it from blinded annotation inputs**.
- **Existing `PyPSA编译映射` sheet:** Align to `legal_semantic_type`, `compilation_roles`, and `executability`. A previous `NOT_DIRECTLY_EXECUTABLE` label means “not an independent optimization constraint,” **not** “legally incorrect.”
- **Existing `新增条款待审_9_11_13` sheet (12 preliminary tasks):** These are section/subsection topics. Break them into atomic propositions and establish exact evidence offsets before human annotation.
- **Suggested additional tables:** `Atomic_Obligations`, `Evidence_Spans`, `Blind_Reviewer_A`, `Blind_Reviewer_B`, `Adjudication`, `Model_Profiles`, `Compiler_Decisions`, `Codebook_Version`.
- **Python compatibility:** Current `src/energy_policy_llm/schema.py` implements only a compact `PolicyTarget` dataclass; `compiler.py` implements a limited generation-share semantic gate. **The repository does not yet implement every codebook field or an operational PyPSA/REC compliance engine.** This document is a proposed annotation specification, not a claim that a complete runtime schema exists.

## 9. Annotation acceptance criteria

1. **Source integrity:** Every record has a frozen source, hash, precise subsection, verifiable evidence text, and reproducible offsets.
2. **Atomicity:** Do not combine independent duties into one training case; preserve qualifications and dependencies.
3. **Field coverage:** Capture regulated actors, normative modality, actions, units, temporal roles, and relevant REC, cost, and conditional requirements.
4. **Faithful normalization:** Never silently convert renewable to zero-carbon, retail sales to generation, or assigned energy to assigned REC.
5. **Reviewer independence:** Separate AI drafts from two real human reviewers and subsequent adjudication.
6. **Model-dependent decisions:** Tie each compilation outcome to a named model profile, variables, data sources, units, period, and execution mode.
7. **Explained abstention:** Use `UNKNOWN`/null with documented rationale for unsupported or ambiguous information; do not force legal-equivalent compilation.
8. **Reproducible versions:** Record codebook version, reviewer IDs, dates, change log, and grouped train/test split assignments.

## 10. Version control and change management

Version v1.1 extends v1.0 with a two-track conventional review and PyPSA compilation protocol, a required input contract, typed IR, and pre-solve/post-solve acceptance gates. This document defines labels and procedures only. If subsequent research reveals that the schema cannot faithfully represent a legal clause in 17.9.571, release an updated codebook and explicit migration guidance; **never silently revise adjudicated labels**. Prioritize pilot reliability testing on 8(F) responsibilities, 9(A) conditional applicability, 10(A) cost exceptions, and the apparent 11(D)/(H) source cross-reference ambiguity. All examples remain non-gold until independent human adjudication.
