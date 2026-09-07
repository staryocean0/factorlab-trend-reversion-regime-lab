# RESULT CARD — Reversal First Passage v0.8

Date: 2026-09-07  
Status: **negative STAR50; weak/inconclusive CSI1000 lead**  
Run: `34101252215`  
Artifact: `reversal-first-passage-v0-8`  
Artifact ID: `10010573304`  
Artifact digest: `sha256:8c97b4bdcccfb23d5e77cd8ac7f3b6046aa5b5c4254b522d36ff9ad45e5bbc0f`

## Hypothesis

The favorable excursion seen in earlier MR diagnostics may be monetizable if a causal symmetric target is reached before an equally distant adverse stop.

## Frozen policy

- signal: v0.5 robust residual re-entry, threshold 2.0;
- frequency: 5m;
- history: `2020-07-23`–`2024-12-31`;
- 2025 unopened;
- entry: next 5m open;
- barriers: symmetric 5bps / 10bps;
- caps: 30m / 60m, same trading day;
- if target and stop are both touched in one 5m OHLC bar, outcome is `ambiguous_same_bar`;
- no favorable fill is assigned to ambiguous bars.

## Audit and tests

- sealed seed validation: passed;
- original main seed validation: passed;
- pytest: **42 passed**;
- STAR50 signal bars: 2,282 across 952 days;
- CSI1000 signal bars: 2,148 across 964 days.

## Main results

### STAR50

| Barrier | Cap | Clean target share | Target share if ambiguous is adverse |
|---:|---:|---:|---:|
| 5bps | 30m | 48.00% | 33.58% |
| 5bps | 60m | 47.82% | 32.86% |
| 10bps | 30m | 48.35% | 43.14% |
| 10bps | 60m | 48.40% | 43.00% |

No first-passage advantage.

### CSI1000

| Barrier | Cap | Clean target share | Target share if ambiguous is adverse |
|---:|---:|---:|---:|
| 5bps | 30m | 50.57% | 42.09% |
| 5bps | 60m | 50.58% | 41.52% |
| 10bps | 30m | 50.75% | 48.52% |
| 10bps | 60m | 51.00% | 48.58% |

The clean 10bps result is only slightly above 50%. About 4–5% of 10bps CSI1000 observations remain order-ambiguous at 5m.

Median resolution for target and stop is typically the first 5m bar.

## Falsification / implication

The v0.2 MFE observation cannot be upgraded into a tradable exit from 5m OHLC alone.

- STAR50: evidence remains adverse.
- CSI1000: a tiny 10bps target-first asymmetry is worth resolving at a finer path grid, but is not yet an economic edge.

## Next step

Keep the 5m signal unchanged and use supplied 1m bars only to resolve target/stop ordering. Do not create a new 1m entry strategy.
