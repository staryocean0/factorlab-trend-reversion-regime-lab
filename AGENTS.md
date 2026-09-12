# Trend/reversion research

Read CONTINUE_HERE.md and docs/research/ETF_ONE_DAY_CLOUD_REVIEW_20260912.md before acting.

The user's six real 2025-12-01 Parquet files are now independently read and hash/row-verified in the cloud. Do not ask for another clone or upload of this day, the five-year pack or the already-delivered source docs. The prior delivery-pending label is superseded.

Source clock and interval audit is complete, not a trading test. Restricted continuous source-label replay is possible, but all-day event intervals are NOT defect-free: both last post-close rows end at 15:00 before they begin at 15:00:02/03. Raw evidence remains; invalid intervals must not be filled, extended or queried as live states. Existing checks never carry across session phases or backfill future checkpoints.

Trade totals match final quote cumulative quantity in raw units for both ETFs. This does not establish shares/lots or independent completeness. The primary quote grid is 2 seconds offset from the index labels; no optimized shift is authorized. Source-interval coverage and time since state change are NOT exchange synchronization or quote age.

The fixed 512100 13:26 case has zero tick rows in [13:25,13:26) and 22 in [13:26,13:27). Neither bin is automatically the original legacy 1m bucket. No old volume or OHLC repair follows from neighbouring prints. Publication times, actual vendor bytes, units, complete action calendars and nonzero IOPV remain unqualified. All iopv_raw in the day are 0; all exact-PIT flags false.

No new date, 2026 prices, half-life, threshold, lead-lag fitting, return/backtest, purchase or strategy promotion. Further fixed-day quantity/price/bucket reconciliation or upstream terminal contract revision requires bounded explicit scope. No new local data handoff is currently needed.

R1_A remains RESERVED_ACTIVE_DEVELOPMENT_PAUSED. Closed R1_B/R2/options and old failures remain. Known 2022-09-02 action repair and zero impact on published cohorts are already complete; do not repeat them. Full old action completeness=true remains insufficient for new admission. `BLACKBOX_query_count=3`, `production_authority=false`, `fresh_oos=false`.
