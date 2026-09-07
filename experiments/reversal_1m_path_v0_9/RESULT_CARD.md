# RESULT CARD — 5m Signal / 1m Path Resolution v0.9

Date: 2026-09-07  
Status: **STAR50 negative; CSI1000 10bps thin lead only**  
Run: `34101572239`  
Artifact: `reversal-1m-path-v0-9`  
Artifact ID: `10010696562`  
Artifact digest: `sha256:be7d479bc8c28dfa83e5cd7912931e46b5a7acabbb65a137065a649f99e7aaaf`

## Hypothesis

The small CSI1000 10bps first-passage asymmetry in v0.8 may be genuine but obscured by 5m OHLC ordering ambiguity.

## Frozen policy

- signal remains the completed-5m v0.5 robust residual re-entry signal;
- signal thresholds and features are unchanged;
- the signal timestamp is projected onto supplied 1m bars only to observe the future path;
- entry: next 1m open after the completed 5m signal, audited against next 5m open;
- barriers: symmetric 5bps / 10bps;
- caps: 5m / 10m / 30m;
- same-day only;
- 2025 unopened.

## Audit and tests

- sealed seed validation: passed;
- original main seed validation: passed;
- pytest: **42 passed**;
- STAR50 5m signals: 2,282; mapped to 1m: 2,279;
- CSI1000 5m signals: 2,148; mapped to 1m: 2,148;
- audited next-1m-open vs next-5m-open exact-match rate: **100%** for both indices;
- maximum audited entry-price difference: **0 points**.

Therefore the 1m analysis resolves future path ordering without intentionally improving entry timing.

## Main results

### STAR50

5bps clean target-first share:

- 5m cap: 47.91%;
- 10m: 47.98%;
- 30m: 47.74%.

10bps clean target-first share:

- 5m: 47.56%;
- 10m: 47.38%;
- 30m: 47.36%.

The 5m-ambiguous 10bps subset is worse after 1m resolution: at 30m, target-first ≈39.2% vs stop-first ≈57.3%.

Conclusion: 5m ambiguity was not hiding a STAR50 reversal edge.

### CSI1000

5bps clean target-first share:

- 5m: 50.13%;
- 10m: 50.22%;
- 30m: 49.51%.

This is effectively noise.

10bps:

| Cap | Target first | Stop first | Neither | Clean target share |
|---:|---:|---:|---:|---:|
| 5m | 32.43% | 29.35% | 38.17% | 52.49% |
| 10m | 43.07% | 40.86% | 16.03% | 51.32% |
| 30m | 50.13% | 48.20% | 1.63% | 50.98% |

The corresponding symmetric target-minus-stop hit imbalance is only roughly +0.31 / +0.22 / +0.19 bps for 5/10/30m.

No spread, fee, market impact, vehicle basis or time-stop PnL has yet been charged.

## Falsification / implication

- STAR50 remains negative evidence for this reversal family.
- CSI1000 10bps retains a real-enough structural asymmetry to investigate, but its magnitude is sub-bp and insufficient to call alpha.
- The next question is whether this thin effect is uniformly distributed or localized by market clock / environment.

## Next step

Freeze the signal, 10bps barrier and 1m path. Report the complete eight-half-hour clock surface; do not select a winning clock window.
