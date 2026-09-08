# K-line recognizer optimization v4 — protocol

Date frozen: 2026-09-08
Base evidence: v3 independent algorithmic judge
Goal: optimize the recognizer itself. Do not create another evaluator layer.

## 1. Architecture

Exactly two roles remain:

1. **Recognizer A** — the only object being improved.
2. **Fixed v3 independent judge** — frozen target/benchmark only. It is not modified, tuned, or wrapped by another judge.

No D/E/F evaluator chain is permitted in v4.

## 2. Data split

Use verified 5m data only; 2026 remains excluded.

Temporal roles:

- development/train: all eligible rows through 2022-12-31;
- model-selection validation: 2023-01-01 through 2024-12-31;
- final temporal holdout: 2025-01-01 through 2025-12-31.

The 2025 partition may not participate in feature selection, threshold tuning, model-family selection, regularization selection, confirmation/persistence tuning, or tie-breaking.

This is a within-history temporal holdout, not fresh OOS evidence.

## 3. Target

Use only the already-frozen v3 independent judge labels at their declared information-availability time.

Concrete targets:

- UpTrend
- DownTrend
- Range
- Shock

Uncertain labels do not become an extra fitted class; they are excluded from supervised fitting and reported separately in coverage audits.

## 4. Candidate recognizer families

Model selection is allowed, but the candidate menu is frozen before validation scoring.

Exactly these three families are allowed:

A. **Rule baseline**
- current causal feature/rule recognizer plus causal persistence decoder.

B. **Regularized multinomial linear classifier**
- standardized causal features;
- L2-regularized softmax;
- regularization candidates `C in {0.1, 1.0, 10.0}`.

C. **Diagonal Gaussian discriminant classifier**
- per-class standardized causal feature means/variances;
- variance floor `1e-6`;
- empirical class priors from training data.

No tree boosting, neural network, hidden-state model, or unregistered family may be added after seeing validation scores.

## 5. Frozen causal feature surface

The fitted candidates may use only already-available prefix-only K-line information:

- log_return_1
- abs_log_return_1
- signed_efficiency_6
- signed_efficiency_12
- bdci_12
- dii_12
- realized_volatility_12
- volatility_rank_prior480
- abs_return_rank_prior480
- body_to_range_ratio_6
- wick_imbalance_6
- close_location_value_6

No independent-judge geometry fields, future bars, oracle labels, P&L, strategy outcomes, or 2026 data may appear as input features.

## 6. Causal persistence tuning

For fitted families only, confirmation length may be selected from:

`{1, 2, 3}` eligible bars.

A confirmed state persists through raw model uncertainty until another concrete state reaches the selected confirmation length.

No other transition filter parameter is tuned in v4.

## 7. Selection objective

Select one single recognizer configuration on the 2023-2024 validation set using the following lexicographic objective across both assets separately:

1. maximize the minimum of the two assets' balanced accuracy;
2. then maximize the minimum of the two assets' macro F1;
3. then maximize the minimum of the two assets' transition F1;
4. then minimize mean false transitions/day;
5. final deterministic tie-breaker: simpler family order `rule < linear < diagonal_gaussian`, then smaller confirmation length, then smaller C.

Do not select on total P&L or pooled-only accuracy.

After selection, the winning family/hyperparameters/confirmation length are locked. That selected model may then be refit once on all eligible labeled data through 2024-12-31 (development + validation combined) before the 2025 holdout is evaluated. No configuration choice may be revisited after that refit.

## 8. Final holdout reporting

After selecting exactly one configuration and performing the allowed through-2024 refit, run once on 2025.

Report for each asset:

- n_scored
- balanced accuracy
- macro F1
- exact accuracy
- concrete coverage
- per-state precision/recall/F1/support
- transition precision/recall/F1
- false transitions/day

Also report train and validation metrics for context, but 2025 is the primary v4 result.

## 9. Success interpretation

V4 is considered a recognizer improvement only if, on 2025 for both assets separately:

- balanced accuracy >= 0.70;
- macro F1 >= 0.70;
- transition F1 >= 0.25;
- false transitions/day <= 0.70;

AND neither asset falls below the frozen v3 point-state balanced-accuracy benchmark by more than 0.03.

A failure is preserved; do not reopen the candidate menu after 2025 is seen.

## 10. Boundaries

- This is optimization of one recognizer, not construction of another analysis layer.
- V3 judge is frozen and unchanged.
- 2025 is temporal holdout within consumed history, not fresh OOS.
- No 2026, UK alert validation, profitability claim, production routing, or live trading.
