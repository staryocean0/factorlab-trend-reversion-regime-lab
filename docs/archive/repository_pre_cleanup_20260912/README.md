# FactorLab Trend–Reversion Regime Lab

Current frontier: **fixed-day field reconciliation complete; source-label consumer restricted; intraday synchronization and original minute semantics not certified**.

Read [CONTINUE_HERE.md](CONTINUE_HERE.md) and [fixed-day reconciliation](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md).

Six2025-12-01 source Parquet files are already cloud-verified. Further accounting completed9798 quote events and1928 legacy-minute boundary scenarios. Day-end quantities agree, but many same-label intraday cumulative quantities do not; the four fixed minute conventions do not fully reproduce oldOHLC. No fitted time shift, guessed quantity conversion or source-data overwrite was used.

[Restricted consumer contract](docs/governance/ETF_SOURCE_LABEL_CONSUMER_V1_20260912.json) prevents reversed-terminal and cross-phase intervals from being used. This is a read-only local consumer restriction, not a repaired upstream DataHub product or real-time execution authority.

No further local transfer is currently requested. This finite audit is finished; no automatic date expansion, acquisition, returns or NAV-premium experiment follows. New studies must explicitly qualify their source assumptions.

R1_A remains an unconfirmed reserved lead with active development paused. The prior known512100 action correction did not change published cohorts or means. All historical sources, freezes, results and failures are retained.

`BLACKBOX_query_count=3`, `production_authority=false`, `fresh_oos=false`. Reproducibility is not strategy certification.
