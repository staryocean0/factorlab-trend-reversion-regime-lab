# Pure index price-validity study — 2026-09-11

Status: **COMPLETE / PRICE-LAYER DIAGNOSTIC ONLY / NO INSTRUMENT IMPLEMENTATION**

This study fills the missing layer between certified R1/R2 mechanisms and instrument implementation. It asks only whether the causal signal direction is followed by favorable cash-index price movement. Synthetic SHORT returns are allowed for research even though the cash index itself is not shortable.

## Frozen design

- entry: next observed 1m close after causal event confirmation;
- primary outcome: zero-cost signed gross cash-index return;
- horizons: 1, 5, 15, 30, 60, 120, 240 observed 1m bars;
- report every horizon; no winner selection;
- LONG and SHORT sides reported separately;
- MFE/MAE reported on the same frozen horizons;
- CSI1000 primary reusable window: 2021–2025;
- STAR50 2021–2025 is a cross-index transport check, not a new mechanism certification;
- no cost, option, ETF, futures, probability threshold, sizing, stop, target, regime, time-of-day, or BLACKBOX search.

Freeze: `docs/governance/INDEX_PRICE_VALIDITY_FREEZE@1.0.json`  
Freeze SHA256: `1ccc32698b6b1097f2e5ae4f55542e8950d30a25fea638b067bad0b3988b25ba`  
Code commit at run: `c7434c2312d1d4ff83d78bdd9ceb0780a5d65e0c`

## Primary results

### CSI1000 / 000852.SH — VALIDATION_2021_2025

| Cell | h | n | mean bp | median bp | win | mean MFE bp | mean MAE bp | +years | LONG mean bp | SHORT mean bp | robust |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| R1_A | 1 | 1296 | +0.54 | +0.84 | 55.2% | +0.54 | +0.54 | 4/5 | +0.23 | +0.84 | YES |
| R1_A | 5 | 1296 | +2.11 | +2.24 | 55.4% | +10.88 | -8.13 | 4/5 | +0.85 | +3.31 | YES |
| R1_A | 15 | 1296 | +4.80 | +3.81 | 56.2% | +24.27 | -18.61 | 5/5 | +3.43 | +6.10 | YES |
| R1_A | 30 | 1296 | +6.80 | +5.24 | 56.0% | +38.36 | -29.82 | 5/5 | +4.71 | +8.80 | YES |
| R1_A | 60 | 1296 | +6.41 | +4.43 | 53.2% | +57.53 | -47.44 | 5/5 | +8.75 | +4.18 | YES |
| R1_A | 120 | 1296 | +5.79 | +0.30 | 50.2% | +81.65 | -71.86 | 4/5 | +9.85 | +1.92 | YES |
| R1_A | 240 | 1296 | +4.65 | -2.18 | 49.2% | +122.77 | -110.27 | 2/5 | +12.10 | -2.47 | no |
| R1_B | 1 | 545 | +0.48 | +0.58 | 52.7% | +0.48 | +0.48 | 4/5 | +0.83 | +0.15 | YES |
| R1_B | 5 | 545 | +0.33 | +1.27 | 52.8% | +10.07 | -8.75 | 5/5 | +0.31 | +0.36 | YES |
| R1_B | 15 | 545 | +2.09 | +0.60 | 50.6% | +23.88 | -20.38 | 2/5 | +3.64 | +0.56 | no |
| R1_B | 30 | 545 | +6.17 | +5.06 | 54.7% | +38.37 | -32.30 | 4/5 | +10.48 | +1.94 | YES |
| R1_B | 60 | 545 | +7.65 | +3.12 | 52.1% | +59.36 | -50.06 | 4/5 | +10.47 | +4.88 | YES |
| R1_B | 120 | 545 | +11.03 | +4.49 | 51.0% | +86.31 | -74.32 | 4/5 | +11.55 | +10.53 | YES |
| R1_B | 240 | 545 | +23.43 | +9.97 | 53.2% | +137.61 | -107.54 | 4/5 | +33.27 | +13.77 | YES |
| R2_A | 1 | 2064 | -0.18 | -0.37 | 47.6% | -0.18 | -0.18 | 2/5 | -0.08 | -0.29 | no |
| R2_A | 5 | 2064 | -1.36 | -0.82 | 47.7% | +8.81 | -10.38 | 1/5 | -0.18 | -2.52 | no |
| R2_A | 15 | 2064 | -2.25 | -2.64 | 46.8% | +20.54 | -23.72 | 1/5 | +0.45 | -4.92 | no |
| R2_A | 30 | 2064 | -4.35 | -3.11 | 47.0% | +32.31 | -37.03 | 1/5 | -3.36 | -5.34 | no |
| R2_A | 60 | 2064 | -6.31 | -5.34 | 46.7% | +46.95 | -55.96 | 0/5 | -3.94 | -8.65 | no |
| R2_A | 120 | 2064 | -10.63 | -7.67 | 46.7% | +70.01 | -84.68 | 0/5 | -2.94 | -18.22 | no |
| R2_A | 240 | 2064 | -17.43 | -12.85 | 47.0% | +101.89 | -126.27 | 0/5 | -8.37 | -26.39 | no |
| R2_B | 1 | 988 | -0.13 | -0.37 | 46.8% | -0.13 | -0.13 | 2/5 | +0.33 | -0.47 | no |
| R2_B | 5 | 988 | -1.47 | -0.82 | 47.9% | +9.37 | -10.79 | 1/5 | -0.42 | -2.22 | no |
| R2_B | 15 | 988 | -1.10 | -1.86 | 47.1% | +20.89 | -22.82 | 2/5 | +4.13 | -4.81 | no |
| R2_B | 30 | 988 | -4.74 | -3.56 | 46.0% | +32.02 | -36.62 | 2/5 | +1.74 | -9.34 | no |
| R2_B | 60 | 988 | -5.76 | -6.27 | 44.3% | +46.77 | -54.15 | 2/5 | +7.67 | -15.28 | no |
| R2_B | 120 | 988 | -13.37 | -10.83 | 44.0% | +64.18 | -78.23 | 1/5 | -0.99 | -22.15 | no |
| R2_B | 240 | 988 | -16.31 | -14.44 | 43.9% | +90.49 | -116.41 | 1/5 | +0.30 | -28.09 | no |

### STAR50 / 000688.SH — TRANSPORT_2021_2025

| Cell | h | n | mean bp | median bp | win | mean MFE bp | mean MAE bp | +years | LONG mean bp | SHORT mean bp | robust |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| R1_A | 1 | 1804 | +0.36 | +0.51 | 51.9% | +0.36 | +0.36 | 4/5 | +0.61 | +0.13 | YES |
| R1_A | 5 | 1804 | +1.37 | +2.28 | 53.9% | +13.52 | -11.70 | 4/5 | +1.00 | +1.71 | YES |
| R1_A | 15 | 1804 | +3.04 | +2.97 | 52.8% | +30.56 | -26.80 | 3/5 | +3.77 | +2.37 | no |
| R1_A | 30 | 1804 | +4.15 | +2.87 | 51.8% | +45.82 | -40.17 | 4/5 | +5.03 | +3.32 | YES |
| R1_A | 60 | 1804 | +2.51 | +0.72 | 50.5% | +67.05 | -61.72 | 3/5 | +8.87 | -3.42 | no |
| R1_A | 120 | 1803 | +1.37 | -1.02 | 49.8% | +96.37 | -92.14 | 1/5 | +14.56 | -10.94 | no |
| R1_A | 240 | 1802 | +4.41 | -7.48 | 48.1% | +146.28 | -138.49 | 2/5 | +22.23 | -12.19 | no |
| R1_B | 1 | 730 | +0.14 | +0.49 | 51.5% | +0.14 | +0.14 | 2/5 | +0.41 | -0.08 | no |
| R1_B | 5 | 730 | -1.57 | -0.66 | 48.8% | +13.23 | -14.55 | 0/5 | -0.28 | -2.63 | no |
| R1_B | 15 | 730 | -0.03 | +0.47 | 50.8% | +29.47 | -30.24 | 3/5 | -0.23 | +0.14 | no |
| R1_B | 30 | 730 | +0.74 | -0.51 | 49.5% | +43.68 | -44.59 | 3/5 | -4.11 | +4.76 | no |
| R1_B | 60 | 730 | +1.72 | +2.85 | 51.8% | +67.43 | -66.41 | 2/5 | +2.59 | +1.00 | no |
| R1_B | 120 | 730 | +5.60 | +1.38 | 50.3% | +99.35 | -96.15 | 4/5 | +11.50 | +0.70 | YES |
| R1_B | 240 | 729 | +18.19 | +1.69 | 50.5% | +160.38 | -140.42 | 4/5 | +25.55 | +12.10 | YES |
| R2_A | 1 | 2961 | -0.27 | -0.53 | 46.7% | -0.27 | -0.27 | 2/5 | -0.06 | -0.50 | no |
| R2_A | 5 | 2961 | -0.86 | -0.91 | 47.7% | +11.88 | -13.14 | 3/5 | +0.89 | -2.80 | no |
| R2_A | 15 | 2961 | -1.57 | -2.38 | 47.1% | +26.40 | -28.12 | 2/5 | +1.28 | -4.74 | no |
| R2_A | 30 | 2960 | -2.59 | -1.97 | 48.1% | +40.33 | -43.11 | 1/5 | +0.52 | -6.05 | no |
| R2_A | 60 | 2960 | -4.25 | -2.57 | 48.3% | +57.89 | -63.79 | 1/5 | -2.08 | -6.67 | no |
| R2_A | 120 | 2960 | -8.97 | -4.38 | 48.1% | +83.78 | -94.24 | 0/5 | -6.66 | -11.54 | no |
| R2_A | 240 | 2960 | -9.43 | -1.67 | 49.7% | +126.79 | -141.90 | 2/5 | -4.42 | -15.00 | no |
| R2_B | 1 | 1288 | -0.35 | -0.48 | 47.3% | -0.35 | -0.35 | 2/5 | +0.56 | -1.18 | no |
| R2_B | 5 | 1288 | -0.35 | -0.91 | 48.4% | +12.77 | -13.25 | 2/5 | +1.52 | -2.04 | no |
| R2_B | 15 | 1288 | +0.59 | -0.50 | 49.0% | +29.56 | -29.32 | 3/5 | +4.55 | -3.02 | no |
| R2_B | 30 | 1288 | -1.83 | -3.82 | 47.7% | +43.96 | -45.45 | 3/5 | +3.62 | -6.80 | no |
| R2_B | 60 | 1288 | +0.98 | -4.28 | 47.4% | +63.88 | -64.38 | 3/5 | +5.37 | -3.03 | no |
| R2_B | 120 | 1288 | -8.53 | -11.56 | 46.0% | +91.25 | -96.41 | 3/5 | -3.57 | -13.05 | no |
| R2_B | 240 | 1288 | -7.42 | +2.05 | 50.6% | +133.20 | -143.75 | 3/5 | -3.50 | -10.99 | no |

## Robust-edge flags

A `robust` flag is horizon-local only: positive pooled mean, positive pooled median, win rate >50%, positive annual mean in at least 4/5 years, and positive mean on both LONG and SHORT sides when each side has at least 30 events. It is **not** permission to select that horizon for trading.

- CSI1000 robust cells/horizons: `[{'cell': 'R1_A', 'horizon': 1, 'mean': 5.411212326210922e-05, 'median': 8.365303806801005e-05, 'win_rate': 0.5516975308641975, 'positive_annual_mean_years': 4}, {'cell': 'R1_A', 'horizon': 5, 'mean': 0.00021064932811767364, 'median': 0.00022397519059114135, 'win_rate': 0.5540123456790124, 'positive_annual_mean_years': 4}, {'cell': 'R1_A', 'horizon': 15, 'mean': 0.000479688830205793, 'median': 0.0003809466562573194, 'win_rate': 0.5617283950617284, 'positive_annual_mean_years': 5}, {'cell': 'R1_A', 'horizon': 30, 'mean': 0.0006799064499780474, 'median': 0.0005243515045139091, 'win_rate': 0.5601851851851852, 'positive_annual_mean_years': 5}, {'cell': 'R1_A', 'horizon': 60, 'mean': 0.0006413260097305344, 'median': 0.0004428881228532022, 'win_rate': 0.5316358024691358, 'positive_annual_mean_years': 5}, {'cell': 'R1_A', 'horizon': 120, 'mean': 0.0005790204682534412, 'median': 2.952520306970241e-05, 'win_rate': 0.5015432098765432, 'positive_annual_mean_years': 4}, {'cell': 'R1_B', 'horizon': 1, 'mean': 4.843314001813136e-05, 'median': 5.785101810740212e-05, 'win_rate': 0.5266055045871559, 'positive_annual_mean_years': 4}, {'cell': 'R1_B', 'horizon': 5, 'mean': 3.343620692067197e-05, 'median': 0.0001266633002376949, 'win_rate': 0.5284403669724771, 'positive_annual_mean_years': 5}, {'cell': 'R1_B', 'horizon': 30, 'mean': 0.00061729263635036, 'median': 0.0005063740233350877, 'win_rate': 0.5467889908256881, 'positive_annual_mean_years': 4}, {'cell': 'R1_B', 'horizon': 60, 'mean': 0.0007649307419898291, 'median': 0.0003120837638794782, 'win_rate': 0.5211009174311927, 'positive_annual_mean_years': 4}, {'cell': 'R1_B', 'horizon': 120, 'mean': 0.0011034782418870444, 'median': 0.0004485144657242479, 'win_rate': 0.5100917431192661, 'positive_annual_mean_years': 4}, {'cell': 'R1_B', 'horizon': 240, 'mean': 0.002343390801007395, 'median': 0.0009965815513119924, 'win_rate': 0.5321100917431193, 'positive_annual_mean_years': 4}]`
- STAR50 transport robust cells/horizons: `[{'cell': 'R1_A', 'horizon': 1, 'mean': 3.625311291216755e-05, 'median': 5.143467057128204e-05, 'win_rate': 0.5194013303769401, 'positive_annual_mean_years': 4}, {'cell': 'R1_A', 'horizon': 5, 'mean': 0.00013681431535354435, 'median': 0.00022799433467479702, 'win_rate': 0.5393569844789357, 'positive_annual_mean_years': 4}, {'cell': 'R1_A', 'horizon': 30, 'mean': 0.0004145303499262438, 'median': 0.0002868909466496872, 'win_rate': 0.5177383592017738, 'positive_annual_mean_years': 4}, {'cell': 'R1_B', 'horizon': 120, 'mean': 0.0005595645263568936, 'median': 0.00013778450199602998, 'win_rate': 0.5027397260273972, 'positive_annual_mean_years': 4}, {'cell': 'R1_B', 'horizon': 240, 'mean': 0.0018191814857064902, 'median': 0.0001686240279321627, 'win_rate': 0.50480109739369, 'positive_annual_mean_years': 4}]`
- horizons/cells with positive pooled mean on both indices: `['R1_A@1', 'R1_A@5', 'R1_A@15', 'R1_A@30', 'R1_A@60', 'R1_A@120', 'R1_A@240', 'R1_B@1', 'R1_B@30', 'R1_B@60', 'R1_B@120', 'R1_B@240']`

## Interpretation boundary

This result answers a narrower question than the earlier economic translations. A positive price edge means the signal contains directional information in the index path. It does not by itself prove ETF/futures/options executability after spreads, fees, T+1, borrow, basis, margin, or inventory constraints.

The earlier option failures remain valid instrument-mapping failures, but they do not override this price-layer evidence.

`BLACKBOX_query_count=3`; no query #4; `production_authority=false`.
