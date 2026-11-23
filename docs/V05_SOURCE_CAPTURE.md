# v0.5 primary-source capture and targeted review queue

**Date:** 2026-11-22. Implementation status: repository scripts committed, network capture optional and not claimed to have run. No gold labels and no LLM scores.

## Confirmed public source entry points

New Mexico investor-owned utilities:
https://www.srca.nm.gov/parts/title17/17.009.0572.html
Regulatory scope is 17.9.572.2; retail-sales and REC definitions are in 17.9.572.7; renewable targets are in 17.9.572.10. Version shown by source: February 28, 2023.

New Mexico distribution cooperatives:
https://www.srca.nm.gov/wp-content/uploads/2025/06/17.9.571.html
Regulatory scope is 17.9.571.2; renewable targets and REC retirement are in 17.9.571.8; reasonable cost threshold is 17.9.571.10. Version shown: June 24, 2025.

CA policy reference (source access requires manual review):
https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=399.15.&lawCode=PUC

**Important:** New Mexico's 2025 rule for cooperatives is a different version and different institutional scope from the investor-owned utilities' 2023 rule. Do not collapse records or leak their amendments between train/test splits.

## Local capture
```bash
python -m pip install -e .
python scripts/capture_official_sources.py --case NM_RPS_2030_PUBLIC_UTILITIES
python scripts/capture_official_sources.py --case NM_RPS_2030_DISTRIBUTION_COOPS
python -m unittest discover -s tests -v
```

Snapshots and metadata are saved under ignored `outputs/source_snapshots/`. This is intentionally non-versioned so source redistribution can be reviewed; hashes/metadata may later be registered separately. HTML extraction creates a normalized text view, not guaranteed to preserve legal formatting or all structured elements. Validate citations/offsets manually against the source. Only exact frozen-text offsets can be used by annotation integrity checks.

## Review plan
`data/policies/review_tasks_v05.json` has 12 targeted review tasks for NM. They are **not** 12 annotated clauses or independently adjudicated gold records. Annotators should note any target/effective-date discrepancies and do not force ambiguous cases into legal equivalence.

## Next milestone
Obtain human-reviewed examples with two independent annotators, then create a model invocation adapter and score output using `benchmark.py` without fixture mode. Never report synthetic fixture results as paper findings.
