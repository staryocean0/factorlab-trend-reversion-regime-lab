# R1 incremental-alpha program decision — 2026-09-11

Status: **COMPLETE / NO HORIZON SELECTED / NO PRODUCTION AUTHORITY**

Source study: `docs/research/R1_INCREMENTAL_ALPHA_ATTRIBUTION_20260911.md`

## Decision

The pure index-price study established that R1 events are followed by favorable signed index returns. The matched-parent attribution now separates two very different interpretations.

### R1_A — pullback-specific incremental alpha is supported on CSI1000

Against results-blind matched parent-trend clocks, CSI1000 R1_A retains a positive incremental effect at the predeclared 15- and 30-bar horizons:

- 15 bars: event `+4.80bp`, matched control `+0.95bp`, incremental `+3.85bp`, event-day cluster-bootstrap 95% CI `[+0.80,+6.88]bp`, positive annual incremental mean `4/5`, LONG `+3.96bp`, SHORT `+3.73bp`;
- 30 bars: event `+6.80bp`, matched control `+0.72bp`, incremental `+6.07bp`, bootstrap 95% CI `[+1.38,+10.66]bp`, positive annual incremental mean `5/5`, LONG `+5.47bp`, SHORT `+6.65bp`.

These are the only CSI1000 R1_A horizons meeting every preregistered strong-incremental condition. This does **not** select 15 or 30 bars as a trading holding period; it locates where pullback-specific information is visible.

STAR50 R1_A points in the same direction at 1/5/15/30 bars, but no horizon meets the full strong-incremental rule because confidence intervals cross zero and annual/side stability is weaker. Therefore STAR50 is supportive transport evidence, not a second independent confirmation.

Program interpretation:

`R1_A_CSI1000_PULLBACK_SPECIFIC_INCREMENTAL_ALPHA_SUPPORTED_TRANSPORT_NOT_YET_STRONG`

### R1_B — raw price edge is primarily parent-trend continuation, not incremental pullback alpha

R1_B's previously attractive delayed raw term structure does not survive matched-parent attribution.

CSI1000 examples:

- 30 bars: event `+6.17bp`, matched parent control `+7.63bp`, incremental `-1.45bp`;
- 120 bars: event `+11.03bp`, control `+17.91bp`, incremental `-6.87bp`;
- 240 bars: event `+23.43bp`, control `+34.63bp`, incremental `-11.20bp`.

STAR50 tells the same broad story: 240-bar event return is `+18.19bp`, matched control `+19.33bp`, incremental `-1.14bp`; no R1_B horizon meets the strong-incremental rule on either index.

The price-path decomposition also shows that CSI1000 R1_B's late positive event return is largely shared with or exceeded by generic matched parent continuation, especially the next-session component.

Program interpretation:

`R1_B_RAW_DIRECTIONAL_EDGE_REINTERPRETED_AS_PARENT_TREND_CONTINUATION_NOT_DISTINCT_PULLBACK_ALPHA`

This does not invalidate the certified R1_B restoration-probability mechanism. It means the R1_B confirmation is not supported as an incremental directional entry advantage over simply being exposed to an otherwise comparable intact parent trend.

## Consequences

1. Do not reopen R1_B option, horizon, probability, or timing rescue based on its large raw 120/240-bar returns.
2. R1_B may remain useful as a state/mechanism descriptor, but it is no longer the lead standalone entry-alpha candidate.
3. R1_A is now the lead price-alpha research lane.
4. The next empirical layer should be **carrier transport**, not signal refitting: replay the unchanged R1_A event timestamps/direction on corresponding ETF/index-tracking prices before any execution-rule optimization.
5. Carrier transport must report the same predeclared horizon surface rather than picking 15 or 30 bars as a winner.
6. Only after carrier transport is understood should spread/fees/T+1/borrow/futures basis be introduced.

R2 direct directional price translation remains unsupported and is not reopened.

`BLACKBOX_query_count=3`; no query #4. `production_authority=false`.
