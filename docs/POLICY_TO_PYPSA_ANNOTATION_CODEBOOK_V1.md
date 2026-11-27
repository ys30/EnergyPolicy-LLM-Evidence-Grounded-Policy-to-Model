# Policy-to-PyPSA Annotation Codebook v1.0

**Released:** 2026-11-27 | **Status:** PROPOSED — draft human-annotation protocol, **not** an adjudicated gold standard.

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

This v1.0 defines labels and review procedures only. If subsequent research reveals that the schema cannot faithfully represent a legal clause in 17.9.571, release an updated codebook and explicit migration guidance; **never silently revise adjudicated labels**. Prioritize pilot reliability testing on 8(F) responsibilities, 9(A) conditional applicability, 10(A) cost exceptions, and the apparent 11(D)/(H) source cross-reference ambiguity. All examples remain non-gold until independent human adjudication.
