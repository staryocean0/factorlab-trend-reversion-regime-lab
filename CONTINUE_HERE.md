# Continue here — reversal / mean-reversion bucket

## Current authority

This repository's current job is **real reversal / mean-reversion strategy research**.

Canonical certified mechanism identities:

- **R1** — `rmr_cross_scale_pullback_parent_integrity_v2`: intact trend parent + lower-scale counter-move recovery; BLACKBOX-certified mechanism.
- **R2** — `rmr_range_boundary_parent_integrity_v2`: intact range parent + boundary overshoot / failed acceptance / re-entry; BLACKBOX-certified mechanism.

Reusable BLACKBOX query count remains exactly **3**:

1. R1 PASS;
2. R5-C FAIL;
3. R2 PASS.

No query #4 is authorized.

`production_authority=false`.

## What is already closed — do not restart it

The repository has already tested and closed the following identities/families under their existing definitions:

- R1 immediate index-level economic translation family;
- R2 `rmr_R2_range_reentry_economic_translation_v1`;
- `rmr_unified_parent_normal_state_router_v1`;
- `rmr_R1B_temporal_impulse_completion_v1` on DEV;
- probability-threshold / probability-sizing rescue of certified restoration probabilities;
- simple horizon / delay / stop / target / cost / scale rescue of the closed execution families;
- broad automatic R8/R9 indicator generation;
- R3/R4 and other broad Stage-1 lanes already closed by their frozen reviews.

The important scientific distinction remains:

> certified restoration probability is not the same thing as a certified trading payoff.

## R5-B1 side-line closure — 2026-09-10

The migrated historical R5-B1 lead received its one authorized limited TRAIN/VALIDATION diagnostic using the exact frozen historical input.

Result:

`R5_B1_limited_diagnostic_not_supported_close_B1`

- daily breadth gate: PASS;
- anti-persistence monotonic-shape gate: FAIL (`Spearman = -0.7`, required `<= -0.80`);
- BLACKBOX not read;
- post-2020 rows not read for that diagnostic;
- no PnL/trading mapping.

Read:

- `docs/research/R5_B1_LIMITED_DIAGNOSTIC_RESULT_20260910.md`
- `research/rmr_r5_b1/outputs/limited_diagnostic_receipt.json`

Do not rescue R5-B1 by changing bins, lag windows, dates or thresholds.

## Current frontier — R1_B payoff-object / instrument theory

The authority chain after the certified mechanisms is:

1. R1/R2 index-level economic translations failed detailed validation;
2. unified common router failed detailed validation and was closed;
3. mechanism-to-execution diagnostic found R2 directional markouts worsen with horizon and found only R1_B to have a meaningful delayed positive right-tail component;
4. one causal R1_B S2-impulse-completion exit was tested on DEV and closed because the preregistered median-net gate failed, despite positive mean net and 5/6 positive annual means;
5. payoff-object theory review therefore requires a materially independent payoff/instrument theory before any new empirical economic test.

The current accepted theory identity is:

`rmr_R1B_MO_convex_impulse_mapping_v1`

Decision:

`R1B_MO_CONVEX_PAYOFF_THEORY_ACCEPTED_DATA_ADMISSION_REQUIRED`

Read:

- `docs/research/R1B_MO_CONVEX_PAYOFF_THEORY_REVIEW_20260910.md`
- historical diagnostic/adjudication package under `docs/archive/rmr_migrated_from_star50_20260909/raw/docs/research/`

### Why MO, not IM

A CSI1000 `IM` futures mapping remains linear and would mostly change basis/cost/margin; under the present evidence that is too close to a cost rescue of the closed linear payoff family.

A long directional CSI1000 `MO` option is a materially different convex payoff object and can, in principle, map a right-tail restoration impulse while bounding downside. This is theory only; option premium/theta/volatility/spread can invalidate it.

## Data-admission gate completed — 2026-09-10

The repository has now completed the **admission infrastructure**, not the empirical option test.

Current facts:

- current repository inventory contains no MO historical intraday best-bid/best-ask tape;
- account-wide GitHub code search found no reusable MO `bid1/ask1` tape in another current bucket;
- CFFEX official historical Level-1 / Level-2 data is the preferred acquisition target;
- AKShare/Sina current MO bid/ask interfaces and historical daily data are not a substitute for historical intraday executable quotes;
- Tushare `opt_mins` documents minute OHLC/volume/amount/OI, not historical best bid/ask, so it is not admitted for the primary execution identity.

Frozen files:

- `docs/governance/R1B_MO_DATA_ADMISSION_PROTOCOL_V1.json`
- `docs/governance/R1B_MO_ADMISSION_MANIFEST_TEMPLATE.json`
- `docs/governance/R1B_MO_DATA_ROLE_FREEZE_20260910.json`
- `docs/research/R1B_MO_DATA_SOURCE_ADMISSION_STATUS_20260910.md`
- `research/r1b_mo_data_admission/validate_mo_quote_source.py`
- `tests/test_r1b_mo_data_admission.py`

The admission-gate CI passed on run `34422130207`.

The data-role boundary was frozen **before any event-conditioned MO option outcome was inspected**:

- 2022-07-22 through 2026-09-10: reusable instrument-development evidence only;
- from 2026-09-11 onward: prospective instrument-validation evidence, provided the observation was genuinely generated after the freeze and paired post-freeze underlying data are separately admitted.

This freeze creates no new BLACKBOX allocation.

## Exact next authorized action

**Do not run an option return study yet.**

Acquire a provenance-stable CSI1000 MO intraday quote source and pass it through the frozen admission gate.

Preferred acquisition target:

1. CFFEX official historical Level-1 or Level-2 MO snapshots;
2. alternatively, a licensed vendor feed only if field-level provenance is traceable to CFFEX and the source contract is documented.

Minimum admitted data fields remain:

- contract code, call/put, strike, expiry;
- exchange-local timestamp;
- bid1/ask1 and sizes;
- last price, volume, open interest, trading status;
- stable source/license provenance and checksum inventory;
- historically applicable exchange and broker fee contract frozen before outcomes.

Once files are obtained, populate `R1B_MO_ADMISSION_MANIFEST_TEMPLATE.json` without changing the frozen protocol and run:

`research/r1b_mo_data_admission/validate_mo_quote_source.py`

Only a PASS admission receipt can unlock a separate pre-execution freeze. A PASS still does **not** itself authorize PnL or production.

The primary R1_B option mapping may not substitute midpoint/last price for missing bid/ask after outcomes are seen and may not search strike, expiry/DTE, horizon, probability threshold, timing, stop, target, scale or time-of-day.

## Bucket boundary

Do not restart a generic K-line state recognizer here. Range/up/down causal state recognition belongs to `factorlab-two-wave-strategy-lab`.

Do not restart bottom-layer volatility/risk-state switching here. Unsafe/Recovering/HighVol risk research belongs to `factorlab-star50-filter-lab`.

The `kline-recognizer` v1-v13 research branches in this repository are mis-scoped historical evidence. They remain in Git history but no longer define current authority.

## Read first

1. `CONTINUE_HERE.md`
2. `docs/research/R1_R2_MIGRATION_NOTE_20260909.md`
3. `docs/research/R1B_MO_CONVEX_PAYOFF_THEORY_REVIEW_20260910.md`
4. `docs/research/R1B_MO_DATA_SOURCE_ADMISSION_STATUS_20260910.md`
5. `docs/research/R5_B1_LIMITED_DIAGNOSTIC_RESULT_20260910.md`
6. `docs/DATA.md`
7. `docs/RESEARCH_GOVERNANCE.md`

`BLACKBOX_query_count=3`.
`production_authority=false`.
