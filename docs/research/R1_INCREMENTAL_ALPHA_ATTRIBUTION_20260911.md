# R1 matched-parent incremental-alpha attribution — 2026-09-11

Status: **COMPLETE / ATTRIBUTION ONLY / NO HORIZON SELECTED / NO INSTRUMENT MAPPING**

This study asks whether R1 adds return beyond generic continuation of an otherwise similar intact parent trend. Each R1 event is paired to a results-blind matched parent-state clock with the same year, parent direction and 30-minute clock bucket, then nearest-neighbor matched on causal parent drift, path efficiency, parent age and local volatility.

## Frozen boundary

Freeze: `docs/governance/R1_INCREMENTAL_ALPHA_ATTRIBUTION_FREEZE@1.0.json`  
Freeze SHA256: `f1f4359ddfd55af438797c1b58b66de6c0fc192d146ab7cd1100490912f95b89`  
Code commit at run: `5a7256fb64999f6fdffb86ede544526886cce796`

No return, MFE/MAE, option, ETF, futures, cost, probability, year/side filter or horizon winner is used to create the controls. Control matching is with replacement and never relaxes the exact stratum after results are known.

## Matching quality

### CSI1000 matching quality

| Cell | eligible | matched | coverage | unique controls | median distance | p90 distance |
|---|---:|---:|---:|---:|---:|---:|
| R1_A | 1296 | 1296 | 100.0% | 1205 | 0.502 | 1.610 |
| R1_B | 545 | 545 | 100.0% | 534 | 0.144 | 1.413 |

### STAR50 matching quality

| Cell | eligible | matched | coverage | unique controls | median distance | p90 distance |
|---|---:|---:|---:|---:|---:|---:|
| R1_A | 1802 | 1802 | 100.0% | 1625 | 0.573 | 1.871 |
| R1_B | 729 | 729 | 100.0% | 711 | 0.239 | 1.353 |

## Incremental return results

### CSI1000 / 000852.SH

| Cell | h | matched/eligible | event mean bp | control mean bp | incremental mean bp | incremental median bp | pair+ | bootstrap 95% bp | +years | LONG inc bp | SHORT inc bp | strong |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| R1_A | 1 | 1296/1296 | +0.54 | +1.01 | -0.47 | +0.20 | 50.7% | [-1.24, +0.31] | 2/5 | -0.14 | -0.78 | no |
| R1_A | 5 | 1296/1296 | +2.11 | +0.95 | +1.16 | -0.22 | 49.4% | [-0.65, +2.93] | 4/5 | +0.45 | +1.83 | no |
| R1_A | 15 | 1296/1296 | +4.80 | +0.95 | +3.85 | +0.10 | 50.2% | [+0.80, +6.88] | 4/5 | +3.96 | +3.73 | YES |
| R1_A | 30 | 1296/1296 | +6.80 | +0.72 | +6.07 | +0.17 | 50.2% | [+1.38, +10.66] | 5/5 | +5.47 | +6.65 | YES |
| R1_A | 60 | 1296/1296 | +6.41 | -0.77 | +7.19 | -0.41 | 49.4% | [-0.30, +14.92] | 3/5 | +11.37 | +3.19 | no |
| R1_A | 120 | 1296/1296 | +5.79 | -0.33 | +6.12 | -1.92 | 47.1% | [-4.25, +16.86] | 2/5 | +11.13 | +1.34 | no |
| R1_A | 240 | 1296/1296 | +4.65 | +0.74 | +3.91 | -2.52 | 46.0% | [-12.45, +20.82] | 2/5 | +15.93 | -7.57 | no |
| R1_B | 1 | 545/545 | +0.48 | +1.51 | -1.03 | -0.59 | 45.1% | [-1.99, -0.12] | 1/5 | -0.93 | -1.12 | no |
| R1_B | 5 | 545/545 | +0.33 | +3.07 | -2.74 | -2.64 | 43.3% | [-5.13, -0.26] | 0/5 | -3.43 | -2.06 | no |
| R1_B | 15 | 545/545 | +2.09 | +3.87 | -1.78 | -2.71 | 40.2% | [-5.76, +2.32] | 1/5 | -3.99 | +0.39 | no |
| R1_B | 30 | 545/545 | +6.17 | +7.63 | -1.45 | -2.44 | 44.2% | [-6.79, +3.91] | 2/5 | -3.46 | +0.52 | no |
| R1_B | 60 | 545/545 | +7.65 | +10.44 | -2.79 | -3.99 | 41.3% | [-10.88, +7.06] | 1/5 | -0.94 | -4.60 | no |
| R1_B | 120 | 545/545 | +11.03 | +17.91 | -6.87 | -4.02 | 41.8% | [-19.18, +7.22] | 1/5 | -1.55 | -12.10 | no |
| R1_B | 240 | 545/545 | +23.43 | +34.63 | -11.20 | -3.63 | 40.9% | [-33.34, +12.11] | 3/5 | -3.19 | -19.06 | no |

### STAR50 / 000688.SH

| Cell | h | matched/eligible | event mean bp | control mean bp | incremental mean bp | incremental median bp | pair+ | bootstrap 95% bp | +years | LONG inc bp | SHORT inc bp | strong |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| R1_A | 1 | 1802/1802 | +0.37 | -0.16 | +0.53 | +0.46 | 51.6% | [-0.24, +1.27] | 4/5 | +1.09 | +0.01 | no |
| R1_A | 5 | 1802/1802 | +1.37 | +0.11 | +1.26 | +0.78 | 51.1% | [-0.46, +2.93] | 4/5 | +1.82 | +0.74 | no |
| R1_A | 15 | 1802/1802 | +3.03 | +0.90 | +2.13 | -0.79 | 48.9% | [-0.89, +5.08] | 3/5 | +4.41 | +0.00 | no |
| R1_A | 30 | 1802/1802 | +4.12 | +1.95 | +2.18 | -1.30 | 48.7% | [-1.90, +6.39] | 3/5 | +3.27 | +1.16 | no |
| R1_A | 60 | 1802/1802 | +2.50 | +2.89 | -0.39 | -1.68 | 48.6% | [-6.48, +6.00] | 2/5 | +8.04 | -8.25 | no |
| R1_A | 120 | 1802/1802 | +1.39 | +1.36 | +0.03 | -2.68 | 48.1% | [-9.39, +10.32] | 2/5 | +22.44 | -20.85 | no |
| R1_A | 240 | 1802/1802 | +4.41 | +2.23 | +2.18 | -1.63 | 48.7% | [-13.98, +19.78] | 2/5 | +43.99 | -36.77 | no |
| R1_B | 1 | 729/729 | +0.13 | +0.98 | -0.85 | -1.02 | 46.5% | [-2.33, +0.79] | 1/5 | -0.89 | -0.82 | no |
| R1_B | 5 | 729/729 | -1.60 | +1.08 | -2.69 | -2.56 | 43.8% | [-5.81, +0.41] | 0/5 | -1.41 | -3.74 | no |
| R1_B | 15 | 729/729 | -0.07 | +2.09 | -2.16 | -3.55 | 44.3% | [-7.45, +3.01] | 1/5 | +0.19 | -4.10 | no |
| R1_B | 30 | 729/729 | +0.76 | +3.22 | -2.46 | -4.04 | 42.7% | [-9.02, +3.95] | 2/5 | -2.25 | -2.63 | no |
| R1_B | 60 | 729/729 | +1.80 | +0.70 | +1.10 | -2.19 | 47.1% | [-9.22, +13.56] | 2/5 | +6.88 | -3.69 | no |
| R1_B | 120 | 729/729 | +5.70 | +3.47 | +2.22 | -3.06 | 45.4% | [-13.79, +20.88] | 2/5 | +8.56 | -3.01 | no |
| R1_B | 240 | 729/729 | +18.19 | +19.33 | -1.14 | -2.09 | 46.6% | [-26.27, +28.11] | 2/5 | +1.09 | -2.97 | no |

A `strong` flag is horizon-local only. It requires >=80% match coverage, positive pooled paired mean, a positive event-day-cluster-bootstrap 95% lower bound, positive annual incremental mean in >=4/5 years, and positive LONG and SHORT incremental means when both sides have >=30 events. It does **not** authorize choosing that horizon.

Common strong incremental horizons across both indices: `{'R1_A': [], 'R1_B': []}`

## Price-path attribution

### CSI1000 / 000852.SH additive signed-log path attribution

#### R1_A

| Segment | event mean bp | control mean bp | incremental mean bp |
|---|---:|---:|---:|
| 0→1 bars | +0.54 | +1.01 | -0.47 |
| 1→5 bars | +1.57 | -0.06 | +1.63 |
| 5→15 bars | +2.71 | +0.02 | +2.69 |
| 15→30 bars | +2.05 | -0.23 | +2.27 |
| 30→60 bars | -0.39 | -1.52 | +1.13 |
| 60→120 bars | -0.55 | +0.44 | -0.99 |
| 120→240 bars | -1.19 | +1.10 | -2.30 |

240-bar session decomposition:

| Component | event mean bp | control mean bp | incremental mean bp |
|---|---:|---:|---:|
| same_session | -0.28 | +2.36 | -2.64 |
| overnight | +1.74 | -2.30 | +4.04 |
| next_session | +3.28 | +0.71 | +2.57 |

Event median bars-to-MFE / MAE: **111.0 / 117.0**. MFE realized by 30/60/120 bars: **23.5% / 35.0% / 52.2%**.

#### R1_B

| Segment | event mean bp | control mean bp | incremental mean bp |
|---|---:|---:|---:|
| 0→1 bars | +0.48 | +1.51 | -1.03 |
| 1→5 bars | -0.14 | +1.56 | -1.70 |
| 5→15 bars | +1.76 | +0.78 | +0.98 |
| 15→30 bars | +4.09 | +3.72 | +0.37 |
| 30→60 bars | +1.46 | +2.82 | -1.36 |
| 60→120 bars | +3.41 | +7.43 | -4.02 |
| 120→240 bars | +12.39 | +16.26 | -3.87 |

240-bar session decomposition:

| Component | event mean bp | control mean bp | incremental mean bp |
|---|---:|---:|---:|
| same_session | +11.73 | +11.94 | -0.21 |
| overnight | +5.19 | +5.83 | -0.64 |
| next_session | +6.54 | +16.32 | -9.78 |

Event median bars-to-MFE / MAE: **132.0 / 104.0**. MFE realized by 30/60/120 bars: **23.1% / 31.4% / 46.8%**.


### STAR50 / 000688.SH additive signed-log path attribution

#### R1_A

| Segment | event mean bp | control mean bp | incremental mean bp |
|---|---:|---:|---:|
| 0→1 bars | +0.38 | -0.16 | +0.53 |
| 1→5 bars | +0.99 | +0.27 | +0.72 |
| 5→15 bars | +1.65 | +0.81 | +0.84 |
| 15→30 bars | +1.14 | +1.06 | +0.07 |
| 30→60 bars | -1.60 | +1.04 | -2.65 |
| 60→120 bars | -1.35 | -1.54 | +0.20 |
| 120→240 bars | +2.69 | +0.96 | +1.73 |

240-bar session decomposition:

| Component | event mean bp | control mean bp | incremental mean bp |
|---|---:|---:|---:|
| same_session | -4.08 | -4.76 | +0.68 |
| overnight | +4.22 | -0.94 | +5.17 |
| next_session | +3.74 | +8.14 | -4.40 |

Event median bars-to-MFE / MAE: **110.0 / 123.0**. MFE realized by 30/60/120 bars: **26.1% / 36.7% / 52.5%**.

#### R1_B

| Segment | event mean bp | control mean bp | incremental mean bp |
|---|---:|---:|---:|
| 0→1 bars | +0.13 | +0.98 | -0.85 |
| 1→5 bars | -1.75 | +0.09 | -1.84 |
| 5→15 bars | +1.54 | +1.01 | +0.53 |
| 15→30 bars | +0.84 | +1.13 | -0.29 |
| 30→60 bars | +0.76 | -2.49 | +3.25 |
| 60→120 bars | +3.56 | +2.74 | +0.82 |
| 120→240 bars | +11.61 | +15.08 | -3.46 |

240-bar session decomposition:

| Component | event mean bp | control mean bp | incremental mean bp |
|---|---:|---:|---:|
| same_session | -4.30 | +3.38 | -7.67 |
| overnight | +11.67 | +8.07 | +3.59 |
| next_session | +9.33 | +7.10 | +2.23 |

Event median bars-to-MFE / MAE: **127.0 / 108.0**. MFE realized by 30/60/120 bars: **23.5% / 34.7% / 48.1%**.


## Interpretation contract

If R1 remains positive relative to matched parent-state controls, the evidence supports a pullback-specific incremental alpha rather than merely generic parent-trend continuation. If the raw event return stays positive but paired incremental return does not, the prior price edge should instead be interpreted mainly as trend continuation.

This study still does not choose an ETF, futures contract, option structure or executable holding period. `BLACKBOX_query_count=3`; no query #4; `production_authority=false`.
