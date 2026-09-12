# FactorLab Trend–Reversion Regime Lab

Current frontier: **one-day files verified; restricted source-label replay available; terminal interval defect identified; real-time and NAV qualification not granted**.

Read [CONTINUE_HERE.md](CONTINUE_HERE.md) and [one-day cloud review](docs/research/ETF_ONE_DAY_CLOUD_REVIEW_20260912.md).

The six actual Parquet files in `data/etf_microstructure_sample_20251201_v1/` were independently read from the user's fixed delivery commit. 123,307 rows / 3,569,715 bytes, all hashes/row identities checked. No full clone or retransmission is needed.

Source-state checkpoints, stable sequences and restricted continuous label intervals were inspected; raw trade quantity totals equal final quote cumulative quantity for both ETFs. Both final post-close valid intervals are reversed and must not be used as valid intervals. This is a source-product boundary defect, not delivery corruption. Raw files are preserved.

The data support bounded historical source-label checks, not verified exchange receipt-time alignment, nonzero IOPV, complete source history or executable arbitrage. No price-repair return, lead-lag, half-life or threshold experiment was run. No automatic purchase, date expansion or 2026 opening follows.

R1_A remains an unconfirmed reserved lead with active development paused. Known 512100 action omission was separately repaired; published cohorts and means did not change. All old prices, freezes, outcomes and failures remain.

`BLACKBOX_query_count=3`, `production_authority=false`, `fresh_oos=false`. Engineering success is not trading-strategy certification.
