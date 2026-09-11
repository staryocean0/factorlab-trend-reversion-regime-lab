# FactorLab Trend–Reversion Regime Lab

Reversal / mean-reversion research with mechanism, price validity and instrument execution kept separate.

## Latest: actual ETF CSV delivery accepted and replay reproduced

`PUBLIC_CSV_DELIVERY_VERIFIED_SECONDARY_RAW_REPLAY_REPRODUCED`

User delivery `9abe7046e50b5eeb6299848eccf6039f7af55647` adds the real public `data/r1a_carrier_prices/cloud_pack_v1/`: 10 annual OHLCV CSVs plus 2 action tables, 583,943 price rows, 39,317,068 bytes.

Cloud run **34628912555** verified file bytes/hashes/row counts and independently regenerated 588000's unchanged seven-horizon ETF returns without private/ or local DataHub. Both the 12,537-row return ledger and 1,802-row coverage ledger are byte-identical to local evidence. 2,128 summary values reconcile.

Research status is still **PARTIAL_CARRIER_TRANSPORT**, not alpha PASS:

| Carrier | Data access | Frozen research state |
|---|---|---|
| 588000.SH / STAR50 | Public CSVs verified and replayed | Descriptive secondary transport; 1,791 complete pairs |
| 512100.SH / CSI1000 | Public CSVs verified | Primary outcomes unopened; 2021 positive-volume coverage 94.478738% <95% |

The primary's existing 240-bar complete event/control path rule also yields only 846/1,296 (65.2778%) usable pairs overall, and 4.8387% in 2021. These are availability diagnostics, not returns. No gate was relaxed. Source-recorded zero volume is not independent proof of exchange no-trade.

## Start here

1. [CONTINUE_HERE.md](CONTINUE_HERE.md)
2. [Cloud raw replay report](docs/ops/evidence/r1a_cloud_raw_replay_9abe704/REPORT.md)
3. [Acceptance receipt](docs/ops/evidence/r1a_cloud_raw_replay_9abe704/acceptance_receipt.json)
4. [Frozen transport protocol](docs/governance/R1A_CARRIER_PRICE_TRANSPORT_FREEZE@1.0.json)
5. [Public data pack](data/r1a_carrier_prices/cloud_pack_v1/README.md)

There is no routine local-model transfer task left for this pack. Continue source/measurement diagnosis in cloud, keeping data sufficiency separate from delivery and statistical profitability.

R1/R2 certifications and previous economic/option closeouts are preserved. R1_A remains the historical lead price-alpha lane. Do not refit, rematch, choose a horizon, fill missing/zero-volume observations or reopen closed identities to manufacture a result.

`BLACKBOX_query_count=3`; no query #4; `production_authority=false`; `fresh_oos=false`.
