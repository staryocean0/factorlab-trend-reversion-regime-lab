# Trend/reversion research

Read CONTINUE_HERE.md and docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md.

Latest fixed-day quantity/price/minute-boundary accounting is complete. All original sources remain unchanged. No new local retransmission is needed. Six Parquet files, source docs and five-year legacy CSVs are already in the cloud.

Day-end quantity equality does not imply intraday equality: continuous quote cum_volume is above recorded tick sums at the same source label in629/4711 and3508/4740 cases. This is not economic ETF/index lead-lag or a calibrated latency estimate. Do not fit a shift to hide it.

All four declared minute scenarios retained; none fully reproduces old OHLC or is newly certified as vendor truth. Raw-unit quantity mismatch does not certify an error or justify multiplying all old volumes. The13:26 anomaly is not reconstructed; no source prices, volumes or historical results may be overwritten with nearby prints.

RestrictedSourceView is an offline consumer contract, not a DataHub patch or live execution API. Reject reversed/empty/unknown intervals, no future checkpoint/backfill, no cross-phase carry, no fallback to old states after an invalid latest event. Clip only consumer ends at declared phase boundaries. Retain original post-close reversed rows; do not invent an end.

This finite audit has ended. No automatic new fit, bucket search, date expansion,2026 price reading, purchase, returns, NAV premium or strategy promotion. Unproven publication times/units/source completeness remain explicit usage limits. New empirical scope requires its own authorization and assumptions.

R1_A reserved and active development paused. ClosedR1_B/R2/options remain closed. Prior known512100 action correction and zero published-cohort impact complete; cancelled2022-08-03 split must not be applied. Preserve all old source bytes, manifests, freezes and receipts. BLACKBOX_query_count=3; production_authority=false; fresh_oos=false.
