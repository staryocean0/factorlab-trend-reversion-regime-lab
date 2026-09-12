# R1_A method-only calibration and information accounting

This module compares three feasible procedures and one unavailable known-covariance oracle on **synthetic outcomes**. It never computes a new p-value for the real R1_A return table.

Authority: `docs/governance/R1A_METHOD_CALIBRATION_FREEZE@1.0.json`; baseline `a4b86fc4c0a8a0d8cf18f5d92dac6998b6602e74`.

## Run

```bash
PYTHONPATH=src:. python -m pytest -q tests/test_r1a_method_calibration.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=src:. \
  python research/r1a_method_calibration/study.py --output /tmp/r1a-method-calibration-new
```

A fresh output directory is mandatory. Prior source data, price outcomes and receipts are not changed. Reproduction is not a new method choice or a confirmation observation.

## Exact scope

The data reader uses original R1_A pair identities and endpoint availability, an already disclosed marginal-SD/SE table, and **only trading_day columns** of hash-checked 2021-2025 CSI1000 parquet files. It does not load ETF endpoint-return ledgers or any market OHLC columns, and has no network acquisition code. The one-off Actions job excludes ETF raw files, real return ledgers and 2026 candidates from checkout.

There are 28 fixed layer/carrier/horizon designs, seven stipulated DGPs and 2,000 joint replicates per DGP: 392,000 design datasets but only 14,000 joint replicate universes. Replicates share calendar shocks across carriers and share pair innovations across horizons/layers. They are not 392,000 independent real observations.

The outcome mean is imposed to be zero for size testing, then each of 2/4/6bp is added for model-based positive-detection power. Historical means are not true effects. Simulated missingness is held at inherited eligibility; informative missing outcomes are not identified.

## Procedures and distinct targets

- `GRAPH_T_BASELINE`: exact existing exposure-union graph quadratic and its approximate t calibration.
- `EXPOSURE_SCORE_HAC6`: fixed Bartlett six-block-lag covariance of duplicated exposure scores. It is PSD with an IID floor, but repeated pair membership makes this an adaptation, not a routine Newey-West validity theorem. Longer serial dependence is an explicit stress.
- `FIVE_YEAR_GROUP_T`: compute five group estimates using both-role/year-contained pairs, then an equal-year mean and t[4]. With heterogeneous effects that target differs from the original pair-weighted estimand. Approximate group independence and distribution assumptions must not be asserted from software success.
- `ORACLE_MEAN_NORMAL_REFERENCE`: knows the imposed covariance. It is a diagnostic benchmark, not an estimator available on real data. Its normal interval is exact for the Gaussian models and approximate in the heavy-tail model.

All candidates were specified before this simulation and no lag, group count, seed, sample, DGP or tolerance may be revised because of a disappointing result. The limited screen is a finite simulation screen, never a real-market deployment license.

## Information accounting

`information_budget_NOT_commitment.csv` states the variance reduction that would be needed to meet a fixed 243/486-day planning budget under inherited nuisance scaling. It does not fit a predictive model or establish an attainable R-squared.

`multiple_control_bounds_ASSUMPTIONS.csv` evaluates an explicit equal-event/control-variance model. With independent event/control errors, averaging K controls of pairwise correlation r gives paired variance ratio `[1+r+(1-r)/K]/2`. Independent infinitely many controls only halve noise in this model; correlation weakens that improvement. This is neither a universal bound nor an empirical decomposition of R1_A.

## Outputs

`REPORT.md`, `method_receipt.json`, all 784 DGP/design/method rows, 84 actual joint-family null rows, 336 information-budget rows and 20 multiple-control assumption rows are retained. Invalid estimates and complete-family quantification are reported so abstention cannot masquerade as calibration.

The stopping rule ends this fixed sweep. No routine local data transfer, real R1_A significance search, new matching implementation, 2026 return opening, option study or confirmation clock is authorized.

`BLACKBOX_query_count=3`; `production_authority=false`; `fresh_oos=false`.
