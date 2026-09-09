# R5-B1 limited diagnostic protocol

Date: 2026-09-10

Research identity: `R5_multiscale_serial_dependence_state_v1 / B1 limited diagnostic`

Status: **RESULTS-BLIND DIAGNOSTIC RULE FROZEN BEFORE EXECUTION**

## Authority and provenance

This is the single limited TRAIN/VALIDATION diagnostic authorized by the 2026-09-08 cloud review of R5-B1. It does not reopen R5-A, R5-B2, or R5-C and does not authorize BLACKBOX, PnL, trading, production, or parameter search.

The frozen R5 construction remains unchanged:

- symbol: `000852.SH`
- TRAIN: `2015-01-05..2018-12-31`
- VALIDATION: `2019-01-01..2020-12-31`
- native 5m close-to-close log returns, exact same-day 5-minute transitions only
- causal volatility scale: 240 valid returns, current return excluded
- state window: 960 valid z rows
- short lags: 1,2,3
- long lags: 12..18
- `anti_persistence = -short_memory`
- B0: `next_z ~ 1 + z_t`
- B1: `next_z ~ 1 + z_t + z_t*anti_persistence`
- OLS fit on TRAIN only; parameters applied unchanged to VALIDATION

Frozen source runner provenance:

- historical repository: `staryocean0/factorlab-two-wave-strategy-lab`
- frozen commit: `cf8397c12a9defa243dc272224dedebe6ccd3251`
- runner blob: `cd0ac94f7f8dc4fba7c9ee25701bcca02f551f2a`
- source data SHA256: `bea21fa9dd9532e21605511e07561b33d5569f86f69f5a487507531593b14c48`
- expected source rows: `70114`

Before diagnostic execution, the current repository's yearly `data/market/5m/000852.SH/{2015..2020}.parquet` must be shown row-for-row equivalent on the four required fields (`symbol`, `trading_day`, `close`, `bar_end_shanghai`) to the frozen source data. If that identity check fails, the diagnostic is invalid and must stop before reading diagnostic outcomes.

## Question 1 — breadth across validation days

For every VALIDATION prediction row, with the original frozen TRAIN coefficients:

`gain_i = squared_error_B0_i - squared_error_B1_i`

Aggregate by `trading_day`:

`day_gain = sum(gain_i)`

Positive `day_gain` means B1 improves on B0 for that day.

Report:

- number of validation days
- positive / zero / negative day counts
- positive-day fraction
- total day gain for 2019 and 2020 separately
- concentration of positive gain in the top 10% of positive-gain days
- median and quantiles of day gain

Breadth diagnostic is **supported** iff all are true:

1. pooled B1 gain is positive (sanity continuation of the frozen core result);
2. 2019 total gain > 0 and 2020 total gain > 0;
3. positive-day fraction >= 0.50;
4. the top 10% of positive-gain days contribute <= 50% of total positive gain.

These cutoffs are frozen before this diagnostic is run. No date removal or favorable time/year/sign filter is allowed.

## Question 2 — anti-persistence monotonic shape

Create five anti-persistence bins using **TRAIN-only quintile edges** from rows eligible for the frozen B target. Apply those edges unchanged to VALIDATION.

Within each VALIDATION bin, fit the descriptive empirical relation:

`next_z = alpha_q + slope_q * z_t`

This is a diagnostic shape estimate only; it does not refit B1 and does not replace the frozen TRAIN coefficients.

Report for each quintile:

- frozen TRAIN edge interval
- validation row count
- median anti-persistence
- empirical slope and intercept
- the same slope by 2019 / 2020 as non-gating diagnostics when estimable

Monotonic-shape diagnostic is **supported** iff all are true:

1. the strongest anti-persistence quintile has a more negative empirical slope than the weakest quintile;
2. at least 3 of the 4 adjacent quintile slope steps are non-increasing as anti-persistence strengthens;
3. Spearman rank correlation between quintile median anti-persistence and empirical slope is <= -0.80.

No alternative bin count, edge search, smoothing choice, lag/window change, or selective year/time filter is allowed after results are seen.

## Adjudication

- both diagnostics supported -> `R5_B1_limited_diagnostic_supported_continue_TRAIN_VALIDATION_only`
- otherwise -> `R5_B1_limited_diagnostic_not_supported_close_B1`

Even on support:

- no BLACKBOX allocation is automatic;
- no HMM/rSLDS/Koopman upgrade is authorized by this result alone;
- no PnL/Sharpe or execution mapping is authorized;
- `production_authority=false`.
