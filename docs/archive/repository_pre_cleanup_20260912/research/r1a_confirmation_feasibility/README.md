# R1_A confirmation feasibility

Authority: `docs/governance/R1A_CONFIRMATION_FEASIBILITY_FREEZE@1.0.json`.
Interpretation: `docs/research/R1A_CONFIRMATION_FEASIBILITY_REVIEW_20260912.md`.

This module does conditional sample-size/power planning and synthetic null calibration. It does not confirm alpha, inspect candidate new market prices, or select a trading horizon. All prior evidence stays immutable.

```bash
PYTHONPATH=src:. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/r1a_confirmation_feasibility/study.py --output /tmp/r1a-feasibility-new
PYTHONPATH=src:. python -m pytest -q tests/test_r1a_confirmation_feasibility.py tests/test_r1a_feasibility_retained.py
```

Use a fresh output directory. No private data or DataHub is required. The 2015-2025 index reader hash-checks the old bytes, and prior endpoint ledgers are pinned by receipt hashes. Historical means are centered before noise estimation; the power scenarios use assumed 2/4/6bp, not observed effects. Conditional years are information equivalents, not forecasts or waiting commitments.

The sparse inclusion-exclusion operator is mathematically identical to the previous union-of-exposure-block adjacency quadratic and tested against it. Four declared simulation models test that unchanged approximate estimator; their parameters do not estimate the true market DGP. Simulation can expose failure under an assumption violation, not certify real-market validity.

All 28 index/ETF/index-identity/horizon designs, four variance specifications, 1/7/14/28 comparison families, 80%/90% targets and 60/120/243/486/1215-day budgets remain reported. Choosing a favorable one after the run is not authorized.

A separate bounded metadata inventory command is available for an explicitly requested new inventory:

```bash
PYTHONPATH=src:. python research/r1a_confirmation_feasibility/audit_data_roles.py --output /tmp/r1a-data-role-new
```

It reads repository trees, allowlisted JSON metadata and branch names, not candidate prices or outcome tables. Use only existing authorized GitHub access. Its output is time-dependent and is NOT automatically rerun in regression CI. The historical inventory and the supplementary metadata-only 2026 CSI1000 candidate review remain preserved.

No qualified new confirmation data role, final confirmation protocol, prospective clock or production permission is granted by either command.
