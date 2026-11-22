# V0.2 Protocol: evidence-based policy records and controlled abstention

**Date:** 2026-11-22. **Status:** pre-annotation; the three provisional records are NOT gold labels or a legal-compliance assessment.

## Evidence chain

`regulation URL + legal version + provision + source timestamp -> exact evidence span -> annotated entities/denominator/target -> typed policy obligation -> compiler decision -> model scenario`

This version includes the registry and fail-closed compiler extension; **exact official excerpts, offset-preserving document snapshots, adjudicated labels, LLM benchmarking and PyPSA integration are future steps**.

## Official policy discovery
- CA: [CPUC RPS](https://www.cpuc.ca.gov/rps); [Public Utilities Code 399.15](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=399.15.&lawCode=PUC). Initial target: 60% by 2030 for RPS-covered retail sales.
- NM public utilities: [New Mexico administrative rule 17.9.572](https://www.srca.nm.gov/parts/title17/17.009.0572.html). Initial target: 50% by January 1, 2030, retail sales to NM customers.
- NM distribution co-ops: [New Mexico administrative rule 17.9.571](https://www.srca.nm.gov/wp-content/uploads/2025/06/17.9.571.html). Distinct regulated entity class, separate case.
- **No legal equivalence** between these compliance schemes and local modeled generation shares; eligible procurement and renewable certificates can matter.

## Human label schema to build
`document_id, retrieval_timestamp, version_as_of, provision_id, start_char, end_char, exact_text, entity_scope, numerator, denominator, accounting_scope, target_value, target_date, exemptions, annotator_1, annotator_2, adjudication, source_hash`.

Do not store a clause as verified until the snippet, legal version, and governing source are recorded; current case descriptions are deliberately short paraphrases.

## Leakage-resistant experiment
Split by *policy document or instrument*, not by random paragraphs. Reserve a held-out jurisdiction. Keep policy versions and amended acts in the same split when evaluating generalization. Compare regex baseline, direct structured LLM, retrieval-augmented LLM, and evidence+schema-validated LLM with exactly matched document access. Record model IDs and prompts.

## Metrics
- Field-level precision/recall/F1 and exact match for target, date, denominator and obligated entity.
- Citation span precision (source offsets) and legal-evidence support.
- Compiler unsafe acceptance rate and abstention coverage.
- Scenario impact sensitivity: 2030 vs 2040, retail denominator vs modeled generation, eligible technology and certificate accounting.
- Bootstrap policies as clusters; report confidence intervals and annotator agreement.

## Execution
```bash
python scripts/validate_evidence_registry.py
python -m unittest discover -s tests -v
```
Existing `toy_lp.py` is synthetic and intentionally separate from real grid economics.
