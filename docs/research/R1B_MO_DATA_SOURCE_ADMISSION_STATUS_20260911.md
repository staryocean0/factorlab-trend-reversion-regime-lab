# R1_B MO data-source admission status — 2026-09-11 (updated)

Research identity: `rmr_R1B_MO_convex_impulse_mapping_v1`

Decision: **MO INTRADAY BID/ASK DATA ADMITTED (DataHub primary route)**

Empirical option outcome test authorized: **no**

`BLACKBOX_query_count=3`  
`production_authority=false`

## Admission PASS

| Field | Value |
|---|---|
| Validator receipt | `docs/ops/evidence/r1b_mo_admission_20260911/admission_validator_receipt.json` |
| Materialize receipt | `docs/ops/evidence/r1b_mo_admission_20260911/materialize_receipt.json` |
| Canonical rows | 46,365,986 |
| Monthly files | 50 |
| Window | 2022-07-22 .. 2026-08-25 |
| Local bundle | `data/r1b_mo_admission/datahub/` (gitignored) |

PASS certifies instrument quote admission only. It does **not** authorize event-conditioned option PnL, parameter search, BLACKBOX query #4, or production.

## Source routing

Primary: local pinned DataHub MO L1 trade-activity (`docs/governance/R1B_MO_SOURCE_ROUTING_DECISION_20260911.json`).

CIIS/CFFEX Level-2 order: optional official-provenance supplement only.

## Fee contract

Frozen: RMB **14 / contract / open leg** and RMB **14 / contract / close leg** (`docs/governance/R1B_MO_FEE_CONTRACT@1.0.json`).

## Fixes applied during materialization

1. Canonical timestamps normalized to fixed microsecond width (mixed fractional/non-fractional strings broke batch parsing).
2. Empty DataHub contract-identity expiries filled via MO third-Friday rule.
3. `lunch_or_break` session mapped to `AUCTION_OR_NONCONTINUOUS`.

## Current source state

`DATAHUB_PRIMARY_MO_BID_ASK_ADMITTED_FEE_FROZEN_14_CNY`

## Next step

Pre-execution freeze is now written at `docs/governance/R1B_MO_PRE_EXECUTION_FREEZE@1.0.json`. Wait for a separate user authorization before any event-conditioned MO outcome inspection.

`BLACKBOX_query_count=3`
