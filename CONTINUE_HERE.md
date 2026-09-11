# Continue here — reversal / mean-reversion research

## Current state: actual ETF data delivered and independently replayed in cloud

Data/computation acceptance:

`PUBLIC_CSV_DELIVERY_VERIFIED_SECONDARY_RAW_REPLAY_REPRODUCED`

Research state remains **`PARTIAL_CARRIER_TRANSPORT`**. Data-delivery acceptance is not an alpha PASS.

User delivery: `9abe7046e50b5eeb6299848eccf6039f7af55647`.
Cloud acceptance run: `34628912555`, job `103360673794` — SUCCESS.

The public pack is `data/r1a_carrier_prices/cloud_pack_v1/`. It contains **12 actual CSVs: 10 annual OHLCV files plus 2 corporate-action tables**, not twelve annual files plus two action files. Total: **583,943 price rows; 39,317,068 CSV bytes**. Each file was read, hash/size/row-checked and reconciled with the original private-export manifest in a fresh GitHub Actions checkout with NO `private/` directory or local DataHub.

There is no outstanding routine local-model data-transfer task for this historical pack. Cloud computations must use the public manifests, not ask the user to resend already delivered files.

## Read first

1. `docs/ops/evidence/r1a_cloud_raw_replay_9abe704/REPORT.md`
2. `docs/ops/evidence/r1a_cloud_raw_replay_9abe704/acceptance_receipt.json`
3. `data/r1a_carrier_prices/cloud_pack_v1/README.md`
4. `docs/governance/R1A_CARRIER_PRICE_TRANSPORT_FREEZE@1.0.json`
5. `PROMPT.md`

Historical stages are preserved: pre-delivery blocker in `r1a_carrier_transport_20260912/`; local replay in `r1a_carrier_transport_20260912_local/`; public-ledger-only audit in `r1a_carrier_cloud_audit_20260912/`; local source audit in `r1a_carrier_source_audit_20260912/`. Do not treat their older availability statements as the current data state.

## Secondary carrier: 588000.SH

The cloud now regenerates ETF returns from the delivered canonical minute OHLCV, not merely from an already calculated return ledger.

- Same **1,791/1,802** complete event/control pairs.
- All seven horizons; **12,537** regenerated return rows.
- Regenerated coverage CSV and return CSV are byte-identical to the retained local files.
- **2,128** nested summary values reconciled; maximum numerical difference in the compared ledgers was zero.

This verifies computational reproduction. It is not a second independent statistical sample, new alpha certification or executable-profitability result. The earlier descriptive return table is unchanged.

## Primary carrier: 512100.SH

The actual data are present. The original data requirements are not satisfied, so primary returns remain **unopened**.

2021 index clock: 58,320 expected minutes; 58,320 present; 0 missing; **3,220 recorded zero-volume**; **55,100 positive-volume**. Positive-volume coverage remains **94.478738% < 95%**. The local audit reports zero deduplication losses for this year; upstream partitions were not re-exported in this cloud acceptance run.

The cloud also evaluated ONLY availability under the existing complete event-and-control 240-bar path rule, without measuring returns:

| Event year | Complete-pair availability |
|---|---:|
| 2021 | 4.8387% |
| 2022 | 39.4822% |
| 2023 | 76.4045% |
| 2024 | 89.0374% |
| 2025 | 98.7952% |
| Pooled | 846/1,296 = 65.2778% |

This also fails the unchanged 80% common-pair gate. Therefore the issue is not merely a 0.52-percentage-point shortfall at the annual gate. Do not lower 95%, drop 2021, fill zero-volume records, choose only shorter horizons or substitute another ETF to force this v1 study through.

Separate missingness exists in 2022: 240 absent index-clock minutes plus 336 recorded zero-volume minutes. The annual/monthly coverage ledger distinguishes those categories rather than calling everything missing data.

## Source interpretation boundary

**Recorded volume=0 is not independently verified exchange no-trade.** The delivered local source audit itself leaves exchange-no-print versus vendor-placeholder semantics UNKNOWN. Its label `TRUE_ZERO_VOLUME_ON_INDEX_CLOCK` means the source rows contain zero, not that every exchange print was independently checked.

Upstream time-label and corporate-action source references/hashes have been delivered in the local source audit. This acceptance independently verifies canonical CSV availability, observed coverage and reproduction; it does not claim to have fetched those upstream source snapshots or re-exported the entire DataHub.

Next work belongs in the cloud using the delivered pack: diagnose these observation/measurement semantics without opening the blocked primary return table. Any later alternative estimand/sampling protocol must be separately justified and frozen, preserving the v1 insufficient-coverage result rather than silently editing it.

## Commands — no local DataHub

```bash
PYTHONPATH=src:. python -m pytest -q tests/test_r1a_*.py
PYTHONPATH=src:. python research/r1a_carrier_transport/verify_cloud_replay.py --output /tmp/r1a-cloud-acceptance-new
```

The acceptance command requires a fresh output directory and no private directory. It replays the delivered v1 pack and tests agreement with the retained local results.

Direct frozen runner:

```bash
PYTHONPATH=src:. python research/r1a_carrier_transport/transport.py \
  --manifest-dir data/r1a_carrier_prices/cloud_pack_v1 \
  --output /tmp/r1a-public-replay-new
```

Exit code 2 is expected for PARTIAL_CARRIER_TRANSPORT, not an engineering crash or alpha rejection. Use new output directories; never overwrite historical receipts.

## Unchanged authority

R1/R2 mechanism certifications remain. R1_A is the lead historical incremental-price research lane; R1_B does not acquire distinct entry alpha merely from its delayed raw returns; R2 direct directional translation remains unsupported. Previous structural, temporal and option identities stay closed.

Fixed maps: `000852.SH -> 512100.SH`, `000688.SH -> 588000.SH`. Original pairs/directions and full `1/5/15/30/60/120/240` index-observation-bar surface remain fixed. Synthetic SHORT and zero-cost price changes are not executable shorting or net profits.

`BLACKBOX_query_count=3`; no query #4; `production_authority=false`; `fresh_oos=false`.
