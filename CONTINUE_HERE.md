# Continue here — reversal / mean-reversion bucket

## Current authority

Certified mechanisms remain:

- **R1** — `rmr_cross_scale_pullback_parent_integrity_v2`;
- **R2** — `rmr_range_boundary_parent_integrity_v2`.

Reusable `BLACKBOX_query_count=3` exactly: R1 PASS, R5-C FAIL, R2 PASS. No query #4 is authorized.

`production_authority=false`.

## Price-layer result

The frozen pure cash-index study established:

`R1_PRICE_EDGE_SUPPORTED_R2_DIRECT_DIRECTIONAL_PRICE_EDGE_NOT_SUPPORTED`

See:

- `docs/governance/INDEX_PRICE_VALIDITY_FREEZE@1.0.json`
- `docs/research/INDEX_PRICE_VALIDITY_STUDY_20260911.md`
- `docs/ops/evidence/index_price_validity_20260911/price_validity_receipt.json`

That result did **not** select a holding horizon and did not test ETF/futures/options execution.

## Latest decisive study — matched-parent incremental attribution

The next frozen study asked whether R1 events add future return beyond an otherwise similar intact parent trend.

Freeze:

`docs/governance/R1_INCREMENTAL_ALPHA_ATTRIBUTION_FREEZE@1.0.json`

Matching was frozen before paired outcomes:

- same symbol / R1 cell / year / parent direction / 30-minute clock bucket;
- nearest neighbor on causal parent drift, parent efficiency, parent age and 30m/240m local-vol ratio;
- no return or outcome information in matching;
- no post-result matching relaxation;
- all `1/5/15/30/60/120/240` horizons reported;
- no horizon winner selected.

Execution run: GitHub Actions `34618319618` — **SUCCESS** after frozen tests passed.

Read:

- `docs/research/R1_INCREMENTAL_ALPHA_ATTRIBUTION_20260911.md`
- `docs/ops/evidence/r1_incremental_alpha_20260911/attribution_receipt.json`
- `docs/research/R1_INCREMENTAL_ALPHA_PROGRAM_DECISION_20260911.md`

### R1_A — lead incremental-alpha lane

CSI1000 `000852.SH`, 2021–2025:

- matching coverage: **1296/1296 = 100%**;
- 15 bars: event `+4.80bp`, matched parent control `+0.95bp`, incremental `+3.85bp`, bootstrap 95% CI `[+0.80,+6.88]bp`, positive annual incremental mean `4/5`, LONG `+3.96bp`, SHORT `+3.73bp`;
- 30 bars: event `+6.80bp`, control `+0.72bp`, incremental `+6.07bp`, bootstrap 95% CI `[+1.38,+10.66]bp`, positive annual incremental mean `5/5`, LONG `+5.47bp`, SHORT `+6.65bp`.

These are the only CSI1000 R1_A horizons satisfying every preregistered strong-incremental condition.

**Do not select 15 or 30 bars as a trading holding period.** They are locations where the fixed horizon surface shows pullback-specific information.

STAR50 `000688.SH` has positive R1_A incremental means at short horizons, but confidence intervals and annual/side stability do not satisfy the full strong rule. Treat it as supportive transport only.

Current classification:

`R1_A_CSI1000_PULLBACK_SPECIFIC_INCREMENTAL_ALPHA_SUPPORTED_TRANSPORT_NOT_YET_STRONG`

### R1_B — reinterpretation

R1_B's large delayed raw index returns do **not** survive matched-parent attribution.

CSI1000:

- 30 bars: event `+6.17bp`, control `+7.63bp`, incremental `-1.45bp`;
- 120 bars: event `+11.03bp`, control `+17.91bp`, incremental `-6.87bp`;
- 240 bars: event `+23.43bp`, control `+34.63bp`, incremental `-11.20bp`.

STAR50 also has no strong R1_B incremental horizon.

Current classification:

`R1_B_RAW_DIRECTIONAL_EDGE_REINTERPRETED_AS_PARENT_TREND_CONTINUATION_NOT_DISTINCT_PULLBACK_ALPHA`

The certified R1_B restoration-probability mechanism remains valid. The conclusion is narrower: R1_B confirmation is not supported as an incremental directional entry advantage over comparable intact parent-trend exposure.

Therefore do not reopen R1_B option, horizon, probability or timing rescue using its raw 120/240-bar returns.

## Current frontier

The lead empirical lane is now **R1_A carrier transport**, not R1_B and not R2.

Correct hierarchy:

`certified R1 mechanism -> R1_A pullback-specific CSI1000 incremental alpha -> carrier price transport -> executable implementation`

The next empirical study should replay the unchanged R1_A causal event timestamps/directions on corresponding ETF or other index-tracking carrier prices.

Carrier transport rules:

- do not refit the R1 signal;
- do not choose 15/30 bars as a winner from the index result;
- report the same full frozen horizon surface;
- synthetic SHORT is allowed for price-transport research and must be labelled non-executable where borrow/shorting is unavailable;
- execution costs, T+1, borrow, futures basis and inventory come only **after** price transport.

No admitted ETF minute-price package is currently in this repository, so ETF transport has not yet been executed.

## Closed — do not restart or retune

Still closed under their own definitions:

- R1 immediate structural economic translation v1/v2/v3;
- R2 `rmr_R2_range_reentry_economic_translation_v1`;
- unified router;
- `rmr_R1B_temporal_impulse_completion_v1`;
- R1_B single-long ATM MO identity;
- R1_B 1x2 adjacent-OTM MO backspread;
- probability-threshold / sizing rescue;
- R3/R4, R5-B1, R5-C and broad automatic R8/R9 lanes.

The matched-parent result does not reopen those identities.

## Data

Verified cash-index 1m data:

- `000852.SH`: 2015-01-05 .. 2025-12-31;
- `000688.SH`: 2020-07-23 .. 2025-12-31.

Loaded through `src/regime_lab/market_data.py` with manifest/hash checks.

The separate `data/r1b_research/` MO package remains valid only for reproduction of already-closed option work.

## Governance boundary

Not authorized:

- selecting 15 or 30 bars and declaring an execution rule;
- post-result stop/target/time-of-day/regime/probability tuning;
- treating R1_B raw delayed return as distinct alpha after matched-parent failure;
- reopening R2 directional execution;
- another R1_B option v3/v4;
- BLACKBOX query #4;
- production promotion.

Authorized next work:

- preserve/reproduce matched-parent attribution;
- locate/admit ETF or carrier minute-price data;
- freeze carrier transport before reading carrier outcomes.

## Read first

1. `CONTINUE_HERE.md`
2. `docs/research/R1_INCREMENTAL_ALPHA_PROGRAM_DECISION_20260911.md`
3. `docs/research/R1_INCREMENTAL_ALPHA_ATTRIBUTION_20260911.md`
4. `docs/governance/R1_INCREMENTAL_ALPHA_ATTRIBUTION_FREEZE@1.0.json`
5. `docs/research/INDEX_PRICE_VALIDITY_STUDY_20260911.md`
6. `docs/research/R1B_POST_BACKSPREAD_PAYOFF_THEORY_REVIEW_20260911.md`

`BLACKBOX_query_count=3`.
`production_authority=false`.
