# First PyPSA + HiGHS solver integration — synthetic policy-translation contrast

**Scope:** This workflow actually calls `Network.optimize(solver_name="highs")` twice when the optional integration GitHub Action passes. This is not a legal compliance solver, not a real-world scenario, and not an LLM extraction accuracy experiment.

## Design

- **Network:** One bus, one fixed 25-MW load over four 1-hour steps (100 MWh); no import/export, transmission congestion, storage or chronological annual variability.
- **Generators:** Fixed 25-MW synthetic renewable (marginal cost 40 arbitrary USD/MWh) and fixed 25-MW synthetic fossil (10 USD/MWh). Both are dispatchable in the toy network, so renewable intermittency is deliberately **not** modeled.
- **Baseline:** No renewable generation-share restriction. PyPSA minimizes dispatch cost.
- **Erroneous policy proxy:** Add a linopy custom constraint via `extra_functionality` requiring renewable dispatch >= 50 MWh. This is a **local generation proxy**, not an RPS retail-sales + REC constraint.
- **Independent REC ledger:** Synthetic retail sales = 100 MWh. The 50% hypothetical target requires 50 MWh eligible retired credits; 30+15 = 45 MWh are retired and eligible, while another 20-MWh synthetic certificate is not retired. **Illustrative shortage: 5 MWh**, independent of the solved dispatch. These certificates are not issued from the solved generators; this is an intentional independence test, not full power-certificate coupling.

## Testable predictions (not verified results until integration CI completes)

| Outcome | No proxy | Generation proxy |
|---|---:|---:|
| Renewable dispatch (MWh) | 0 | 50 |
| Fossil dispatch (MWh) | 100 | 50 |
| Local renewable generation share | 0% | 50% |
| Synthetic dispatch objective | 1,000 | 2,500 |
| Synthetic REC shortfall (MWh) | 5 | 5 |
| Legal compliance established | No | No |

The above numbers are **analytically expected fixture values**, not empirical findings or executed results unless the GitHub Actions log and produced artifact independently confirm the solver completed. Costs reflect only toy dispatch, not investment.

## Reproduction

```bash
python -m pip install -e .
python -m pip install 'pypsa==1.4.0' 'highspy>=1.11,<2'
python -m unittest tests.test_pypsa_synthetic_experiment -v
python scripts/run_pypsa_synthetic_experiment.py
```

CI: [pypsa-synthetic-integration workflow](../.github/workflows/pypsa-synthetic-integration.yml). It runs the PyPSA tests and archives `outputs/pypsa_synthetic/experiment_results.json` only if successful. Normal repository tests skip optional PyPSA integration when PyPSA/HiGHS are absent.

## Boundaries and next research requirements

This initial PyPSA adapter does not implement `LEGAL_CONSTRAINT`, certificate issuance/trading/retirement within optimization, annual weighted chronological datasets, realistic generator availability, co-op/G&T responsibility, or the 2050 conditional targets. To approach meaningful scientific results:

1. Add weather-dependent dispatch and time weighting across model years.
2. Build a separate REC issuance/transfer/retirement ledger with serial uniqueness and eligible resource metadata; reconcile with electricity simulation without treating MWh generation as a legal credit automatically.
3. Use independent retail-sales denominators and actual utility-to-network mappings.
4. Freeze codebook gold and test code generation failures and abstention separately from solver optimization outputs.
5. Compare multiple controlled semantic-error types, not only one generation-share proxy.
