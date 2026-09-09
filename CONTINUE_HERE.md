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

## Exact next authorized action

**Do not run an option return study yet.**

The current repository does not contain an MO intraday best-bid/best-ask tape. The next authorized action is data admission only:

1. obtain a provenance-stable CSI1000 MO intraday quote source;
2. require contract code, call/put, strike, expiry, timestamp, bid1/ask1 and sizes, volume, open interest and trading-status fields where available;
3. freeze exchange-calendar and timestamp normalization;
4. freeze historically applicable exchange/broker fee treatment;
5. checksum and inventory the source before event-conditioned option outcomes are opened;
6. preserve pre-freeze historical MO observations as reusable instrument-development evidence, not fresh mechanism BLACKBOX;
7. reserve prospective post-freeze observations for a clean validation boundary.

The primary R1_B option mapping may not substitute midpoint/last price for missing bid/ask after outcomes are seen and may not search strike, expiry/DTE, horizon, probability threshold, timing, stop, target, scale or time-of-day.

## Bucket boundary

Do not restart a generic K-line state recognizer here. Range/up/down causal state recognition belongs to `factorlab-two-wave-strategy-lab`.

Do not restart bottom-layer volatility/risk-state switching here. Unsafe/Recovering/HighVol risk research belongs to `factorlab-star50-filter-lab`.

The `kline-recognizer` v1-v13 research branches in this repository are mis-scoped historical evidence. They remain in Git history but no longer define current authority.

## Read first

1. `CONTINUE_HERE.md`
2. `docs/research/R1_R2_MIGRATION_NOTE_20260909.md`
3. `docs/research/R1B_MO_CONVEX_PAYOFF_THEORY_REVIEW_20260910.md`
4. `docs/research/R5_B1_LIMITED_DIAGNOSTIC_RESULT_20260910.md`
5. `docs/DATA.md`
6. `docs/RESEARCH_GOVERNANCE.md`

`production_authority=false`.
