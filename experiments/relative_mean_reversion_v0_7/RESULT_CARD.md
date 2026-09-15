# RESULT CARD — Cross-Index Relative-Value MR v0.7

Date: 2026-09-07  
Status: **negative overall; retain as environment-dependence evidence**  
Run: `34100826456`  
Head: `1ea6ca281ad2b4515e02711e746a86d488138d42`  
Artifact: `relative-mean-reversion-v0-7`  
Artifact ID: `10010413195`  
Artifact digest: `sha256:e97c18050054914de0055c5a140b012181312a39d9387065106a27b6de0c8427`

## Hypothesis

After removing the common market component by trading STAR50 against CSI1000, a sufficiently unusual 60-trading-minute relative return that has begun to re-enter its prior robust distribution may continue to mean-revert.

This is a distinct mean-reversion mechanism. It does not use a trend strategy or Trend-vs-Reversion gate.

## Frozen v0.7 policy

- frequency: 5m;
- common history: `2020-07-23`–`2024-12-31`;
- 2025 unopened;
- 60 trading-minute STAR-minus-CSI same-day log-return dislocation;
- 60m lookback is undefined if it would cross a trading-day boundary;
- robust state: median / `1.4826*MAD` from the most recent 48 valid strictly-prior dislocation observations;
- threshold: `|z| >= 2`;
- signal occurs only when z crosses back inside the band;
- +1 = long STAR / short CSI; -1 = short STAR / long CSI;
- both legs enter at next-bar open with equal notional diagnostic exposure;
- fixed same-day diagnostic horizons: 5/10/15/30/60/120 trading minutes;
- no fees, spread, financing or impact included.

## Audit and tests

- sealed research-seed hashes unchanged: passed;
- untouched original main exact-set validator: passed;
- full pytest: **36 passed in 0.70s**;
- synchronized rows: 51,792;
- common trading days: 1,079;
- valid same-day 60m dislocation rows: 38,844;
- valid causal z rows: 38,796;
- signals: 1,613 across 835 days;
- long STAR / short CSI signals: 787;
- short STAR / long CSI signals: 826.

## All-sample gross diagnostics

| Horizon | Mean bps | Median bps | Win rate | Central-90% mean bps |
|---:|---:|---:|---:|---:|
| 5m | -0.28 | -0.18 | 49.40% | -0.11 |
| 10m | -0.12 | +0.04 | 50.13% | +0.10 |
| 15m | -0.64 | +0.22 | 50.45% | -0.04 |
| 30m | -1.04 | +0.10 | 50.13% | -0.12 |
| 60m | -1.49 | -0.79 | 48.61% | -0.79 |
| 120m | -3.76 | -0.90 | 48.93% | -2.57 |

The baseline is not a stable positive strategy even before costs.

## Calendar transport

Mean bps:

| Year | 5m | 10m | 15m | 30m | 60m | 120m |
|---|---:|---:|---:|---:|---:|---:|
| 2020 | -0.65 | -1.48 | -1.85 | -1.92 | -9.98 | -17.37 |
| 2021 | -0.61 | +0.13 | -0.53 | -2.22 | -4.28 | -6.24 |
| 2022 | +0.48 | +0.63 | +0.86 | +0.54 | +0.89 | +0.01 |
| 2023 | +0.07 | +0.38 | +0.16 | +0.35 | +2.64 | +1.89 |
| 2024 | -0.98 | -1.18 | -2.82 | -2.82 | -2.21 | -5.03 |

The sign switch is substantial: 2022–2023 are broadly more mean-reverting under the same rule; 2020 and 2024 are broadly continuation-dominated.

## Direction asymmetry

All-sample mean bps by spread direction:

| Side | 5m | 10m | 15m | 30m | 60m | 120m |
|---|---:|---:|---:|---:|---:|---:|
| Long STAR / short CSI | -0.12 | -0.44 | -0.73 | -2.16 | -2.91 | -4.56 |
| Short STAR / long CSI | -0.43 | +0.20 | -0.54 | +0.07 | +0.01 | -2.91 |

This asymmetry is descriptive and must not be converted into a one-sided winner after seeing the result.

## Falsification / implication

v0.7 rejects the first universal cross-index relative-reentry rule.

It does **not** reject all relative-value mean reversion. Instead it exposes a sharper question:

> What pre-entry environment separates the 2022–2023 mean-reverting behavior from the 2020/2024 continuation behavior?

## Next step

Freeze v0.7 entry events and build a failure atlas from prior-only coordinates: common volatility, volatility expansion, cross-index correlation, relative path efficiency, common displacement, shock concentration, time of day and direction.

Do not change the entry threshold, select the favorable years, or import the independent trend strategy in this diagnostic phase.
