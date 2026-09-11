# FactorLab Trend–Reversion Regime Lab

Reversal / mean-reversion research; index price validity and instrument execution are separate layers.

## Current frontier

**`PARTIAL_CARRIER_TRANSPORT`** after local delivery `b656b4b` and cloud public-ledger audit `34624375457`.

| Fixed carrier | Status |
|---|---|
| `588000.SH` / STAR50 | Locally admitted and measured; 1,791/1,802 common event/control pairs. Cloud ledger and original-index comparator audit passed. |
| `512100.SH` / CSI1000 | Local data exported, but 2021 positive-volume minute coverage is 94.478738%, below the frozen 95% gate. Primary outcomes remain unopened. |

All seven observed-index-bar horizons are retained; no signal refit, rematching or chosen holding period. On the secondary carrier, 15/30-bar ETF event means are +3.60/+5.16bp and paired increments +3.02/+3.73bp. These are zero-cost descriptive returns, not executable or independently confirmed alpha. The primary CSI1000 test has not been completed.

The cloud checked 12,537 ledger rows, 2,128 summary fields and index comparisons recomputed from verified index bytes. Raw ETF CSVs remain private/local: this is **not** full raw-ETF cloud reproduction. Source timestamp/deduplication/corporate-action assurance and primary 2021 zero-volume attribution are the exact next audit tasks.

## Read first

- [`CONTINUE_HERE.md`](CONTINUE_HERE.md)
- [`Cloud delivery audit`](docs/ops/evidence/r1a_carrier_cloud_audit_20260912/REPORT.md)
- [`Local transport receipt`](docs/ops/evidence/r1a_carrier_transport_20260912_local/transport_receipt.json)
- [`Frozen carrier contract`](docs/governance/R1A_CARRIER_PRICE_TRANSPORT_FREEZE@1.0.json)

Earlier missing-data receipts and R1/R2/R1_B option evidence are preserved, not overwritten. `PROMPT.md` now resumes from the delivered-data state, not a generic request to acquire the same history again.

`BLACKBOX_query_count=3`; no query #4; `production_authority=false`; `fresh_oos=false`.
