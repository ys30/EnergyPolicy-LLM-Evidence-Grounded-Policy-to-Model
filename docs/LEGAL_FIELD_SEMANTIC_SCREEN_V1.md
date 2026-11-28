# Legal field semantics screen v1 — evidence is not entailment

**2026-11-28.** Implemented a conservative and explicit semantic-risk screening step after exact source-span checks but **before** creating AI-draft `PolicyIR`.

This module is **not** a trained natural-language inference (NLI) model, legal semantic verifier, or legal decision-maker. It checks narrow, testable warning patterns; absence of warnings does not establish that a field is legally supported.

## Implementation

- [`field_semantic_screen.py`](../src/energy_policy_llm/field_semantic_screen.py) compares the proposed legal field against the exact field-level citation text.
- [`rag_policy_bridge.py`](../src/energy_policy_llm/rag_policy_bridge.py) runs these checks **after** verifying the original frozen source SHA-256, retrieved chunk membership and precise evidence range.
- When a risk flag is raised, the bridge returns `ABSTAIN` and **does not create a PolicyIR**.
- When no risk flag is raised, the bridge returns `EVIDENCE_MATCHED_AI_DRAFT_NEEDS_SEMANTIC_REVIEW` with `evidence_verified=False` and `human_adjudicated=False`. Strict Compiler v2 still abstains.

## Screened error patterns (closed-vocabulary pilot)

| Check | Example of unsafe draft | Result |
|---|---|---|
| `ENTITY_SUPPORT_NOT_VISIBLE` | `entity_id=distribution_cooperative` but quoted evidence only states “New Mexico” | Mark for reviewer; do not infer actor from location |
| `FRACTION_QUOTE_MISMATCH` | Extracted `0.50` but citation says “forty percent” | Reject draft mapping |
| `YEAR_QUOTE_MISMATCH` | Extracted 2030 but cited year is 2050 | Reject |
| `RETAIL_DENOMINATOR_NOT_SUPPORTED` | Retail-sales RPS claim citing only “local generation” | Reject shortcut |
| `GENERATION_RETAIL_CONFLATION` | Claims retail-sales metric but cites generation-share terminology | Reject shortcut |
| `CONDITION_SUPPORT_NOT_VISIBLE` | 2050 three-condition target cites reliability + affordability but omits feasibility | Require complete condition evidence |
| `SUSPECT_CROSS_REFERENCE` | 17.9.571.11 references 17.9.571.13(E) | Preserve original, flag for source ambiguity review |

**Important limitations:** A legal actor can legitimately be supplied by a separate definitional/obligation subsection, so these are *review flags*, not conclusive contradiction diagnoses. The fixed English phrase patterns may miss paraphrases, numeric variants or multi-evidence citations. They do not adjudicate the legal semantics of REC retirement, statutory exceptions, eligibility, delegation, or G&T responsibility. The source provenance test is technical and does not prove the legal claims.

## Reproduction

```bash
python -m pip install -e .
python -m unittest tests.test_field_semantic_screen tests.test_rag_policy_bridge -v
python -m unittest discover -s tests -v
```

All data in the tests are **synthetic teaching fixtures**. Human Gold = **0**. A real NLI/LLM verification benchmark requires independent field-level human support / refutation labels, claim-evidence pairs, and policy-family holdout splits. Do not report accuracy, recall, selective risk or false-positive rates as empirical findings yet.

## Next research checkpoint

Create a human annotation task with `SUPPORTED`, `CONTRADICTED`, `INSUFFICIENT_CONTEXT`, `SOURCE_AMBIGUITY` labels for each *claim + set of complete supporting passages*. Distinguish positive field verification from unsupported but literally matching quotes. Extend the schema to support multiple evidence passages per field, legal applicability logic and provenance to the exact source version. The claim-level human Gold annotations should precede evaluation of a genuine NLI model.
