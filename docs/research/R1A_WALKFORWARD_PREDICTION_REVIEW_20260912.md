# R1_A parent-baseline walk-forward prediction — completed diagnostic

## Decision

**WALKFORWARD_PREDICTION_DIAGNOSTIC_COMPLETED_NO_CONFIRMATION_AUTHORITY**.

The authorized fixed prediction experiment actually ran. Adding the unchanged R1_A indicator gives small pooled improvements at some horizons, but the former 15/30-bar lead is not consistently improved across years. The 60-bar comparison has positive improvement in all five years and both directions, yet the enhanced model is still worse than a zero-return forecast on that event sample. Do not promote 60 bars or claim a validated prediction edge. The fixed model comparison is complete; no automatic model/feature/lambda search follows.

This is neither a proof that R1_A contains no nonlinear information nor a causal attribution result. It is a limited, model-relative diagnostic on consumed Development history. It does not reopen closed matched-control/option identities or authorize fresh confirmation or trading.

Freeze commit: `606d25933debcdb986fb19b4489e5c61407b52b3`.
Freeze SHA256: `5e9e2b8f6afdee89e8d23c6bb9fc74a7400212f51f79e91290fb732b3280d3f7`.
Decisive code: `be103560415ccb4426a6c4ec79bd0df2af85d252`.
Actions: `34668445944`, job `103485041666`, SUCCESS.
Evidence: `docs/ops/evidence/r1a_walkforward_prediction_20260912/`.

## 1. What changed, and what did not

This changes the measurement question from an event-minus-selected-control return to the improvement in prediction error on the SAME realized event outcome. No new matched-control return was constructed. Both models see the same eligible historical training rows, with equal weight per row. The baseline has the four inherited parent-state covariates, direction and fixed information-clock indicators. The enhancement adds just one existing R1_A indicator.

A single linear-ridge family is used, with objective mean squared error plus `0.001 * sum(beta^2)` and an unpenalized intercept. All non-intercept columns, including the indicator, are standardized using training-only means and SDs. No interactions, severity predictors, new technical indicators, oversampling, winsorization or hyperparameter selection were performed.

The R1_A indicator is a deterministic summary of price history. The question is whether it adds predictive representation relative to THIS finite baseline feature set, not whether it creates information beyond the entire price history or identifies a treatment effect.

## 2. Source, clock and denominator audit

Exactly six hash-verified original CSI1000 2015-2020 price partitions were used: 350,561 minute observations. The eligible training population contains 1,752 original R1_A events plus 144,733 original eligible non-event parent-state observations, each once. The non-event pool excludes the prior 240-bar post-R1_A interval under its inherited definition; it is not every market minute.

The 645 events with information time in 2015 are warm-up and remain explicitly unscored. The remaining 1,107 events in information years 2016-2020 are ALL scored at EVERY horizon, yielding 7,749 event-horizon forecasts. Their original identities and four parent features were checked against the pinned Development ledger. There are no dropped hard-to-predict or out-of-range evaluation events.

At each year boundary, train on expanding prior history, then hold the two fitted models fixed throughout that year. Labels are admitted separately for each horizon only if `entry+h <= fold_cutoff`. Entry remains the next observed close after causal confirmation. Fold assignment and time-of-day features use the information timestamp, not the later entry/exit clock.

Five actual price-prefix reconstructions reproduced all then-known event identities and pre-entry features with maximum feature difference ZERO. All 35 fold/horizon training audits satisfy label maturity; all 70 fits succeeded. These finite checks support the implementation but are not a general proof that every possible preprocessing or source convention is correct.

The inherited original cohort requires 240 remaining observed bars before the end of 2020. Warm-up and this terminal boundary are explicit; do not present this as every possible historical event or a prospective event-admission protocol. STAR50 was not fitted because its pre2021 context has no full prior-year warm-up. No ETF, post2020, 2026 or option price file was read.

## 3. Complete primary event results

MSE is in **bp squared** and RMSE in bp. A loss improvement is NOT incremental trading return. Positive relative MSE reduction means a smaller squared prediction error.

| Horizon | Events | Parent RMSE bp | Parent+R1_A RMSE bp | MSE improvement bp^2 | Relative MSE reduction | Positive years | Both directions improve |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 1,107 | 8.6605 | 8.6461 | +0.2500 | +0.3333% | 3/5 | yes |
| 5 | 1,107 | 34.0245 | 34.2373 | -14.5272 | -1.2549% | 1/5 | no |
| 15 | 1,107 | 53.8611 | 53.7847 | +8.2309 | +0.2837% | 3/5 | yes |
| 30 | 1,107 | 80.6114 | 80.4955 | +18.6596 | +0.2872% | 2/5 | no |
| 60 | 1,107 | 99.9529 | 99.6550 | +59.4781 | +0.5953% | 5/5 | yes |
| 120 | 1,107 | 144.1842 | 143.7854 | +114.8452 | +0.5524% | 4/5 | no |
| 240 | 1,107 | 206.4262 | 206.6967 | -111.7651 | -0.2623% | 4/5 | no |

Every year's and direction's scores, mean prediction, realized mean/median, mean error, MAE and reference losses are retained in `scores.csv`. No horizon was chosen from this table.

### Former 15/30-bar leads

| Evaluation information year | Events | h15 MSE improvement bp^2 | h30 MSE improvement bp^2 |
|---|---:|---:|---:|
| 2016 | 326 | +32.0692 | +132.9865 |
| 2017 | 96 | -1.5923 | -47.4022 |
| 2018 | 209 | -9.2769 | -89.3938 |
| 2019 | 201 | +0.1850 | -4.9973 |
| 2020 | 275 | +2.5877 | +5.6035 |

At h15, LONG/SHORT improvements are +10.6098/+5.8391 bp^2. At h30 they are +76.8273/-39.8243 bp^2. Thus positive pooled h30 improvement is not symmetric or repeatedly observed every year.

These Development scores are not comparable as new confirmations of the earlier 2021-2025 ETF increment estimates: dates, warm-up, denominator and the estimand differ. No old return table is revised.

## 4. Why 60 bars is not a promoted winner

h60 satisfies the predeclared DESCRIPTIVE consistency flag: positive pooled gain, at least four positive years and both directions positive. But its prediction MSEs are:

| Forecast | h60 event MSE bp^2 |
|---|---:|
| Always zero return | **9,915.8333** |
| Parent+R1_A | 9,931.1136 |
| Past mixed-training mean | 9,959.6858 |
| Parent model | 9,990.5916 |

The extra indicator improves a weak fitted baseline without beating the simplest zero forecast. It is not a sufficient demonstration of useful mean prediction. Zero is a prediction reference, not a trading or economic-profit test.

At h15/h30, the enhanced event MSE is slightly below both zero and the past mixed mean, but the incremental improvement lacks the stated year/side consistency. At h5/h120/h240 the enhanced event MSE is above both simple references. On the 134,247 non-event forward background observations, the parent model's pooled MSE is above zero at all seven horizons. This is evidence of limited benchmark quality in this fixed simple specification, not a license to search replacements until the old history looks favorable.

A model's average predicted return, its average bias and its MSE need not move together. For example, the indicator can reduce an overforecast in one period rather than predict a stronger positive trading return. Never translate the MSE gains into bp of alpha.

## 5. Support and concentration

For each horizon, two of the 1,107 evaluation events (0.1807%) have at least one continuous feature outside the prior mixed-training coordinate range; eleven (0.9937%) are outside the prior non-event coordinate range. No event lacks a prior same-direction/information-clock non-event stratum. Nearest standardized background distance is about 0.458 at the median and 1.410 at the 95th percentile. All such events remain in the forecast and score ledgers.

These diagnostics do NOT prove multivariate overlap, exchangeability, causal identification or faithful prediction outside the training support. Their purpose is disclosure, not a filter or a new pass gate.

The daily loss bookkeeping contains every one of 1,218 evaluation trading dates, including days with no event. It attributes the completed loss difference to its forecast information date, NOT to a tradable price-path portfolio. At h15/h30 the largest 1% of dates account for 29.86%/30.51% of total ABSOLUTE daily loss differences; the largest 5% account for 63.32%/59.70%. This is not the share of positive gains. Nothing was clipped or removed.

Fixed lag products are retained without converting them into a new SE or p-value. Sharing the same realized outcome improves the comparison's definition, but overlapping horizons and dependence remain; prior inferential-calibration problems are not automatically resolved.

## 6. End-of-experiment judgment

This bounded specification does not deliver a sufficiently clear, persistent predictive advantage to justify formal confirmation or execution. The observed improvements are small and uneven, and the apparently most consistent location fails a simple benchmark comparison. Preserve R1_A as an unconfirmed historical lead, not as a certified predictive strategy and not as universally disproved.

Do not turn h60 into a holding period, reverse the h5 signal, change the ridge penalty, add interactions, discard 2016/2018, reinterpret high-support cases as a new subgroup, or reopen 2026 data automatically. Additional scientific work would require an independently justified new question and explicit authorization, not a continuation of this fixed diagnostic until it passes.

## 7. Engineering and reproducibility

Eight CSV tables retain 12,264 all-original-event coverage rows, 7,749 forecasts, 252 event/context score groups, 8,526 daily rows, 35 lag rows, 35 fold audits, 1,225 parameter rows and five prefix checks. The receipt pins source identities and every evidence checksum.

The decisive artifact `10289796009` was also downloaded and checked independently: ZIP SHA256 `355033b2e12e61f378df726106d8f44bc060fdd474e57aa33e46956c54ba03cc`, all eight file hashes verified, all 126 event score groups independently reconciled from the forecast ledger, and all 32 new synthetic/retained-evidence tests passed locally. This is a result audit, not a second market sample.

`model_parameters.csv` stores a centered-coordinate intercept and feature centers/scales. `coefficient_raw` for a non-intercept feature acts on `(x-center)`. To write a fully uncentered formula, subtract `sum(coefficient_raw*center)` from the stored intercept. Prediction itself always uses the explicit standardized formula in `RidgeFit.predict`.

The retained workflow re-runs from the six source partitions in a fresh output directory and audits exact identities/counts/flags, while recording tightly bounded continuous floating-point differences. It never overwrites the decisive receipt. Original study files and closed results are unchanged.

## References

- Hyndman and Athanasopoulos, time-series cross-validation: https://otexts.com/fpp3/tscv.html
- Ridge objective: https://scikit-learn.org/stable/modules/linear_model.html#ridge-regression-and-classification
- Train-only preprocessing and leakage: https://scikit-learn.org/stable/common_pitfalls.html#data-leakage

The project's annual schedule, lambda, feature set and descriptive flags are declared design choices, not universal rules supplied by these references.

`BLACKBOX_query_count=3`; `production_authority=false`; `fresh_oos=false`; `confirmation_protocol_frozen=false`; `confirmation_clock_started=false`; `horizon_selected=false`.
