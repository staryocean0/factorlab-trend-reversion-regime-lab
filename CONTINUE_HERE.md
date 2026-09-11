# Continue here — reversal / mean-reversion bucket

## Authority

This repository owns real reversal / mean-reversion strategy research.

Certified mechanism identities:

- **R1** — `rmr_cross_scale_pullback_parent_integrity_v2`;
- **R2** — `rmr_range_boundary_parent_integrity_v2`.

Reusable BLACKBOX query count is exactly **3**: R1 PASS, R5-C FAIL, R2 PASS. No query #4 is authorized.

`production_authority=false`.

## Closed — do not restart

The following are closed under their frozen definitions:

- R1 immediate index-level economic translation;
- R2 `rmr_R2_range_reentry_economic_translation_v1`;
- unified parent-normal-state router;
- R1_B `rmr_R1B_temporal_impulse_completion_v1`;
- probability threshold/sizing rescue;
- simple horizon/delay/stop/target/cost/scale rescue;
- broad automatic R8/R9 generation;
- R3/R4 and other closed Stage-1 lanes;
- R5-B1 limited diagnostic.

R5-B1 final decision: `R5_B1_limited_diagnostic_not_supported_close_B1`. Its frozen runner/input/result package is archived under `docs/archive/r5_b1_closed_20260910/`.

The key scientific distinction remains: **certified restoration probability is not the same as a certified trading payoff.**

## Current frontier

The only active payoff-object identity is:

`rmr_R1B_MO_convex_impulse_mapping_v1`

Decision:

`R1B_MO_PRE_EXECUTION_FROZEN_OUTCOME_TEST_NOT_AUTHORIZED`

Why: the closed causal linear R1_B payoff retained a delayed positive right tail but failed the preregistered median-net gate. A long directional CSI1000 `MO` option is materially different because it is convex and bounded-loss; an `IM` mapping remains linear and is not promoted as a rescue.

Instrument quotes are admitted and the mapping is now frozen. **No event-conditioned MO option outcome/PnL test is authorized.**

Read:

- `docs/research/R1B_MO_CONVEX_PAYOFF_THEORY_REVIEW_20260910.md`
- `docs/research/R1B_MO_PRE_EXECUTION_FREEZE_20260911.md`
- `docs/governance/R1B_MO_PRE_EXECUTION_FREEZE@1.0.json`
- `docs/archive/rmr_migrated_from_star50_20260909/`

## Data-admission state

MO historical intraday best-bid/best-ask tape is **admitted** on the DataHub primary route. Validator **PASS** receipt: `docs/ops/evidence/r1b_mo_admission_20260911/admission_validator_receipt.json` (**46,365,986** canonical rows, **50** monthly files, window **2022-07-22 .. 2026-08-25**). This admits instrument quotes only; it does **not** authorize option outcomes, BLACKBOX #4, or production.

Confirmed:

- CFFEX Level-2 provides the necessary bid/ask depth, sizes, last price, volume and open interest capability;
- CIIS is a current official distribution route for CFFEX historical Level-2 Snapshot;
- the old `.../sampledata/20221206_Sample_CFF_Snapshot.xlsx` href is still 404, but the current Sample Data page serves the same workbook from `.../uploadfiles/202212/12/2022121215374452718660.xlsx` (SHA-256 `b0aa832d…`, 628,017 bytes, 1,621 MO rows on 2022-12-06);
- current CIIS manual (v4 2026-08-19), order form (v20260820) and `hd@ciis.com.hk` contact route are live;
- a current CIIS manual documents a CFFEX delivery-format transition effective **2024-07-08**.

Therefore the acquisition window is frozen as two physical delivery epochs:

1. `LEGACY_CFFEX_SNAPSHOT`: 2022-07-22 .. 2024-07-07 — **schema mapped on public sample only** (`docs/governance/R1B_MO_LEGACY_CFFEX_SNAPSHOT_MAPPING_v1.json`);
2. `POST_TRANSITION_CFFEX_DELIVERY`: 2024-07-08 .. 2026-09-10 — **still unresolved** (no MO-bearing post-transition sample acquired).

Each epoch requires an independent source-specific mapping and schema/provenance check. One epoch cannot waive unresolved fields in the other; canonical concatenation is forbidden until both pass.

**DataHub primary route (user decision 2026-09-11):**

- product `cffex_index_option_trade_activity_3s`, dataset_version `derivative_trade_activity_cn_cffex_3s_20191223_20260825_v5_20260830`;
- MO L1 bid/ask effective window **2022-07-22 .. 2026-08-25**; user waived the nominal tail to 2026-09-10;
- binding/mapping/routing: `R1B_MO_DATAHUB_SOURCE_BINDING_v1.json`, `R1B_MO_DATAHUB_TRADE_ACTIVITY_MAPPING_v1.json`, `R1B_MO_SOURCE_ROUTING_DECISION_20260911.json`;
- adapter `adapt_datahub_mo_trade_activity.py`; bounded 2022-12 adapt receipt: **328,706** rows at `ADAPTED_NOT_ADMITTED`;
- route doc: `docs/research/R1B_MO_DATAHUB_ROUTE_20260911.md`.

**CIIS/CFFEX official Level-2 order is optional** (`docs/research/R1B_MO_CIIS_ORDER_REQUEST_PACKAGE_20260911.md`) — only for later official byte-layout provenance, not a current blocker.

Current source state:

`DATAHUB_PRIMARY_MO_BID_ASK_ADMITTED_FEE_FROZEN_14_CNY_PRE_EXECUTION_FROZEN`

Session receipt: `docs/ops/evidence/r1b_mo_acquisition_20260911/acquisition_session_receipt.json`.

Order package for the user-only external step: `docs/research/R1B_MO_CIIS_ORDER_REQUEST_PACKAGE_20260911.md`.

Historical dead-link recovery evidence remains under `docs/archive/ciis_public_sample_recovery_20260910/`.

Tracking issue: **#7 — R1B MO: acquire and admit official CIIS/CFFEX Level-2 delivery**.

## Active infrastructure

Governance:

- `docs/governance/R1B_MO_DATA_ADMISSION_PROTOCOL_V1.json`
- `docs/governance/R1B_MO_ADMISSION_MANIFEST_TEMPLATE.json`
- `docs/governance/R1B_MO_DATA_ROLE_FREEZE_20260910.json`
- `docs/governance/R1B_MO_CFFEX_SOURCE_MAPPING_TEMPLATE.json`
- `docs/governance/R1B_MO_LEGACY_CFFEX_SNAPSHOT_MAPPING_v1.json`
- `docs/governance/R1B_MO_DATAHUB_SOURCE_BINDING_v1.json`
- `docs/governance/R1B_MO_DATAHUB_TRADE_ACTIVITY_MAPPING_v1.json`
- `docs/governance/R1B_MO_SOURCE_ROUTING_DECISION_20260911.json`
- `docs/governance/R1B_MO_FEE_CONTRACT@1.0.json`
- `docs/governance/R1B_MO_PRE_EXECUTION_FREEZE@1.0.json`
- `docs/governance/R1B_MO_CIIS_DELIVERY_EPOCH_FREEZE_20260910.json`

Research/source docs:

- `docs/research/R1B_MO_CONVEX_PAYOFF_THEORY_REVIEW_20260910.md`
- `docs/research/R1B_MO_CFFEX_ACQUISITION_SPEC_20260910.md`
- `docs/research/R1B_MO_CIIS_CURRENT_ORDER_ROUTE_20260910.md`
- `docs/research/R1B_MO_CIIS_ORDER_REQUEST_PACKAGE_20260911.md`
- `docs/research/R1B_MO_DATA_SOURCE_ADMISSION_STATUS_20260910.md`
- `docs/research/R1B_MO_FEE_SOURCE_STATUS_20260910.md`
- `docs/research/R1B_MO_DATAHUB_ROUTE_20260911.md`
- `docs/research/R1B_MO_DATA_SOURCE_ADMISSION_STATUS_20260911.md`
- `docs/research/R1B_MO_FEE_SOURCE_STATUS_20260911.md`
- `docs/research/R1B_MO_PRE_EXECUTION_FREEZE_20260911.md`

Code:

- `research/r1b_mo_data_admission/adapt_cffex_snapshot.py`
- `research/r1b_mo_data_admission/adapt_cffex_snapshot_epochs.py`
- `research/r1b_mo_data_admission/prepare_ciis_legacy_cff_snapshot.py`
- `research/r1b_mo_data_admission/adapt_datahub_mo_trade_activity.py`
- `research/r1b_mo_data_admission/export_datahub_mo_month.py`
- `research/r1b_mo_data_admission/materialize_datahub_mo_admission_bundle.py`
- `research/r1b_mo_data_admission/validate_mo_quote_source.py`
- `research/r1b_mo_pre_execution/validate_pre_execution_freeze.py`
- `research/r1b_mo_pre_execution/selection.py`

Tests:

- `tests/test_r1b_mo_data_admission.py`
- `tests/test_r1b_mo_cffex_adapter.py`
- `tests/test_r1b_mo_cffex_epoch_adapter.py`
- `tests/test_r1b_mo_prepare_legacy_cff_snapshot.py`
- `tests/test_r1b_mo_datahub_adapter.py`
- `tests/test_r1b_mo_pre_execution_freeze.py`

Local pytest on 2026-09-11: **24 passed**.

Adapters deliberately fail closed. Successful canonicalization means only `ADAPTED_NOT_ADMITTED` or `MULTI_EPOCH_ADAPTED_NOT_ADMITTED`; it does not create empirical authority.

## Data-role freeze

Frozen before any event-conditioned MO outcome was inspected:

- 2022-07-22 through 2026-09-10: reusable instrument-development evidence;
- from 2026-09-11 onward: prospective instrument-validation evidence only for observations genuinely generated after the freeze, with paired post-freeze underlying data separately admitted.

No BLACKBOX allocation is created by this freeze.

## Fee-contract state

Current state:

`R1B_MO_FEE_CONTRACT_FROZEN_USER_14_CNY_PER_LEG`

User froze all-in MO trading fee at **RMB 14 per contract per open leg** and **RMB 14 per contract per close leg** over **2022-07-22 .. 2026-08-25**. Machine contract: `docs/governance/R1B_MO_FEE_CONTRACT@1.0.json`. Spread is not double-counted in fees.

Historical exchange-only evidence at RMB 15/contract remains archived context in `docs/research/R1B_MO_FEE_SOURCE_STATUS_20260910.md` and is not the active fee authority.

## Exact next authorized action

**Do not run an option return study yet.**

Pre-execution freeze is complete. The next legal step is a **separate user authorization** to run `R1B_MO_ATM_DIRECTIONAL_LONG_SAME_CAUSAL_EXIT` exactly as frozen.

Joinable paired window is **2022-07-22 .. 2025-12-31** because admitted 000852.SH 1m ends 2025-12-31. 2026 MO quotes remain unjoinable until that underlying is separately admitted.

Local quote bundle (not in Git): `data/r1b_mo_admission/datahub/`.

This freeze does not authorize PnL, BLACKBOX #4, or production.

For a local execution agent, use `PROMPT.md` verbatim.

## Bucket boundary

Generic Range/UpTrend/DownTrend state recognition belongs to `factorlab-two-wave-strategy-lab`.
Unsafe/Recovering/HighVol risk-state switching belongs to `factorlab-star50-filter-lab`.

Legacy/mis-scoped/closed evidence is archived under `docs/archive/` and remains in Git history; it is not active authority.
