# R1_A event-time control allocation — design only

CONTROL_ALLOCATION_DESIGN_SCREEN_COMPLETED_NO_OUTCOMES

No newly assigned event/control returns, p-values or noise estimates were calculated. Original event denominators and old ledgers are preserved.

| Symbol | Stage | Original events | Matched | Coverage | No past stratum | Outside caliper | Interval blocked |
|---|---|---:|---:|---:|---:|---:|---:|
| 000688.SH | PAST_CALIPER | 156 | 27 | 17.31% | 34 | 95 | 0 |
| 000688.SH | PAST_CALIPER_EXCLUSIVE | 156 | 17 | 10.90% | 34 | 95 | 10 |
| 000688.SH | PAST_NEAREST | 156 | 122 | 78.21% | 34 | 0 | 0 |
| 000852.SH | PAST_CALIPER | 1752 | 414 | 23.63% | 107 | 1231 | 0 |
| 000852.SH | PAST_CALIPER_EXCLUSIVE | 1752 | 241 | 13.76% | 107 | 1231 | 173 |
| 000852.SH | PAST_NEAREST | 1752 | 1645 | 93.89% | 107 | 0 | 0 |

## Primary design decisions

- 000688.SH: DESIGN_SCREEN_FAIL_NO_OUTCOMES; reasons ['INSUFFICIENT_COVERAGE', 'COVARIATE_BALANCE_OR_RETENTION_SHIFT']; coverage groups ['POOLED', 'YEAR_2020', 'SIDE_LONG', 'SIDE_SHORT', 'YEAR_SIDE_2020_LONG', 'YEAR_SIDE_2020_SHORT']; balance groups ['POOLED', 'YEAR_2020', 'SIDE_LONG', 'SIDE_SHORT', 'YEAR_SIDE_2020_LONG', 'YEAR_SIDE_2020_SHORT'].
- 000852.SH: DESIGN_SCREEN_FAIL_NO_OUTCOMES; reasons ['INSUFFICIENT_COVERAGE', 'COVARIATE_BALANCE_OR_RETENTION_SHIFT']; coverage groups ['POOLED', 'YEAR_2015', 'YEAR_2016', 'YEAR_2017', 'YEAR_2018', 'YEAR_2019', 'YEAR_2020', 'SIDE_LONG', 'SIDE_SHORT', 'YEAR_SIDE_2015_LONG', 'YEAR_SIDE_2015_SHORT', 'YEAR_SIDE_2016_LONG', 'YEAR_SIDE_2016_SHORT', 'YEAR_SIDE_2017_LONG', 'YEAR_SIDE_2017_SHORT', 'YEAR_SIDE_2018_LONG', 'YEAR_SIDE_2018_SHORT', 'YEAR_SIDE_2019_LONG', 'YEAR_SIDE_2019_SHORT', 'YEAR_SIDE_2020_LONG', 'YEAR_SIDE_2020_SHORT']; balance groups ['POOLED', 'YEAR_2015', 'YEAR_2016', 'YEAR_2017', 'YEAR_2018', 'YEAR_2019', 'YEAR_2020', 'SIDE_LONG', 'SIDE_SHORT', 'YEAR_SIDE_2015_LONG', 'YEAR_SIDE_2015_SHORT', 'YEAR_SIDE_2016_LONG', 'YEAR_SIDE_2016_SHORT', 'YEAR_SIDE_2017_LONG', 'YEAR_SIDE_2017_SHORT', 'YEAR_SIDE_2018_LONG', 'YEAR_SIDE_2018_SHORT', 'YEAR_SIDE_2019_LONG', 'YEAR_SIDE_2019_SHORT', 'YEAR_SIDE_2020_LONG', 'YEAR_SIDE_2020_SHORT'].

## All primary coverage groups

| Symbol | Group | Denominator | Matched | Coverage | Required | Balance pass |
|---|---|---:|---:|---:|---|---|
| 000688.SH | POOLED | 156 | 17 | 10.90% | True | False |
| 000688.SH | YEAR_2020 | 156 | 17 | 10.90% | True | False |
| 000688.SH | SIDE_LONG | 64 | 8 | 12.50% | True | False |
| 000688.SH | SIDE_SHORT | 92 | 9 | 9.78% | True | False |
| 000688.SH | YEAR_SIDE_2020_LONG | 64 | 8 | 12.50% | True | False |
| 000688.SH | YEAR_SIDE_2020_SHORT | 92 | 9 | 9.78% | True | False |
| 000852.SH | POOLED | 1752 | 241 | 13.76% | True | False |
| 000852.SH | YEAR_2015 | 645 | 35 | 5.43% | True | False |
| 000852.SH | YEAR_2016 | 326 | 30 | 9.20% | True | False |
| 000852.SH | YEAR_2017 | 96 | 31 | 32.29% | True | False |
| 000852.SH | YEAR_2018 | 209 | 50 | 23.92% | True | False |
| 000852.SH | YEAR_2019 | 201 | 51 | 25.37% | True | False |
| 000852.SH | YEAR_2020 | 275 | 44 | 16.00% | True | False |
| 000852.SH | SIDE_LONG | 919 | 133 | 14.47% | True | False |
| 000852.SH | SIDE_SHORT | 833 | 108 | 12.97% | True | False |
| 000852.SH | YEAR_SIDE_2015_LONG | 364 | 23 | 6.32% | True | False |
| 000852.SH | YEAR_SIDE_2015_SHORT | 281 | 12 | 4.27% | True | False |
| 000852.SH | YEAR_SIDE_2016_LONG | 176 | 20 | 11.36% | True | False |
| 000852.SH | YEAR_SIDE_2016_SHORT | 150 | 10 | 6.67% | True | False |
| 000852.SH | YEAR_SIDE_2017_LONG | 41 | 14 | 34.15% | True | False |
| 000852.SH | YEAR_SIDE_2017_SHORT | 55 | 17 | 30.91% | True | False |
| 000852.SH | YEAR_SIDE_2018_LONG | 81 | 24 | 29.63% | True | False |
| 000852.SH | YEAR_SIDE_2018_SHORT | 128 | 26 | 20.31% | True | False |
| 000852.SH | YEAR_SIDE_2019_LONG | 105 | 23 | 21.90% | True | False |
| 000852.SH | YEAR_SIDE_2019_SHORT | 96 | 28 | 29.17% | True | False |
| 000852.SH | YEAR_SIDE_2020_LONG | 152 | 29 | 19.08% | True | False |
| 000852.SH | YEAR_SIDE_2020_SHORT | 123 | 15 | 12.20% | True | False |

## Interpretation limits

Only PAST_CALIPER_EXCLUSIVE is the proposed design. The other two stages diagnose where availability is lost; they are not alternatives selected after failure.
PAST_CALIPER coverage is an upper bound on per-event admissibility under these exact past/year/stratum/scaling/caliper rules before interval competition. A greedy allocation failure is NOT proof that every allocator fails.
The 0.5 prefix-scale caliper, 80% coverage and 0.1 balance limits are predeclared project-specific screening criteria, not statistical significance or proof of exchangeability. All observed covariate variance ratios are also reported.
A control needs its entire 240-bar path to have ended by the event information cutoff. Normalization uses the same-year matured control prefix only. Outcomes of those controls are not read by the allocator.
The historical feature compiler reuses the existing structural event engine, which uses close prices and structural first passage internally. This is not a claim of never loading post-event price rows; no NEW allocation return is evaluated.
Unit-incidence energies describe repeated clock use, not actual simple-return variance, realized noise reduction or independent information. Cross-pair event/control exposures may remain.
The fixed terminal-complete Development cohort is not fresh OOS, an online event-admission specification, or an identified full-population causal contrast. Missing matches stay visible, never zero-imputed.
CSI1000 is primary; STAR50 2020 is short context only. No ETFs, post2020 prices or 2026 candidate outcomes entered this study.
No signal/threshold/horizon change, no new significance test, no production promotion. Stop after this fixed screen; do not retune failed design settings.

BLACKBOX_query_count=3; production_authority=false; fresh_oos=false.
