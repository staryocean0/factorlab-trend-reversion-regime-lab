# R1_A bounded method calibration and information review

Decision: `BOUNDED_SYNTHETIC_METHOD_REVIEW_COMPLETED_NO_CONFIRMATION_AUTHORITY`.

Freeze `3032c6567b15c7df705f09101d63ba1caeadd4d1`; code `bd1b4b7fac45bf5075be84a4a666287df4a411b9`; Actions `34662714569`.

All outcomes below are synthetic; the actual R1_A means were not retested. Seven predeclared DGPs, 28 designs and 2,000 shared-family replicates per DGP. No 2026 data, market OHLC columns or return ledgers read.

## Fixed method screen

| Method | Severe marginal cells | Severe family cells | Max joint MC upper | Screen pass |
|---|---:|---:|---:|---|
| GRAPH_T_BASELINE | 109 | 12 | 40.75% | False |
| EXPOSURE_SCORE_HAC6 | 26 | 2 | 11.76% | False |
| FIVE_YEAR_GROUP_T | 28 | 0 | 6.15% | False |
| ORACLE_MEAN_NORMAL_REFERENCE | 0 | 0 | 2.31% | False |

The known-covariance oracle is never eligible for the screen. Passing a finite simulation screen would not establish market validity.

## Nominal 5% pointwise null rejection ranges across 28 designs

| Model | Method | Minimum | Maximum |
|---|---|---:|---:|
| IID_GAUSSIAN | GRAPH_T_BASELINE | 3.65% | 4.25% |
| IID_GAUSSIAN | EXPOSURE_SCORE_HAC6 | 0.90% | 1.65% |
| IID_GAUSSIAN | FIVE_YEAR_GROUP_T | 4.45% | 5.15% |
| IID_GAUSSIAN | ORACLE_MEAN_NORMAL_REFERENCE | 4.70% | 5.80% |
| BLOCK_GAUSSIAN_RHO0 | GRAPH_T_BASELINE | 4.60% | 6.45% |
| BLOCK_GAUSSIAN_RHO0 | EXPOSURE_SCORE_HAC6 | 1.20% | 3.40% |
| BLOCK_GAUSSIAN_RHO0 | FIVE_YEAR_GROUP_T | 4.40% | 5.75% |
| BLOCK_GAUSSIAN_RHO0 | ORACLE_MEAN_NORMAL_REFERENCE | 4.15% | 5.45% |
| BLOCK_GAUSSIAN_RHO06 | GRAPH_T_BASELINE | 7.55% | 22.65% |
| BLOCK_GAUSSIAN_RHO06 | EXPOSURE_SCORE_HAC6 | 2.20% | 5.45% |
| BLOCK_GAUSSIAN_RHO06 | FIVE_YEAR_GROUP_T | 5.20% | 7.00% |
| BLOCK_GAUSSIAN_RHO06 | ORACLE_MEAN_NORMAL_REFERENCE | 4.15% | 5.55% |
| BLOCK_GAUSSIAN_RHO09 | GRAPH_T_BASELINE | 18.55% | 50.30% |
| BLOCK_GAUSSIAN_RHO09 | EXPOSURE_SCORE_HAC6 | 6.15% | 19.85% |
| BLOCK_GAUSSIAN_RHO09 | FIVE_YEAR_GROUP_T | 9.30% | 16.00% |
| BLOCK_GAUSSIAN_RHO09 | ORACLE_MEAN_NORMAL_REFERENCE | 4.70% | 6.05% |
| BLOCK_T5_RHO06 | GRAPH_T_BASELINE | 7.85% | 22.70% |
| BLOCK_T5_RHO06 | EXPOSURE_SCORE_HAC6 | 2.20% | 5.45% |
| BLOCK_T5_RHO06 | FIVE_YEAR_GROUP_T | 4.70% | 6.30% |
| BLOCK_T5_RHO06 | ORACLE_MEAN_NORMAL_REFERENCE | 4.30% | 5.65% |
| HETEROSKEDASTIC_BLOCK_RHO06 | GRAPH_T_BASELINE | 12.00% | 26.95% |
| HETEROSKEDASTIC_BLOCK_RHO06 | EXPOSURE_SCORE_HAC6 | 2.90% | 5.75% |
| HETEROSKEDASTIC_BLOCK_RHO06 | FIVE_YEAR_GROUP_T | 5.15% | 6.30% |
| HETEROSKEDASTIC_BLOCK_RHO06 | ORACLE_MEAN_NORMAL_REFERENCE | 4.90% | 6.05% |
| SIGNED_LEG_REUSE_RHO06 | GRAPH_T_BASELINE | 4.00% | 4.90% |
| SIGNED_LEG_REUSE_RHO06 | EXPOSURE_SCORE_HAC6 | 1.10% | 2.05% |
| SIGNED_LEG_REUSE_RHO06 | FIVE_YEAR_GROUP_T | 4.45% | 5.20% |
| SIGNED_LEG_REUSE_RHO06 | ORACLE_MEAN_NORMAL_REFERENCE | 4.40% | 5.55% |

## Joint familywise false rejection

| Model | Method | Index family14 | ETF family14 | Combined family28 |
|---|---|---:|---:|---:|
| IID_GAUSSIAN | GRAPH_T_BASELINE | 0.35% | 0.50% | 0.10% |
| IID_GAUSSIAN | EXPOSURE_SCORE_HAC6 | 0.10% | 0.15% | 0.05% |
| IID_GAUSSIAN | FIVE_YEAR_GROUP_T | 0.80% | 1.15% | 0.75% |
| IID_GAUSSIAN | ORACLE_MEAN_NORMAL_REFERENCE | 0.55% | 0.80% | 0.45% |
| BLOCK_GAUSSIAN_RHO0 | GRAPH_T_BASELINE | 1.70% | 1.95% | 1.10% |
| BLOCK_GAUSSIAN_RHO0 | EXPOSURE_SCORE_HAC6 | 0.90% | 0.90% | 0.60% |
| BLOCK_GAUSSIAN_RHO0 | FIVE_YEAR_GROUP_T | 1.55% | 2.05% | 1.35% |
| BLOCK_GAUSSIAN_RHO0 | ORACLE_MEAN_NORMAL_REFERENCE | 1.25% | 1.65% | 0.80% |
| BLOCK_GAUSSIAN_RHO06 | GRAPH_T_BASELINE | 10.95% | 11.75% | 8.90% |
| BLOCK_GAUSSIAN_RHO06 | EXPOSURE_SCORE_HAC6 | 2.15% | 2.40% | 1.40% |
| BLOCK_GAUSSIAN_RHO06 | FIVE_YEAR_GROUP_T | 1.70% | 1.75% | 1.20% |
| BLOCK_GAUSSIAN_RHO06 | ORACLE_MEAN_NORMAL_REFERENCE | 0.95% | 1.20% | 0.45% |
| BLOCK_GAUSSIAN_RHO09 | GRAPH_T_BASELINE | 37.40% | 38.60% | 34.55% |
| BLOCK_GAUSSIAN_RHO09 | EXPOSURE_SCORE_HAC6 | 9.90% | 10.35% | 8.40% |
| BLOCK_GAUSSIAN_RHO09 | FIVE_YEAR_GROUP_T | 4.35% | 5.10% | 2.85% |
| BLOCK_GAUSSIAN_RHO09 | ORACLE_MEAN_NORMAL_REFERENCE | 1.00% | 1.25% | 0.60% |
| BLOCK_T5_RHO06 | GRAPH_T_BASELINE | 11.15% | 11.80% | 9.15% |
| BLOCK_T5_RHO06 | EXPOSURE_SCORE_HAC6 | 1.90% | 2.15% | 1.55% |
| BLOCK_T5_RHO06 | FIVE_YEAR_GROUP_T | 2.25% | 2.50% | 1.75% |
| BLOCK_T5_RHO06 | ORACLE_MEAN_NORMAL_REFERENCE | 1.10% | 1.20% | 0.50% |
| HETEROSKEDASTIC_BLOCK_RHO06 | GRAPH_T_BASELINE | 12.70% | 13.35% | 10.00% |
| HETEROSKEDASTIC_BLOCK_RHO06 | EXPOSURE_SCORE_HAC6 | 1.40% | 1.60% | 0.90% |
| HETEROSKEDASTIC_BLOCK_RHO06 | FIVE_YEAR_GROUP_T | 1.35% | 1.70% | 1.05% |
| HETEROSKEDASTIC_BLOCK_RHO06 | ORACLE_MEAN_NORMAL_REFERENCE | 1.20% | 1.35% | 0.75% |
| SIGNED_LEG_REUSE_RHO06 | GRAPH_T_BASELINE | 0.70% | 0.70% | 0.35% |
| SIGNED_LEG_REUSE_RHO06 | EXPOSURE_SCORE_HAC6 | 0.35% | 0.35% | 0.20% |
| SIGNED_LEG_REUSE_RHO06 | FIVE_YEAR_GROUP_T | 1.05% | 1.30% | 0.65% |
| SIGNED_LEG_REUSE_RHO06 | ORACLE_MEAN_NORMAL_REFERENCE | 0.85% | 1.05% | 0.45% |

## Information efficiency: illustrative CSI1000 index locations, not selected horizons

| h | Assumed effect bp | One-year required noise reduction | Needed information multiple | Infinite balanced independent controls enough? |
|---:|---:|---:|---:|---|
| 15 | 2 | 98.66% | 74.77 | False |
| 15 | 4 | 94.65% | 18.69 | False |
| 15 | 6 | 87.96% | 8.31 | False |
| 30 | 2 | 99.50% | 201.06 | False |
| 30 | 4 | 98.01% | 50.27 | False |
| 30 | 6 | 95.52% | 22.34 | False |

In the explicit equal-variance independent-event/control model, infinitely many independent controls can remove at most half of paired noise (2x information). Correlated controls reduce that benefit. This is not a measured universal bound. Required reductions inherit the old planning assumptions and are not attained R-squared values.

## Limits and stopping rule

The exposure-score HAC is a duplicated-incidence adaptation, not a plug-in validity theorem. Group t relies on approximately independent group estimates and changes the target to equal-year means when effects differ. The oracle knows the simulated covariance and is unavailable in practice. Cross-block AR, heavy-tail, heteroskedastic and signed/reused-leg cases are stipulated scenarios, not fitted market truth.

Joint shocks are explicitly shared across horizons and layers; one stylized family dependence is tested, not every possible dependence. Abstentions and complete-family quantification are recorded. No bandwidth/group/DGP/seed/threshold was changed based on results.

The bounded method sweep ends here. No method is applied to historic R1_A means, no failed common-primary cohort is opened, and no prospective data are spent. Historical research conclusions and all old freezes remain unchanged.

`BLACKBOX_query_count=3`; `production_authority=false`; `fresh_oos=false`.
