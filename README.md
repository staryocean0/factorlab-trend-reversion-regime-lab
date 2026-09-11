# FactorLab Trend–Reversion Regime Lab

This repository owns reversal / mean-reversion strategy research.

## Current authority

Certified mechanisms remain:

- **R1** — intact parent trend + lower-scale counter-move recovery;
- **R2** — intact parent range + boundary overshoot / failed acceptance / re-entry.

`BLACKBOX_query_count=3`; no query #4.  
`production_authority=false`.

## Latest result

The pure cash-index study first established:

`R1_PRICE_EDGE_SUPPORTED_R2_DIRECT_DIRECTIONAL_PRICE_EDGE_NOT_SUPPORTED`

A subsequent preregistered matched-parent attribution then asked whether R1 adds return beyond generic continuation of an otherwise similar intact parent trend.

Final interpretation:

- **R1_A / CSI1000:** pullback-specific incremental alpha is supported. At the frozen 15/30-bar locations the paired incremental means are `+3.85bp` / `+6.07bp`, bootstrap 95% lower bounds are positive, annual incremental means are positive in `4/5` / `5/5` years, and LONG/SHORT incremental means are both positive.
- **R1_A / STAR50:** incremental means point in the same direction at short horizons, but transport does not meet the full strong-incremental rule.
- **R1_B:** its large delayed raw returns do not survive matched-parent attribution. CSI1000 240-bar raw event return is `+23.43bp`, but the matched parent control is `+34.63bp`; incremental return is `-11.20bp`. Treat the delayed R1_B price edge primarily as parent-trend continuation, not distinct pullback alpha.
- **R2:** direct directional price translation remains unsupported.

Current classification:

`R1_A_CSI1000_PULLBACK_SPECIFIC_INCREMENTAL_ALPHA_SUPPORTED_TRANSPORT_NOT_YET_STRONG`

`R1_B_RAW_DIRECTIONAL_EDGE_REINTERPRETED_AS_PARENT_TREND_CONTINUATION_NOT_DISTINCT_PULLBACK_ALPHA`

No holding horizon has been selected.

## Current frontier

The lead lane is now **R1_A carrier price transport**:

`certified R1 mechanism -> R1_A incremental cash-index alpha -> ETF/index-carrier transport -> executable implementation`

The next carrier study must replay unchanged R1_A event timestamps/directions and report the full `1/5/15/30/60/120/240` horizon surface. It may not choose 15 or 30 bars as a winner from the index result.

No admitted ETF minute-price package is currently in this repository.

## Start here

1. [`CONTINUE_HERE.md`](CONTINUE_HERE.md)
2. [`docs/research/R1_INCREMENTAL_ALPHA_PROGRAM_DECISION_20260911.md`](docs/research/R1_INCREMENTAL_ALPHA_PROGRAM_DECISION_20260911.md)
3. [`docs/research/R1_INCREMENTAL_ALPHA_ATTRIBUTION_20260911.md`](docs/research/R1_INCREMENTAL_ALPHA_ATTRIBUTION_20260911.md)
4. [`docs/governance/R1_INCREMENTAL_ALPHA_ATTRIBUTION_FREEZE@1.0.json`](docs/governance/R1_INCREMENTAL_ALPHA_ATTRIBUTION_FREEZE@1.0.json)
5. [`docs/research/INDEX_PRICE_VALIDITY_STUDY_20260911.md`](docs/research/INDEX_PRICE_VALIDITY_STUDY_20260911.md)

Closed R1/R2 translations and R1_B option identities remain closed. Do not rescue them with post-result horizon, strike, DTE, ratio, filter or timing search.
