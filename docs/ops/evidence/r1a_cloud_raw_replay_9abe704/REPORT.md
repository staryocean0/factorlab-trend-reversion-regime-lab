# R1_A public CSV delivery — independent cloud replay

Decision: `PUBLIC_CSV_DELIVERY_VERIFIED_SECONDARY_RAW_REPLAY_REPRODUCED`

Delivery commit: `9abe7046e50b5eeb6299848eccf6039f7af55647`

Verified 12 actual CSVs: 10 annual OHLCV and 2 corporate-action tables; 583,943 price rows; 39,317,068 bytes. No private directory or local DataHub was used.

## Reproduction

588000: 1791/1802 complete pairs; all seven horizons regenerated from actual canonical ETF CSVs and original index bytes. 2128 nested summary values reconciled with the local receipt.

| Ledger | Rows | Byte-identical | Max numeric error |
|---|---:|---|---:|
| 588000.SH_coverage.csv | 1802 | True | 0 |
| 588000.SH_transport.csv | 12537 | True | 0 |

## Primary coverage — no return measurement

| Year | Expected | Missing | Recorded zero volume | Positive volume | Valid coverage |
|---|---:|---:|---:|---:|---:|
| 2021 | 58320 | 0 | 3220 | 55100 | 94.478738% |
| 2022 | 58080 | 240 | 336 | 57504 | 99.008264% |
| 2023 | 58080 | 0 | 72 | 58008 | 99.876033% |
| 2024 | 58080 | 0 | 47 | 58033 | 99.919077% |
| 2025 | 58320 | 0 | 2 | 58318 | 99.996571% |

The 2021 95% gate still fails. No primary returns, year removal, zero-volume filling, ETF substitution or gate relaxation occurred.

For data-quality diagnosis only, the existing common 240-bar event-and-control path rule gives:

```json
{
  "frozen_pairs": 1296,
  "complete_pairs": 846,
  "coverage": {
    "pooled": 0.6527777777777778,
    "2021": 0.04838709677419355,
    "2022": 0.3948220064724919,
    "2023": 0.7640449438202247,
    "2024": 0.8903743315508021,
    "2025": 0.9879518072289156
  },
  "reasons": {
    "complete_common_path": 846,
    "event_missing_or_zero_volume_minute;control_missing_or_zero_volume_minute": 232,
    "control_missing_or_zero_volume_minute": 121,
    "event_missing_or_zero_volume_minute": 95,
    "event_corporate_action_crossing;control_corporate_action_crossing": 1,
    "event_corporate_action_crossing": 1
  },
  "minimum_coverage_pass": false
}
```

These availability counts are NOT returns or permission to bypass admission.

## Source boundary

- Zero-volume means the delivered source records volume=0; exchange no-trade versus vendor placeholder is not independently established.
- Delivered canonical OHLCV is now cloud-readable and replayed; upstream dictionary/corporate-action source snapshots remain referenced by the local audit rather than re-downloaded here.

Research state remains `PARTIAL_CARRIER_TRANSPORT`. File-delivery acceptance and computational reproduction do not grant causal, significance, fresh-OOS or trading-profitability claims. `BLACKBOX_query_count=3`; `production_authority=false`.
