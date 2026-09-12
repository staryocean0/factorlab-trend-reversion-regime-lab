# R1_A parent-baseline walk-forward prediction diagnostic

WALKFORWARD_PREDICTION_DIAGNOSTIC_COMPLETED_NO_CONFIRMATION_AUTHORITY

Original CSI1000 Development only. Annual expanding fits, 2015 warm-up, information years 2016-2020 scored.
Loss reduction is prediction-error improvement in bp^2, NOT extra trading return in bp. No calibrated significance or fresh-OOS claim.

| h | Events | Parent RMSE bp | Enhanced RMSE bp | MSE improvement bp^2 | Relative MSE change | Positive years | Both sides + |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 1107 | 8.6605 | 8.6461 | +0.2500 | +0.3333% | 3/5 | True |
| 5 | 1107 | 34.0245 | 34.2373 | -14.5272 | -1.2549% | 1/5 | False |
| 15 | 1107 | 53.8611 | 53.7847 | +8.2309 | +0.2837% | 3/5 | True |
| 30 | 1107 | 80.6114 | 80.4955 | +18.6596 | +0.2872% | 2/5 | False |
| 60 | 1107 | 99.9529 | 99.6550 | +59.4781 | +0.5953% | 5/5 | True |
| 120 | 1107 | 144.1842 | 143.7854 | +114.8452 | +0.5524% | 4/5 | False |
| 240 | 1107 | 206.4262 | 206.6967 | -111.7651 | -0.2623% | 4/5 | False |

## Limits

Both models are simple linear ridge on the same event/background mixture; the added indicator is only a global event-location term, not a nonlinear or interaction search.
Support flags never delete events. Coordinate ranges/nearest distances are not joint-support or exchangeability certificates.
The original event cohort has a terminal 240-bar completeness condition. Warm-up and unscored folds remain explicit; this is not all historical events or prospective admission.
Daily loss accounting retains overlaps and zero-event days. It is not an IID SE, a trading equity curve or a causal comparison.
Check zero/past-mean benchmark errors and yearly/side results before interpreting any relative gain. A weak parent model can make enhancement comparisons misleading.
No post2020/ETF/2026 prices were read. Existing selected-pair failures, source bytes and old results are unchanged.
No automatic refit, new candidate, execution experiment, confirmation clock or horizon selection follows this report.
