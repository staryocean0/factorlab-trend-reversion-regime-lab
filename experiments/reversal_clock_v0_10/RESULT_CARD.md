# RESULT CARD — Half-Hour Clock Localization v0.10

Date: 2026-09-07  
Status: **result-driven localization; no clock rule selected**  
Run: `34101849785`  
Artifact: `reversal-clock-v0-10`  
Artifact ID: `10010808067`  
Artifact digest: `sha256:db262cb9c8faa9c908cb404b3b24b4e8e6e498e0e0263fb7f5e56b41769678e8`

## Hypothesis

The thin CSI1000 10bps asymmetry observed in v0.9 may depend materially on intraday clock rather than representing a uniform mean-reversion effect.

## Frozen policy

- completed-5m robust residual re-entry signal unchanged;
- 1m future path resolution unchanged;
- symmetric 10bps barrier;
- caps: 5m / 10m / 30m;
- all eight continuous-auction half-hour blocks reported;
- no clock winner selected;
- 2025 unopened.

## Audit and tests

- sealed seed validation: passed;
- original main seed validation: passed;
- pytest: **42 passed**;
- STAR50 signals mapped to clock blocks: 2,279;
- CSI1000 signals mapped to clock blocks: 2,148.

## STAR50

Most clock blocks remain below 50% clean target-first share. Small isolated late-day pockets do not persist across caps and are not sufficient to change the prior negative conclusion.

## CSI1000

### 5m cap

| Clock block | Events | Clean target share | Symmetric hit imbalance |
|---|---:|---:|---:|
| 09:30–10:00 | 339 | 55.16% | +0.855 bps |
| 10:00–10:30 | 436 | 50.49% | +0.069 bps |
| 10:30–11:00 | 361 | 48.13% | -0.222 bps |
| 11:00–11:30 | 263 | 56.72% | +0.684 bps |
| 13:00–13:30 | 162 | 50.00% | 0.000 bps |
| 13:30–14:00 | 200 | 54.95% | +0.550 bps |
| 14:00–14:30 | 206 | 53.21% | +0.340 bps |
| 14:30–15:00 | 142 | 53.52% | +0.352 bps |

### Cross-cap observations

- `09:30–10:00` remains positive at 5/10/30m.
- `11:00–11:30` remains positive at 5/10/30m.
- `10:30–11:00` remains negative at 5/10/30m.
- `13:00–13:30` is neutral at 5m and negative at 10/30m.
- other afternoon blocks are mixed.

## Interpretation discipline

This experiment is explicitly post-v0.9 failure localization. Eight clock blocks across multiple caps create a multiple-comparison surface. The apparently favorable blocks must **not** be converted directly into a strategy filter.

The important result is structural:

> CSI1000's already-thin short-horizon re-entry asymmetry is strongly time-of-day dependent.

This is compatible with prior China intraday literature showing materially different continuation/reversal relations across intraday intervals, but the literature does not validate our specific signal or clock blocks.

## Next step

Freeze the current definitions and report a complete `year × clock × LONG/SHORT` matrix before any clock mask is allowed.

If the clock pattern is unstable by year or side, treat it as sample composition and stop further clock specialization. If it is reasonably persistent, only then preregister a candidate clock mask and evaluate a real exit policy plus conservative friction stress.
