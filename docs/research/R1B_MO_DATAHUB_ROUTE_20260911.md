# R1_B MO — DataHub source route — 2026-09-11

Research identity: `rmr_R1B_MO_convex_impulse_mapping_v1`

## What DataHub provides

Pinned product for MO executable L1 research:

| Field | Value |
|---|---|
| product_id | `cffex_index_option_trade_activity_3s` |
| dataset_version | `derivative_trade_activity_cn_cffex_3s_20191223_20260825_v5_20260830` |
| MO coverage | 2022-07-22 .. 2026-08-25 |
| bid/ask | `bid_price_1`, `ask_price_1`, `bid_volume_1`, `ask_volume_1` |
| source filter | `source_kind=baidu_cffex_500ms_derived_trade_activity_3s` only |
| contract master | `derivative_contract_identity_cn_cffex_index_option_20191223_20260825_v2_20260826` |

Machine binding: `docs/governance/R1B_MO_DATAHUB_SOURCE_BINDING_v1.json`

Field mapping: `docs/governance/R1B_MO_DATAHUB_TRADE_ACTIVITY_MAPPING_v1.json`

Adapter: `research/r1b_mo_data_admission/adapt_datahub_mo_trade_activity.py`

Export helper: `research/r1b_mo_data_admission/export_datahub_mo_month.py`

## What this is not

- Not a CIIS/CFFEX Level-2 snapshot byte delivery.
- Not a substitute for the CIIS two physical delivery epochs; DataHub uses its own pinned dataset_version lineage.
- Not admission PASS by itself; fee contract and full validator manifest remain required.
- Not production authority.

Under `R1B_MO_DATA_ADMISSION_PROTOCOL_V1.json`, this is **source priority rank 2**: licensed vendor feed with documented lineage and L1 bid/ask.

## Relationship to 000852 index data

DataHub/FACTORLAB index bars for `000852.SH` continue to serve R1_B event timing and direction only. MO trade-activity is the separate instrument quote surface for premium execution.

## Remaining blockers after DataHub wiring

1. Tail gap: pinned source ends **2026-08-25**, not frozen window end **2026-09-10**.
2. Fee contract: broker/customer historical commission still unresolved.
3. Full admission manifest over complete MO history not yet materialized in-repo (lake stays external; repo holds binding + adapter + bounded evidence exports).

`BLACKBOX_query_count=3`
