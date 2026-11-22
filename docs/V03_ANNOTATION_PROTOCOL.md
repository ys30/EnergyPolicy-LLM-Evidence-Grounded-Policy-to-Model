# v0.3 — Source-grounded annotation protocol (2026-11-22)

**Implemented:** exact-span validator, SHA-256 UTF-8 snapshot integrity check, independent annotator/adjudicator gate, and offline annotation queue generator. **Not implemented:** licensed document crawler, actual stored statutory snapshots, adjudicated gold corpus, LLM evaluation, or PyPSA simulation.

## Scope correction: identify the legal entity and denominator
- CA CPUC retail sellers: California Public Utilities Code §399.15(b); 60% by 2030. Separately, local publicly owned utilities are regulated under §399.30; do not silently collapse them.
- NM public utilities: 17.9.572.10(B)(4) NMAC; 50% no later than January 1, 2030.
- NM distribution co-ops: 17.9.571.8 NMAC; 50% no later than January 1, 2030. Cooperatives have distinct cost-threshold and supply obligations; do not merge with the public utility case.

Official entry points:
- https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=399.15.&lawCode=PUC
- https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/electric-power-procurement/rps/rps-compliance-rules-and-process/60-percent-rps-procurement-rules
- https://www.srca.nm.gov/parts/title17/17.009.0572.html
- https://www.srca.nm.gov/wp-content/uploads/2025/06/17.9.571.html

These are **source pointers**, not verified verbatim annotations. Preserve actual source version, capture date and an authorized snapshot before computing offsets. Current registry fields are preliminary summaries awaiting independent review.

## Exact-span protocol
1. Capture a legally redistributable plain-text document snapshot outside the repo (or preserve citation/offset metadata without redistributing the content); record the retrieval time, publication version and SHA-256 over UTF-8 bytes.
2. Record start/end **Python character** offsets into the frozen text file (zero based; end exclusive), quoted substring and exact provision; confirm `snapshot[start:end] == quote`.
3. Annotator A and B separately mark entity, goal, numerator, denominator, effective date, eligible technologies, accounting method, exceptions, and ambiguity. Keep amendments in the same split.
4. Adjudicate all mismatches and write adjudicator ID. Only `adjudicated` records with two different annotator IDs count as gold. The code enforces a minimum integrity gate, but does not substitute for human legal interpretation.
5. Freeze a holdout split by policy instrument/jurisdiction **before** prompting models.
6. Compare regex, structured LLM, retrieved-context LLM, evidence-bound validated LLM. Score against adjudicated clauses; report provenance, cost, model IDs, prompts, accuracy and abstention.

## Commands
```bash
python scripts/create_annotation_queue.py
python scripts/validate_evidence_registry.py
python -m unittest discover -s tests -v
```

The review queue includes 3 work items, zero gold annotations. Do not claim 50 annotated clauses or model evaluation until actually completed.

## Next checkpoint
Capture source texts and annotate 10–15 short governing/exception clauses as a pilot; assess inter-annotator agreement and the legal semantics schema. Later scale to 50+ adjudicated clauses and frozen benchmarking.
