# FactorLab Trend–Reversion Regime Lab

Reversal / mean-reversion research, with price validity kept separate from instrument execution.

## Current frontier

**R1_A ETF price transport: `BLOCKED_CARRIER_DATA_NOT_ADMITTED`.**

The transport contract is frozen and its implementation, 33 synthetic tests, real index-clock checks and source acquisition audit have executed in cloud run `34621777306`. Neither ETF has an admitted 2021-2025 minute-price delivery, so **no ETF returns have been computed and no ETF alpha PASS/FAIL exists**.

| Reference index | Fixed ETF | Unchanged event/control pairs |
|---|---|---:|
| CSI1000 `000852.SH` | `512100.SH` | 1,296 |
| STAR50 `000688.SH` | `588000.SH` | 1,802 |

49,568 frozen index-clock anchor rows are retained. They are timestamps, not ETF prices. The replay keeps the original event AND matched control and all `1/5/15/30/60/120/240` observed-index-bar horizons. No signal refit, control rematching or best holding period is selected.

The next dependency is full non-event-conditioned ETF 1m OHLCV, a source time/adjustment dictionary and complete split/distribution ex-dates. Data request, manifest shape and commands: [`research/r1a_carrier_transport/README.md`](research/r1a_carrier_transport/README.md).

## Scientific lineage

R1 and R2 mechanism certifications remain intact. Prior index diagnostics and matched-parent attribution identify **R1_A / CSI1000** as the lead historical incremental-price-alpha lane. At 15/30 bars the paired increments were +3.85bp/+6.07bp. STAR50 evidence was weaker. R1_B's positive raw delayed returns did not exceed comparable matched-parent controls, and R2 direct directional price response remained unsupported.

These are historical observational findings conditional on the matching design, not proof of causal identification or fresh independent OOS. The selected ETF's related exposure will not constitute independent confirmation. The existing reports and receipts are preserved.

R1_B temporal and option mappings, R2 economic translation and other closed research identities remain closed. Do not use missing ETF data to reopen them.

## Read first

1. [`CONTINUE_HERE.md`](CONTINUE_HERE.md)
2. [`docs/research/R1A_CARRIER_TRANSPORT_STATUS_20260912.md`](docs/research/R1A_CARRIER_TRANSPORT_STATUS_20260912.md)
3. [`docs/governance/R1A_CARRIER_PRICE_TRANSPORT_FREEZE@1.0.json`](docs/governance/R1A_CARRIER_PRICE_TRANSPORT_FREEZE@1.0.json)
4. [`docs/research/R1_INCREMENTAL_ALPHA_PROGRAM_DECISION_20260911.md`](docs/research/R1_INCREMENTAL_ALPHA_PROGRAM_DECISION_20260911.md)

`BLACKBOX_query_count=3`, no query #4, `production_authority=false`, `fresh_oos=false`.

Paid/nonpublic carrier deliveries stay under the Git-ignored `data/r1a_carrier_prices/private/` unless separately authorized for redistribution. Engineering regression success must not be presented as ETF empirical success.
