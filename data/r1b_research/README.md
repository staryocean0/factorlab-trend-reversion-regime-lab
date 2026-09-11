# R1B research CSV pack

This directory is the in-repo, GitHub-sized CSV pack for cloud execution of the frozen R1B MO study. Cursor / CI can run without the local DataHub lake.

| Path | Content |
|---|---|
| `underlying_1m/000852.SH_1m_YYYY.csv` | CSI1000 1m, 2015-01-05 .. 2025-12-31 |
| `contract_master.csv` | MO identity used for expiry-then-ATM selection |
| `mo_quotes/mo_YYYY-MM.csv` or `mo_YYYY-MM-DD.csv` | Slim L1 bid/ask for 2022-07-22 .. 2025-12-31 |

Columns for quotes: `contract_code,option_type,strike,expiry,timestamp,bid1,bid1_size,ask1,ask1_size,trading_status`.

Files are capped at 80MB so they stay under GitHub's 100MB limit. Larger months are split by calendar day.

2026 MO quotes are omitted: there is no admitted 2026 `000852.SH` 1m series, so those rows cannot form events.

The raw DataHub bundle remains local-only at `data/r1b_mo_admission/datahub/`.
