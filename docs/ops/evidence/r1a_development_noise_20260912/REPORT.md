# Development actual difference-noise accounting

DEVELOPMENT_NOISE_ACCOUNTING_COMPLETED_NOT_ALPHA_TEST

Original CSI1000 Development 2015-2020; STAR50 short 2020 context only. No 2021-2025/ETF/2026 returns read.
Observed centered dispersion is not identified irreducible noise or a standard error of the mean.

| Symbol | h | n | Event SD bp | Control SD bp | Difference SD bp | Correlation | Covariance cancellation |
|---|---:|---:|---:|---:|---:|---:|---:|
| 000852.SH | 1 | 1752 | 11.371 | 8.984 | 14.025 | 0.0651 | 6.34% |
| 000852.SH | 5 | 1752 | 44.341 | 36.543 | 53.221 | 0.1447 | 14.21% |
| 000852.SH | 15 | 1752 | 70.745 | 49.940 | 82.659 | 0.0943 | 8.89% |
| 000852.SH | 30 | 1752 | 99.850 | 68.887 | 114.823 | 0.1113 | 10.40% |
| 000852.SH | 60 | 1752 | 146.928 | 99.927 | 170.086 | 0.0900 | 8.37% |
| 000852.SH | 120 | 1752 | 199.967 | 159.723 | 246.298 | 0.0757 | 7.38% |
| 000852.SH | 240 | 1752 | 303.988 | 236.876 | 377.672 | 0.0408 | 3.96% |
| 000688.SH | 1 | 156 | 11.500 | 15.665 | 20.891 | -0.1632 | -15.57% |
| 000688.SH | 5 | 156 | 29.709 | 27.658 | 42.052 | -0.0735 | -7.33% |
| 000688.SH | 15 | 156 | 44.844 | 42.803 | 62.285 | -0.0095 | -0.95% |
| 000688.SH | 30 | 156 | 60.443 | 54.926 | 78.698 | 0.0718 | 7.15% |
| 000688.SH | 60 | 156 | 89.732 | 79.500 | 125.975 | -0.1050 | -10.42% |
| 000688.SH | 120 | 156 | 133.225 | 97.435 | 165.288 | -0.0030 | -0.29% |
| 000688.SH | 240 | 156 | 210.496 | 158.290 | 256.401 | 0.0544 | 5.22% |

## Limits

Full-year nearest-control selection is retrospective, not an online control. It is reused unchanged for accounting only.
Calendar decomposition uses exact telescoping simple returns, allocates overnight changes to the next observed price date, and includes zero-exposure days.
Primitive weight-energy ratios assume independent equal-variance minute-return shocks; daily variance and lag cross-products are realized diagnostics, not calibrated inference.
Within/between-stratum components use future-complete group means and do not establish achievable causal variance reduction.
Counterfactual control-count tables impose zero event-control covariance and fixed correlations; no controls were added and no estimator was selected.
Signed/unsigned differences do not identify latent common market factors. No p-values, new alpha PASS, fitted residualization or confirmation launch.

BLACKBOX_query_count=3; production_authority=false; fresh_oos=false.
