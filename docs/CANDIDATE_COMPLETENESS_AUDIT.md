# New Mexico source coverage audit

**Purpose:** enumerate the precise records missed by the old 200-candidate cap, then identify other potential omissions due to line/section matching.

Audit rules:
1. Remove the default 200 candidate cap; retain an explicit optional `limit` for controlled tests.
2. Count candidate records in every matched section and compute exactly `max(0, uncapped_count - 200)`.
3. Independently scan physical lines for the keywords used by the extractor.
4. List keyword-bearing lines **outside any recognized section** (possible missing section headings).
5. List keyword-bearing lines within recognized sections **not covered** by a candidate (e.g., short lines).
6. Show matched legal sections and number of extracted lines per section.

**Interpretation:** zero uncovered keyword lines does **not** establish that every legal requirement was captured: paraphrases using no keywords, HTML normalization, headings not at a line start, multi-line clauses, exceptions and cross-references can all escape lexical extraction. Audit results are unreviewed, not gold labels. The first 200 lines were a hard truncation, and the full number must be computed from the frozen official source rather than guessed.

The GitHub Actions artifact includes `*.audit.json` with findings for the official sources. Relevant subsets must be manually inspected before constructing a legal gold benchmark.

Workflow: [capture-official-corpus.yml](../.github/workflows/capture-official-corpus.yml)
