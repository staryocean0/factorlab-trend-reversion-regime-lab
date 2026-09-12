# R1_A parent-baseline walk-forward prediction

A completed model-relative prediction diagnostic on original consumed CSI1000 Development, not an attribution matching repair or independent confirmation.

Authority: `docs/governance/R1A_WALKFORWARD_PREDICTION_FREEZE@1.0.json`.
Interpretation: `docs/research/R1A_WALKFORWARD_PREDICTION_REVIEW_20260912.md`.

The original 1,752-event cohort is unchanged. Training includes each original event and each eligible non-event parent-state minute once, not selected matched controls. Both ridge models use identical rows and weights. The only added feature is R1_A. No interactions, new indicators, class balancing or lambda search.

2015 is warm-up (645 events); information years 2016-2020 contain 1,107 fully scored events at all seven horizons. At each year boundary only completed past labels enter fitting and normalization. Models stay fixed during the subsequent year. Forecast features use confirmation-time information. The original terminal 240-bar completeness boundary remains disclosed.

The primary quantity `(y-p_parent)^2-(y-p_enhanced)^2` is measured in **bp squared**, not excess return. Support flags never remove events. Zero/past-mean references, all years/sides, non-event context and daily concentration remain visible. No p-value or independent-sample claim is issued.

Results are small and uneven. h15/h30 reduce MSE by about 0.284%/0.287%, with positive improvement in 3/5 and 2/5 years. h60 is the only descriptive consistency flag but its enhanced MSE remains above the zero-return benchmark. No horizon or executable strategy is selected.

## Reproduce into a fresh directory

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=src:. \
  python research/r1a_walkforward_prediction/study.py --output /tmp/r1a-forward-new
PYTHONPATH=src:. python research/r1a_walkforward_prediction/verify_replay.py \
  --reference docs/ops/evidence/r1a_walkforward_prediction_20260912 \
  --replay /tmp/r1a-forward-new --output /tmp/r1a-forward-audit.json
PYTHONPATH=src:. python -m pytest -q tests/test_r1a_walkforward_prediction.py tests/test_walkforward_prediction_retained.py
```

Exactly six original CSI1000 2015-2020 source partitions are needed. No DataHub, ETF, 2021-2025 or 2026 input is needed. Preserve the sealed receipt.

Model parameters use a centered-coordinate intercept. The non-intercept `coefficient_raw` column acts on `(x-center)`; a fully uncentered intercept is `stored_intercept-sum(coefficient_raw*center)`. `RidgeFit.predict` uses the explicit standardized formula.

The limited additive model cannot rule out all nonlinear information. A positive relative score does not establish calibrated inference, causal effect, fresh OOS or economic profitability. The experiment is complete; no automatic model sweep or new confirmation run follows.
