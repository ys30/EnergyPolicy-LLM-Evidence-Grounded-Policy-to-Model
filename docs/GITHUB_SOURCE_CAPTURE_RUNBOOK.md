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

## Failure diagnostics (2026-11-23 hotfix)

The run now uploads a separate `NM-official-policy-capture-diagnostics` artifact **on failure** when a manifest exists. Download `capture_manifest.json` and inspect `failures[].phase`:

- `fetch_or_parse`: DNS, SSL, 403/404, timeout, redirect or decoding failure; see `error_type` and `message`. A local DNS failure is not proof of GitHub runner DNS failure.
- `content_validation`: downloaded content was too short or did not include the required section and renewable-law context. This can be an official-site HTML change or an error page.
- `candidate_extraction`: actual source text was downloaded, but candidate extraction returned zero matches. Do **not** treat this as a successful legal corpus: inspect normalization and headings.

The workflow continues to **fail closed**, so failed/partial results do not become gold or usable benchmark scores. It separately attempts both official sources so one failing page does not suppress diagnostics for the other. Check the job log if no diagnostic artifact exists (for example dependency installation or a workflow syntax error before the script runs).

Note: This patch improves failure classification; it does not establish that the initial failed run was caused by any one of these phases, and a successful new run has not yet been observed.
