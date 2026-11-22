# Research protocol v0.1 — 2026-11-22

## Working paper title
**When Policy Language Becomes Model Constraints: Evaluating Semantic Fidelity and Error Propagation in LLM-Assisted Power-System Analysis**

## Core distinction
A retail-sales RPS obligation involving eligible credits is not directly equivalent to a geographic region's generation-share constraint. Such mapping requires a documented accounting bridge (sales, imports/exports, REC retirements, eligible technologies, ownership and compliance periods), and may still be unidentifiable with public data. The compiler must abstain otherwise.

## RQ / hypotheses
- RQ1: How precisely can extractors identify quantitative thresholds, target dates, obligated entities, technology eligibility, and exceptions from governing policy clauses?
- RQ2: Does typed schema validation with abstention reduce unsafe policy-to-constraint conversions vs naive prompting?
- RQ3: Conditional on explicit scenario assumptions, how does policy-to-model translation error propagate to costs, dispatch and emissions in an independent electricity-system model?

## Proposed experiment
1. Stage 0: two official policy cases, CA 2030 RPS 60%; NM public utility 2030 RPS 50%. Independently check governing text, edition and compliance context.
2. Stage 1: expand to 4–6 Western states and historical legislative versions; do not use unreviewed examples as gold labels.
3. Create clause-level gold annotation with two annotators + adjudication. Annotate null/ambiguous/exception, not merely percentage/date.
4. Freeze test set by policy instrument and jurisdiction; additionally hold out an unseen state.
5. Baselines: regex, zero-shot structured LLM extraction, RAG extraction, evidence-bound extraction + schema validation; same document access across models.
6. Metrics: field-level exact match/F1, legal scope error rate, source span correctness, abstention precision/coverage, compiler validity, end-to-end scenario delta; uncertainty intervals by bootstrapping policies (not clauses as independent units).
7. Test perturbations: incorrect target year, denominator swap, renewable vs zero-carbon eligibility, compliance period, entity exclusions. Report modeled effects and explicit non-equivalence; no claim of *real-world policy effect* from model deltas.
8. After benchmark: integrate with a separate pinned PyPSA model. Document whether retail sales/RECs can actually be modeled; only compile to legal-compliance constraints with verified accounting bridge.

## Early acceptance criteria
- 100% abstention on unsupported retail-sales→generation-share conversions in safety test set.
- At least 50 independently annotated policy clauses before testing LLM accuracy; larger dataset for publication.
- Code+config+document snapshots and citation offsets reproducible, where redistribution permissions allow.
- Never attribute synthetic LP outputs to real grid economics.

## Next implementation tasks
- Build document ingestion with immutable source snapshots, offsets, source timestamps and legal version keys.
- Design PolicyTarget JSON schema with denominator, eligibility, entity, accounting method, target dates, exceptions and evidence spans.
- Implement LLM adapters only after gold set and fixed eval framework; track model/version/temperature.
- Integrate PyPSA through reviewed custom constraints and explicit unit tests on a separately frozen example network.
- Expand cases to CO/AZ only after primary-source review.
