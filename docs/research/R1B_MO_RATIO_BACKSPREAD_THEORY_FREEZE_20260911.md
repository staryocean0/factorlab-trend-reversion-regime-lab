# R1_B MO ratio-backspread theory freeze — 2026-09-11

Identity: `rmr_R1B_MO_ratio_backspread_v1`

Candidate: `R1B_MO_1x2_ADJACENT_OTM_RATIO_BACKSPREAD_SAME_CAUSAL_EXIT`

Status: **FROZEN BEFORE OUTCOME EXECUTION**

`fresh_oos=false`  
`BLACKBOX_query_count=3`  
`production_authority=false`

Machine freeze: `docs/governance/R1B_MO_BACKSPREAD_PRE_EXECUTION_FREEZE@1.0.json`.

## Why this is a new payoff object rather than a retune

The closed single-long ATM MO identity failed all three sealed gates. Its completed-event mean was -46.58 CNY, median -1248 CNY, win rate 28.96%, and only 2024 had a positive annual mean. The failure was not missing quotes; it was the economic shape: the typical event paid option premium/spread while the inherited causal completion clock arrived late, even though a sparse right tail remained.

This review does **not** change R1_B events, S2/S3 thresholds, parent direction, entry clock, causal success/failure exit, 1200-bar safety horizon, DTE rule, fees, years, or any probability threshold.

The new object is a same-expiry **1x2 directional ratio backspread**:

- upward R1_B parent: short one frozen-ATM call, long two immediately adjacent OTM calls;
- downward R1_B parent: short one frozen-ATM put, long two immediately adjacent OTM puts.

The short ATM leg finances part of the premium paid for two farther-tail options. The package has a materially different nonlinear payoff geometry from one long ATM option: it intentionally accepts a moderate-move loss valley in exchange for lower net premium burden and positive tail convexity when parent restoration becomes sufficiently large. This directly represents the previously observed “rare large restoration / weak typical event” shape without selecting a favorable strike distance from outcomes.

The long strike is exactly one listed strike beyond the deterministic ATM leg in the OTM direction. The ratio is exactly 1:2. Neither is searched.

## Conservative execution

The two contracts must be executable at a **common quote timestamp**. Entry uses the short-leg bid and two long-leg asks; exit uses the short-leg ask and two long-leg bids. Size must support 1 short contract and 2 long contracts. Legging across different timestamps, midpoint pricing and last-price substitution are forbidden.

The existing user-frozen 14 CNY per contract per open/close leg applies. A completed package therefore pays 84 CNY total fees across six contract executions.

## Sealed evidence gates

Because this is explicitly a tail-convex payoff object, a positive event-level median is not an appropriate gate. Instead all of the following are frozen before outcomes:

1. joint executable-fill coverage >= 80% of joinable underlying R1_B events;
2. pooled mean net CNY > 0;
3. annual mean net CNY > 0 in at least 2 of 2023/2024/2025;
4. quarterly mean net CNY > 0 in at least 6 of the 12 quarters from 2023Q1 through 2025Q4.

The quarterly gate prevents a single isolated annual/tail episode from carrying the whole identity while still allowing an intentionally skewed event-level distribution.

Any failed gate closes this identity. There is no second width, second ratio, alternate DTE, alternate exit, or filtered rescue.

## What a PASS would and would not mean

A PASS would establish only an instrument-payoff research candidate on consumed historical evidence. It would not authorize BLACKBOX #4 or production. Because the position contains a short option leg, broker spread-margin treatment, capital usage and portfolio concurrency would require a later separate account-level audit before any executable-account claim.

The next legal action is a results-blind implementation followed by one execution of the frozen study.
