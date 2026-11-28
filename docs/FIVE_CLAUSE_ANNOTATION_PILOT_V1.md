# Five-clause annotation pilot v1 — 2026-11-27

**Status: AI-PREPARED PILOT, NO HUMAN REVIEW OR ADJUDICATED GOLD.** This is a worked application of [Codebook v1.0](POLICY_TO_PYPSA_ANNOTATION_CODEBOOK_V1.md), not a formal model benchmark.

The [machine-readable pilot](../data/policies/nm_coop_five_clause_pilot_v1.json) records five original section-specific evidence intervals against the frozen **NM_COOP_2025.txt** (SHA-256 `673f60931b4a2ba68c2de2c67601097bc292da8998536bdb38b3d014acfdea01`). Intervals were **actually validated** using Python zero-based, end-exclusive slicing of the archived source; the full source text is intentionally not checked into this repository.

| Provision | Frozen source char range | Codebook semantic tag | Preliminary PyPSA decision | Critical finding |
|---|---:|---|---|---|
| 17.9.571.8(B) | [5718, 5903) | TARGET | UNASSESSED | 2025 40% renewable; 8(F)(2) G&T responsibility requires linked interpretation |
| 17.9.571.8(D) | [6094, 6738) | CONDITIONAL_TARGET | ABSTAIN | 2050 80%; technical feasibility AND reliable service AND affordability |
| 17.9.571.9(A) | [7955, 8620) | CONDITIONAL_TARGET | ABSTAIN | 2050 100% zero-carbon is not the same as 80% renewable; same 3 conjunctions |
| 17.9.571.10(A) | [9340, 10143) | COST_EXCEPTION | ABSTAIN | Cooperative annual LCOE decision; USD 60/MWh after-2020 inflation adjustment; excuse does not delay subsequent years |
| 17.9.571.11(D) | [13682, 14081) | ACCOUNTING | ABSTAIN | Mandatory WREGIS registration; literal 17.9.571.13(E)/(B) internal references are suspicious and must **not** be silently corrected |

**Important:** The original 8(B) legal obligation is not directly a local renewable generation-share constraint, and **UNASSESSED** is used because no frozen `model_profile_id` was supplied. Other preliminary ABSTAIN judgments are conservative AI recommendations, not ground-truth compiler outcomes. Absence of sufficient data for a legal-equivalent translation is not failure to extract the legal rule.

## Source-verification procedure

1. Download the verified official corpus artifact from the [successful capture workflow](https://github.com/ys30/EnergyPolicy-LLM-Evidence-Grounded-Policy-to-Model/actions/runs/45443775485).
2. Read `NM_COOP_2025.txt` as Unicode text without changing whitespace or newlines.
3. Confirm UTF-8 byte SHA-256 is the codebook value above.
4. For each JSON row, verify `text[start_char:end_char]` and compare against the printed source excerpt in the locally generated review workbook. The exact five selections were checked against the source during pilot creation.
5. Cross-check legal meaning independently, including exceptions and neighboring subsections. Source offset checks cannot prove semantic correctness.

## Blind review protocol

The downloadable workbook in the conversation is structured with separate sheets `AI建议_5条试标`, `证据原文_5条`, `Reviewer_A_空白`, `Reviewer_B_空白`, `最终裁决_空白`. For **actual blind** review, distribute a reviewer-specific copy with AI suggestions removed/hidden and only evidence plus blank review sheet; do **not** send the full workbook to either blind reviewer. A and B must be separate human reviewers. A real adjudicator resolves substantive disagreements and all source ambiguities, then assigns Gold eligibility.

## Findings needing codebook revision / explicit adjudication

- A `TARGET` with no model profile is **UNASSESSED**, not automatically `LEGAL_CONSTRAINT` or `SCENARIO_PROXY`.
- For `CONDITIONAL_TARGET`, explicitly record `ALL` plus individual conditions; zero-carbon target and renewable target are two separate norms.
- `COST_EXCEPTION` stores threshold amount+unit+inflation basis in cost metadata, never as an RPS ratio numerator or denominator.
- `ACCOUNTING` at .11(D) must preserve both apparent mismatched cross-references and hold compilation pending an authoritative interpretation.
- The five cases deliberately span semantics; they do **not** measure inter-annotator agreement (no human A/B) and do **not** train, fine-tune, run, or benchmark an LLM or PyPSA solver.

**Next technical gate:** define a frozen `model_profile_id` and schema for retail-sales MWh, REC issuance/ownership/tracking/retirement, eligibility, compliance-year, zero-carbon resources, CPI and reliability/affordability inputs, then repeat compiler decisions under that profile.
