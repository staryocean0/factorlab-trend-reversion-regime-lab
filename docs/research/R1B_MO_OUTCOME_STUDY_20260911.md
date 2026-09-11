# R1_B MO frozen outcome study — 2026-09-11

Research identity: `rmr_R1B_MO_convex_impulse_mapping_v1`

Candidate: `R1B_MO_ATM_DIRECTIONAL_LONG_SAME_CAUSAL_EXIT`

Decision: **FAIL_IDENTITY_CLOSED**

`fresh_oos=false`  
`BLACKBOX_query_count=3`  
`production_authority=false`

Machine freeze: `docs/governance/R1B_MO_PRE_EXECUTION_FREEZE@1.0.json`  
Receipt: `docs/ops/evidence/r1b_mo_outcome_20260911/outcome_receipt.json`  
Ledger: `docs/ops/evidence/r1b_mo_outcome_20260911/event_ledger.csv`

## Authority

The user authorized this exact frozen mapping with the instruction to run the outcome study. Mapping, clocks, ATM/OTM tie, fees (14+14), and the three viability gates were not changed after results.

This window is reusable instrument-development evidence for **2022-07-22 .. 2025-12-31**. It is not fresh OOS and not BLACKBOX. 2022 is report-only and does not vote. 2026 MO quotes were not used to construct events.

The closed linear identity `rmr_R1B_temporal_impulse_completion_v1` remains closed. Its 2015--2020 lockbox was not reused as MO evidence.

## Execution

The runner regenerated certified R1_B `S2-inside-S3` events on the admitted `000852.SH` 1m series **2015-01-05 .. 2025-12-31** with frozen thresholds, kept continuous structural non-overlap, and scored only events whose next-bar entry date fell in the joinable window.

Option fills used admitted DataHub MO L1: first `TRADING` ask at or after the 1m entry clock, first `TRADING` bid at or after the inherited causal exit. Completed payoff:

`(exit_bid - entry_ask) * 100 - 14 - 14` CNY.

## Inventory

| Item | Count |
|---|---:|
| Joinable underlying events | 385 |
| Completed two-leg events | 366 |
| `entry_invalid` | 19 |
| Quote missingness | 0 |
| 2026 events | 0 |

Exit classes on completed events: 330 `temporal_completion`, 36 `parent_failure`, 0 `censored`.

Calls 181 / puts 185. Holding bars: mean 117.3, median 71, max 1148.

Independent recomputation of every completed `net_cny` from ask/bid/fees has maximum absolute error `4.55e-13`.

## Sealed gates

| Gate | Result | Evidence |
|---|---|---|
| pooled mean net CNY > 0 | **FAIL** | `-46.58` |
| pooled median net CNY > 0 | **FAIL** | `-1248.00` |
| mean net > 0 in at least 2 of `{2023,2024,2025}` | **FAIL** | 1/3 (only 2024) |

Annual completed mean / median net CNY:

| Year | n | Mean | Median | Votes |
|---|---:|---:|---:|---|
| 2022 | 45 | -429.33 | -1248.00 | no |
| 2023 | 70 | -546.86 | -1378.00 | yes |
| 2024 | 153 | +394.75 | -1168.00 | yes |
| 2025 | 98 | -202.49 | -1178.00 | yes |

Win rate on completed events is `28.96%`.

## Interpretation

The convex long-MO mapping does **not** convert the inherited R1_B temporal-completion clock into a viable event-level payoff on this joinable window.

The shape matches the already-closed linear identity: a possible right tail (2024 mean is positive) with a deeply negative typical event. Causal S2-completion confirmation remains late relative to the impulse extreme. Paying ask and selling bid, plus 28 CNY fees, makes the typical event worse, not better.

This is not a quote-coverage failure. Every tradeable event found both legs.

## Explicitly closed

Do not rescue this identity by:

- strike or DTE search;
- midpoint / last-price / delay search;
- horizon, stop, or S2-extreme exits;
- dropping 2022/2025 or keeping only 2024;
- probability filters or sizing;
- IM futures;
- BLACKBOX query #4;
- production promotion.

A later instrument identity would require a new, separately frozen payoff object. It may not retune this candidate.
