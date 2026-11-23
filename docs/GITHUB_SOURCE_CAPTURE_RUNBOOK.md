# Obtain official source snapshots using GitHub Actions

This addresses the authoring environment's DNS error by running official-document retrieval from an Ubuntu GitHub Actions runner. It is **not evidence that GitHub successfully downloaded the pages until a run completes**.

## Start
Open [Actions](https://github.com/ys30/EnergyPolicy-LLM-Evidence-Grounded-Policy-to-Model/actions/workflows/capture-official-corpus.yml), select **Run workflow**, choose main, and click **Run workflow**. The workflow also triggers once when the YAML file is first committed.

## Expected artifact
A successful run produces **NM-official-policy-corpus-unreviewed** (retained for seven days) with:
- `NM_IOU_2023.txt` and `NM_COOP_2025.txt` (normalized primary-source text)
- `*.candidates.json` with exact character offsets and snapshot hashes
- `capture_manifest.json` with official URLs, expected version labels, retrieval time, hash, character and candidate counts

## Failure handling
A 403/error page, unexpected short document, missing expected rule section or no candidate matches makes the capture job **fail**. If downloading is denied, fetch the official source manually under the same names and run `python scripts/capture_corpus_ci.py` only after adapting capture input; never replace actual law text with synthetic examples.

## Scientifically necessary next action
The output is **unreviewed**. Use its frozen snapshots to begin independent annotation, then adjudicate at least 10–15 clauses as a pilot. Do not count extracted candidates as gold labels or report LLM accuracy. Inspect normalization around statutory subsections and source dates before annotation. Full texts must not be silently committed to a public repository without source redistribution review.
