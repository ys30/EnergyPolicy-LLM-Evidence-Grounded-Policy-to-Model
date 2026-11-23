# Official New Mexico policy corpus — omission and coverage audit (2026-11-23)

## Verified runs
- Initial successful limited extraction: https://github.com/ys30/EnergyPolicy-LLM-Evidence-Grounded-Policy-to-Model/actions/runs/45282578108
- Uncapped extraction: https://github.com/ys30/EnergyPolicy-LLM-Evidence-Grounded-Policy-to-Model/actions/runs/45292178310
- Correct encoding + complete audit: https://github.com/ys30/EnergyPolicy-LLM-Evidence-Grounded-Policy-to-Model/actions/runs/45292580947 (**success**)

## Quantified omission
| Source | Old candidates | Corrected candidates | Previously missed | Cause | Keyword lines outside recognized sections | Keyword lines within sections uncovered |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| NM_IOU_2023 | 200 | 276 | 76 | Silent default extraction cap (200) | 1 (document title) | 0 |
| NM_COOP_2025 | 13 | 167 | 154 | Lossy UTF-8 decoding of legacy Windows-1252 HTML, causing chapter-heading corruption | 1 (document title) | 0 |
| **Total** | **213** | **443** | **230** | Both defects fixed | **2** | **0** |

Original NM_COOP audit showed 155 outside-section keyword lines because only 17.9.571.15 was recognized. After strict UTF-8 decoding with Windows-1252 fallback, sections 17.9.571.1–17.9.571.15 were recognized and the outside count dropped to one document-title line.

### Hashes of the latest normalized text
- NM_IOU_2023: `56a166bfe2114513c9f4e79d2f330d5b700af64d913368637cd7b692894e0274` (51,254 characters)
- NM_COOP_2025: `673f60931b4a2ba68c2de2c67601097bc292da8998536bdb38b3d014acfdea01` (25,245 characters)

**Latest artifact**: [NM-official-policy-corpus-unreviewed](https://github.com/ys30/EnergyPolicy-LLM-Evidence-Grounded-Policy-to-Model/actions/runs/45292580947/artifacts/14874074516). Expires 2026-11-30 23:53 UTC.

## Section/format audit
- NM_COOP: all 15 expected numbered sections from 17.9.571.1 through 17.9.571.15 were matched.
- NM_IOU: 24 section-heading-like matches across numbered sections 17.9.572.1–17.9.572.22, with repeats of 17.9.572.16 and 17.9.572.19, and one 17.9.572.19 match appearing ahead of 17.9.572.18. **These require human review to distinguish duplicate headings from cross-references falsely classified as headings**. The lexical extractor might assign some lines to an incorrect section. Do not treat all provisional citations as verified.
- The one outside-section keyword line per document is the high-level 'PART ... RENEWABLE ENERGY...' title, not an identified missing obligation.

## Important limits
This audit counts **keyword-bearing physical lines**, not independent legal obligations or evidence completeness. Lines without extractor keywords, legal conditions spread across paragraphs, cross-references, tables, exceptions, and version validity can still be missed. 443 records are **unreviewed candidate lines, not Gold Standard clauses**. No manual legal adjudication, model inference or PyPSA simulations occurred in this audit. Gold count remains **zero**.

## Recommended next steps
1. Resolve duplicate and out-of-order IOU section matches by manually viewing their actual headings from the frozen artifact.
2. Review the 230 newly recovered candidate lines, prioritizing 2030/2040/2045/2050 goals, applicable entities, REC accounting, retail-sales denominators, and exceptions.
3. Group contiguous lines into complete legal provisions with surrounding context; two annotators independently review, then adjudicate.
4. After independent validation, use the human-gold set for real model comparison; do not report lexical line counts as recall or accuracy.
