# Continue here — reversal / mean-reversion research

## Latest completed task

**`BOUNDED_SYNTHETIC_METHOD_REVIEW_COMPLETED_NO_CONFIRMATION_AUTHORITY`**

The limited method-only calibration and information-efficiency review has executed. No implementable method clears the complete prespecified synthetic screen; no real R1_A p-value was recalculated and no confirmation sample was opened. R1_A remains an unconfirmed historical lead, not a disproved mechanism.

Read first:

1. `docs/research/R1A_METHOD_CALIBRATION_REVIEW_20260912.md`
2. `docs/ops/evidence/r1a_method_calibration_20260912/REPORT.md`
3. `docs/ops/evidence/r1a_method_calibration_20260912/method_receipt.json`
4. `docs/governance/R1A_METHOD_CALIBRATION_FREEZE@1.0.json`
5. `research/r1a_method_calibration/README.md`

Freeze commit `3032c6567b15c7df705f09101d63ba1caeadd4d1`; decisive code `bd1b4b7fac45bf5075be84a4a666287df4a411b9`; Actions `34662714569`, job `103468357915`: SUCCESS.

## Actual execution scope

Seven stipulated DGPs x 28 fixed layer/carrier/horizon designs x 2,000 replicates =392,000 design datasets in 14,000 jointly simulated replicate universes. Three feasible methods and a nondeployable oracle are fully reported. There are 784 method cells, 84 directly simulated joint-family checks, 336 information-budget rows and 20 multiple-control assumption rows.

The method reader only uses original pair/availability identities, disclosed historical SD/SE values and trading_day columns from five hash-verified 2021-2025 index files. It does not load market OHLC or ETF return ledgers. The decisive checkout excluded ETF outcomes, ETF raw data and new candidate prices. Shared calendar and pair shocks are modeled jointly across layers/horizons; not every possible joint dependence is established.

## Findings

Under imposed AR(0.6) calendar shocks, nominal-5% marginal error across designs is 7.55%-22.65% for the old graph, 2.20%-5.45% for fixed exposure-score HAC6 and 5.20%-7.00% for five-year group t. Under stronger AR(0.9), these become 18.55%-50.30%, 6.15%-19.85% and 9.30%-16.00%.

For the 14-contrast ETF family, AR(0.6) errors are 11.75%/2.40%/1.75%; AR(0.9) errors are 38.60%/10.35%/5.10%. Group t has no severe FAMILY flag but fails marginal safeguards and changes the estimand to equal-year weighting; do not misreport it as failing every joint check. The oracle does well but knows the imposed covariance and cannot be used on real unknown data.

No feasible method passes the complete frozen screen. Finite simulation success would not itself certify market validity anyway. All methods quantified every replicate; none obtained low rejection by hiding failed draws.

Signed event/control loadings with exact reuse behave materially differently from unsigned common-load shocks: old graph size in the signed AR(0.6) case is 4.00%-4.90%. This is a hypothetical cancellation mechanism, not proof of the actual R1_A covariance structure. Do not treat the worst unsigned model as market truth.

## Information efficiency, explicitly conditional

Under the previous normal power/noise assumptions, a 243-day index budget for a true 4bp effect with family14/80% power needs approximately 94.65% (h15) or 98.01% (h30) variance reduction: 18.69x/50.27x information. These are NOT attainable-R-squared claims, forecasts or universal limits.

In the explicit balanced independent event/control noise model, averaging infinitely many independent controls can only halve paired variance (2x information). Correlated controls improve less. This does not establish actual R1_A noise composition and no matching was changed.

## Current decision and next boundary

Do not launch formal confirmation or execution. End this fixed estimator sweep; do not shop more lags, group counts, seeds, model exclusions or real-history p-values. Preserve R1_A as a lead, not a closed mechanism.

If further work is authorized, the bounded scientific question is **Development-only event/control and signed-common-noise decomposition**, not another significance search. Determine which variance components actually dominate and whether a causally available measurement could materially reduce them without changing the intended target. Any changed target or matching rule is a separately disclosed design. That future study has not run or been frozen by this method receipt.

Keep the known 2026 CSI1000 candidate metadata-only until source/exposure qualification and a defensible final design exist. No confirmation clock, automated collection, purchase or live trade has started.

## Available data and preserved history

The actual historical ETF pack remains `data/r1a_carrier_prices/cloud_pack_v1/`; no local DataHub/private dependency or routine transfer request remains. A 2026 CSI1000 file exists in the overnight repository, with known repeat-use metadata and unresolved R1_A exposure. Do not claim no 2026 data exist or that it is fresh holdout.

All old signals, pairs, directions, seven horizons, fixed ETF maps, raw bytes and receipts are preserved. Both endpoint diagnostics remain completed; full-path v1 remains PARTIAL_CARRIER_TRANSPORT under its own definition. The primary failed all-seven-endpoint common-cohort ETF table stays unopened. Source zero-volume semantics and missing-outcome selection remain unresolved by synthetic simulations.

Earlier decisions: `R1A_CONFIRMATION_FEASIBILITY_REVIEW_20260912.md`, `R1A_ENDPOINT_ROBUSTNESS_REVIEW_20260912.md`, and `R1A_ENDPOINT_METHOD_REVIEW_20260912.md` under `docs/research/`. They are historical evidence, not competing latest instructions.

R1/R2 mechanism certification and closed R1_B/R2-directional/MO identities remain unchanged. `BLACKBOX_query_count=3`; no #4; `production_authority=false`; `fresh_oos=false`; `confirmation_protocol_frozen=false`; `confirmation_clock_started=false`; `horizon_selected=false`.

## Reproduce — fresh directory only

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=src:. \
  python research/r1a_method_calibration/study.py --output /tmp/r1a-method-new
PYTHONPATH=src:. python -m pytest -q tests/test_r1a_*.py
```

Regression replays old experiments only to check reproducibility, not to generate new significance claims. No live data-role probe is needed for ordinary tests.
