# RESULT CARD — Year × Clock × Side Stability v0.11

Date: 2026-09-07  
Status: **clock effect partly real at aggregate level; side/year mechanism still unstable**  
Run: `34102486393`  
Artifact: `reversal-stability-v0-11`  
Artifact ID: `10011041657`  
Artifact digest: `sha256:62b36bffccf4823376bbff73cb269a65e3687a81f6151f43f10946ff68c1b340`

## Hypothesis

The v0.10 CSI1000 clock dependence may represent a repeatable intraday structure rather than a small number of favorable years or one reversal side.

## Frozen policy

No entry or exit definition was changed from v0.10:

- completed-5m robust residual re-entry signal, threshold 2.0;
- supplied 1m path resolution;
- symmetric 10bps target/stop;
- caps 5m / 10m / 30m;
- same eight half-hour continuous-auction blocks;
- full 2020(partial)–2024 surface;
- report ALL / LONG / SHORT separately;
- 2025 unopened.

## Audit and tests

- sealed seed validation: passed;
- original main seed validation: passed;
- pytest: **42 passed**;
- STAR50 mapped signals: 2,279;
- CSI1000 mapped signals: 2,148;
- first signal day: 2020-07-24;
- last signal day: 2024-12-31.

## Main result 1 — CSI1000 H1 aggregate clock effect is unusually persistent

For `09:30–10:00` (H1), ALL-side clean target share is above 50% in all five calendar slices at the 5m cap:

- positive years: **5 / 5**;
- median yearly clean target share: **53.33%**;
- minimum: **51.35%**;
- maximum: **68.42%**;
- events: 339.

At 10m and 30m, four years are above 50% and one year is exactly 50%; none is below 50%.

This is stronger year transport than the pooled v0.10 table alone implied.

Important caveat: 2020 is a partial common-sample year beginning in late July and H1 has only 23 CSI1000 events in the 2020 10m cell. It must not receive the same evidential weight as a full year.

## Main result 2 — the aggregate H1 stability is not homogeneous across reversal side

H1 LONG stability:

| Cap | Positive years | Negative years | Median yearly clean target share | Total events |
|---:|---:|---:|---:|---:|
| 5m | 4 | 1 | 62.79% | 203 |
| 10m | 4 | 1 | 61.70% | 203 |
| 30m | 4 | 1 | 61.70% | 203 |

H1 SHORT stability:

| Cap | Positive years | Negative years | Median yearly clean target share | Total events |
|---:|---:|---:|---:|---:|
| 5m | 3 | 2 | 60.61% | 136 |
| 10m | 3 | 2 | 56.76% | 136 |
| 30m | 3 | 2 | 56.76% | 136 |

The year signs also rotate by side. At the 10m cap, for example:

- LONG is positive in 2020–2023 but negative in 2024;
- SHORT is strong in 2020–2021, negative in 2022–2023, and positive again in 2024.

Therefore the apparently stable ALL-side H1 effect can partly arise from changing side composition / different side-specific environments. It should **not** yet be called one stable homogeneous reversal mechanism.

## Main result 3 — H4 long-side lead is worth preserving as a hypothesis, not a rule

For `11:00–11:30` (H4), CSI1000 LONG is more persistent than H4 ALL/SHORT:

- 5m: 4 positive years / 1 negative; median yearly clean share ≈63.64%;
- 10m: 4 / 1; median ≈60.00%;
- 30m: 4 positive / 0 negative with one exactly 50%; median ≈61.54%;
- total LONG events: 145.

This is a result-driven lead discovered after multiple clock/side inspections. It is **not** eligible to become a strategy filter without a new preregistered confirmation step.

## Main result 4 — adverse and mixed clock blocks remain important controls

CSI1000 `10:30–11:00` (H3) is mostly adverse:

- 5m ALL: 0 positive years, 4 negative, one exactly 50%;
- 30m ALL: 1 positive, 4 negative.

`13:00–13:30` (H5) is mixed and materially weak in several recent cells.

These negative clock blocks are useful controls and must remain in any subsequent full-surface report.

## STAR50

STAR50 remains inconsistent and broadly non-supportive of the reversal family. Some clock slices have positive year medians, but there is no stable cross-cap pattern that overturns the prior first-passage anti-edge. In particular, H6 at the 30m cap is negative in all five year slices.

No STAR50 clock winner should be promoted.

## Interpretation

v0.11 partially confirms **time-of-day dependence**, but it does not yet identify the economic mechanism.

The key new finding is not simply “09:30–10:00 works.” It is:

> The CSI1000 H1 pooled effect transports surprisingly well by year at the aggregate side level, while its LONG/SHORT components rotate materially across years.

That points toward an interaction with pre-entry directional/session context rather than a universal clock-only reversal law.

Possible mechanisms to test next include prior-only coordinates such as overnight gap, open-to-signal displacement, same-day direction and volatility expansion. These are hypothesis coordinates, not trend-strategy imports.

The current package lacks signed order flow, depth and news, so liquidity/information stories cannot be causally identified.

## Next step

Do **not** create an H1/H4 winner filter yet.

A sensible v0.12 is a mechanism audit of the frozen CSI1000 events:

1. overnight gap direction/magnitude (especially H1);
2. open-to-signal signed displacement;
3. whether the re-entry is against or with the day's prior direction;
4. volatility expansion/compression at entry;
5. report the full clock × side surface inside coarse prior-only buckets.

The purpose is to explain why side signs rotate across years, not to add another optimized condition.

2025 remains unopened.
