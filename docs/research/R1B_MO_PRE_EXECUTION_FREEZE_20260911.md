# R1_B MO pre-execution freeze — 2026-09-11

Research identity: `rmr_R1B_MO_convex_impulse_mapping_v1`

Candidate: `R1B_MO_ATM_DIRECTIONAL_LONG_SAME_CAUSAL_EXIT`

Machine contract: `docs/governance/R1B_MO_PRE_EXECUTION_FREEZE@1.0.json`

Status: **FROZEN_RESULT_FREE**

Empirical option outcome test authorized: **no**

`BLACKBOX_query_count=3`  
`production_authority=false`

## Why this freeze exists

DataHub MO L1 bid/ask is admitted. That admission only certifies instrument quotes. This freeze writes the single mapping that may later be tested, including the ATM distance-tie rule that the 2026-09-10 theory review left open.

It does **not** run or authorize an event-conditioned MO PnL study.

## Inherited causal object

The closed linear identity `rmr_R1B_temporal_impulse_completion_v1` remains closed. This freeze reuses its clocks, not its 2015--2020 lockbox or its 10bp index-return gates.

| Item | Frozen value |
|---|---|
| Event engine | certified R1_B `S2-inside-S3` (PAIR_B), no refit |
| S2 / S3 | `0.006891654009228464` / `0.013783308018456928` |
| Underlying entry | next observed 000852.SH 1m close after R1_B confirmation |
| Success exit | first later parent-aligned S2 confirmation close |
| Failure exit | first close that crosses the original S3 failure boundary |
| Safety horizon | `entry_idx + 1200` observed 1m bars |

S2 wave extremes remain noncausal and may not be used as exits.

## Instrument mapping

- Upward parent → one long MO call; downward parent → one long MO put.
- ATM spot is that same 1m entry close. Do not re-strike on a later 3s print.
- Expiry first: earliest expiry **strictly after** the 1m date at `horizon_end_idx`.
- Then strike: minimum `|K - spot|`. Exact distance tie → OTM (call: higher K; put: lower K). Residual tie → smallest `contract_code`.
- Entry fill: first `TRADING` best ask after the 1m entry clock. Exit fill: first `TRADING` best bid after the inherited causal exit.
- No interpolation, midpoint, last-price substitute, or delay search.

Primary completed payoff:

`(exit_bid - entry_ask) * 100 - 14 - 14` CNY.

Incomplete events are counted (`option_entry_unavailable`, `option_exit_unavailable`, `option_entry_after_exit`, `underlying_horizon_truncated`, `window_unjoinable`, `entry_invalid`) and excluded from primary gates.

## Joinable window

MO quotes exist through **2026-08-25**. The admitted CSI1000 1m package in this repo ends **2025-12-31**.

The first authorized paired window is therefore **2022-07-22 .. 2025-12-31**. 2026 MO rows stay unjoinable until a separate 2026 1m admission exists. 2022 is a partial listing year and does not vote.

This window is reusable instrument-development evidence. It is not fresh OOS and not BLACKBOX.

## Sealed viability gates

These gates apply only after a later, explicit outcome-run authorization:

1. pooled mean net CNY > 0;
2. pooled median net CNY > 0;
3. mean net CNY > 0 in at least **2 of 3** years `{2023, 2024, 2025}`.

A failed gate closes the identity. Post-result retuning is forbidden.

## Next legal action

Wait for a separate user authorization to run this exact frozen outcome study. Do not start event-quote joins, strike/DTE search, or production work from this freeze.
