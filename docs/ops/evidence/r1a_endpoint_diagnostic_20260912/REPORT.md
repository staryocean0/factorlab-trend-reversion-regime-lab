# R1_A observed-endpoint price diagnostic

Decision: `ENDPOINT_DIAGNOSTIC_COMPLETE_DESCRIPTIVE`

This is a separate retrospective endpoint-conditional estimand. Original full-path v1 remains PARTIAL_CARRIER_TRANSPORT; no v1 gate or prior receipt was edited.

Freeze commit: `6687f9fa7000e02b03a0d5a7a4a65d9a63359116`; code commit: `dcc41db484c2fc5f8783aee9012c6de49484191c`.

Four positive-volume exact endpoints per pair/horizon remain mandatory. Interiors do not enter terminal-return algebra. No missing price is filled; no 2021 removal; no signal/control refit. Exit-availability conditioning is NOT a live entry rule.

## 512100.SH

| h | included/all | pooled coverage | worst-year coverage | ETF event bp | ETF control bp | ETF increment bp | same-sample index increment bp | increment residual bp | corr |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1271/1296 | 98.07% | 90.32% | +0.344 | +1.206 | -0.861 | -0.449 | -0.412 | +0.824 |
| 5 | 1268/1296 | 97.84% | 91.40% | +1.926 | +0.942 | +0.984 | +1.112 | -0.127 | +0.950 |
| 15 | 1268/1296 | 97.84% | 88.71% | +5.007 | +0.638 | +4.368 | +3.894 | +0.475 | +0.976 |
| 30 | 1259/1296 | 97.15% | 85.48% | +7.739 | +0.665 | +7.074 | +6.527 | +0.547 | +0.980 |
| 60 | 1261/1296 | 97.30% | 87.63% | +6.901 | -0.076 | +6.976 | +7.198 | -0.222 | +0.990 |
| 120 | 1265/1296 | 97.61% | 87.63% | +7.236 | +0.209 | +7.026 | +6.697 | +0.329 | +0.987 |
| 240 | 1261/1296 | 97.30% | 87.63% | +5.371 | +1.240 | +4.131 | +4.397 | -0.266 | +0.996 |

### Side, year and selection diagnostics

| h | LONG increment bp | SHORT increment bp | positive increment years | ETF event median bp | ETF event positive fraction | full-index increment bp | eligible-index increment bp | excluded-index increment bp |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | -0.479 | -1.221 | 1/5 | +0.000 | 37.29% | -0.467 | -0.449 | -1.350 |
| 5 | +0.620 | +1.332 | 3/5 | +0.000 | 47.24% | +1.160 | +1.112 | +3.324 |
| 15 | +4.795 | +3.970 | 4/5 | +4.041 | 52.13% | +3.845 | +3.894 | +1.658 |
| 30 | +6.237 | +7.855 | 5/5 | +7.454 | 53.61% | +6.074 | +6.527 | -9.333 |
| 60 | +10.607 | +3.607 | 3/5 | +4.063 | 50.99% | +7.188 | +7.198 | +6.801 |
| 120 | +12.692 | +1.700 | 2/5 | +0.000 | 49.09% | +6.123 | +6.697 | -17.287 |
| 240 | +15.655 | -6.667 | 2/5 | +0.000 | 49.41% | +3.908 | +4.397 | -13.741 |

Common-endpoint intersection: 1192/1296; gate pass=False; outcomes measured=False.

Annual common-endpoint coverage: `{"pooled": 0.9197530864197531, "2021": 0.6021505376344086, "2022": 0.9255663430420712, "2023": 0.9943820224719101, "2024": 0.9893048128342246, "2025": 0.9919678714859438}`.

## 588000.SH

| h | included/all | pooled coverage | worst-year coverage | ETF event bp | ETF control bp | ETF increment bp | same-sample index increment bp | increment residual bp | corr |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1802/1802 | 100.00% | 100.00% | +0.139 | -0.492 | +0.630 | +0.532 | +0.099 | +0.840 |
| 5 | 1802/1802 | 100.00% | 100.00% | +1.783 | -0.138 | +1.922 | +1.259 | +0.663 | +0.942 |
| 15 | 1802/1802 | 100.00% | 100.00% | +3.668 | +0.550 | +3.118 | +2.128 | +0.990 | +0.958 |
| 30 | 1801/1802 | 99.94% | 99.77% | +5.434 | +1.471 | +3.963 | +2.195 | +1.768 | +0.971 |
| 60 | 1801/1802 | 99.94% | 99.77% | +3.936 | +2.376 | +1.560 | -0.558 | +2.118 | +0.984 |
| 120 | 1802/1802 | 100.00% | 100.00% | +3.181 | +1.053 | +2.127 | +0.027 | +2.100 | +0.986 |
| 240 | 1801/1802 | 99.94% | 99.77% | +8.112 | +1.650 | +6.462 | +2.639 | +3.823 | +0.988 |

### Side, year and selection diagnostics

| h | LONG increment bp | SHORT increment bp | positive increment years | ETF event median bp | ETF event positive fraction | full-index increment bp | eligible-index increment bp | excluded-index increment bp |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | +1.510 | -0.189 | 4/5 | +0.000 | 34.18% | +0.532 | +0.532 | NA |
| 5 | +3.078 | +0.844 | 4/5 | +0.000 | 45.39% | +1.259 | +1.259 | NA |
| 15 | +5.196 | +1.183 | 3/5 | +0.000 | 48.45% | +2.128 | +2.128 | NA |
| 30 | +5.351 | +2.672 | 3/5 | +0.000 | 48.08% | +2.177 | +2.195 | -30.909 |
| 60 | +10.471 | -6.731 | 3/5 | +0.000 | 48.75% | -0.393 | -0.558 | +296.693 |
| 120 | +25.591 | -19.727 | 2/5 | +0.000 | 47.28% | +0.027 | +0.027 | NA |
| 240 | +48.719 | -32.938 | 2/5 | +0.000 | 47.36% | +2.178 | +2.639 | -829.249 |

Common-endpoint intersection: 1799/1802; gate pass=True; outcomes measured=True.

Annual common-endpoint coverage: `{"pooled": 0.9983351831298557, "2021": 1.0, "2022": 1.0, "2023": 1.0, "2024": 0.9931192660550459, "2025": 1.0}`.

| common-sample h | ETF event bp | ETF increment bp | same-sample index increment bp |
|---:|---:|---:|---:|
| 1 | +0.109 | +0.599 | +0.520 |
| 5 | +1.711 | +1.841 | +1.203 |
| 15 | +3.598 | +3.024 | +2.055 |
| 30 | +5.365 | +3.813 | +2.054 |
| 60 | +3.965 | +1.701 | -0.385 |
| 120 | +2.717 | +1.745 | -0.177 |
| 240 | +6.963 | +5.243 | +1.449 |

## Interpretation boundary

All seven horizons and both fixed carriers are reported, including unavailable cells. Per-horizon primary samples can differ. Use the composition audit and gated common-sample sensitivity before comparing horizon means; do not choose a winner.

Coverage is a reporting safeguard, not proof that missingness is random. ETF returns for excluded pairs remain unknown. These observed historical samples do not establish all-event alpha, causal identification, fresh OOS, statistical significance, net profits, borrow feasibility, or complete-path risk.

Source-recorded zero volume is not independently verified exchange no-trade. Canonical source time/corporate-action assumptions are inherited. No new upstream data was invented.

No MFE/MAE, stops or targets were computed. No BLACKBOX query #4. production_authority=false; fresh_oos=false.
