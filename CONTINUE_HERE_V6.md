# Continue here — K-line recognizer transition policy v6

Date: 2026-09-08

Project rule: optimize recognizer A itself. Do not build evaluator-on-evaluator tool chains.

## Immutable upstream

- v3 independent judge result commit: `c6487eab13fca2cd79a0c1c30fbc41c4943eede5`
- v4 direct recognizer optimization result commit: `40e1a35bf134fd7eb9191a4537a9a2eea7f58a9c`
- v5 probability hysteresis result commit: `e4ddffd3c190ba18739587aabf73844b3daa2230`

Current best stable recognizer remains **v5**, not v6.

## V6 design

V6 kept the same v4/v5 linear classifier (`C=1.0`), same causal feature surface and same frozen v3 benchmark. It changed only A's switch policy.

Frozen menu before replay:
- 16 type-specific policies = 2 settings each for:
  - trend -> range;
  - range -> trend;
  - enter Shock;
  - exit Shock;
- plus the unchanged v5 universal policy as baseline.

Selection folds:
- train through 2021 -> validate 2022;
- train through 2022 -> validate 2023;
- train through 2023 -> validate 2024.

2025 was forbidden from selection and used only as already-consumed diagnostic evidence.

## Formal execution

- immutable market package validation: PASS;
- full repository pytest: 113 passed, 1 warning;
- formal v6 replay: PASS;
- v6 result commit: `9e5289e757116294e00a45bcd47cb7c76aeb85e1`;
- one-shot workflow removed after success.

Outputs:
`experiments/kline_recognizer_transition_policy_v6/`

## Selected v6 candidate

`v6_t0r0e1x0`

- Trend -> Range: margin 0.05, min probability 0.45, 4 bars;
- Range -> Trend: margin 0.05, min probability 0.45, 3 bars;
- Enter Shock: margin 0.05, min probability 0.55, 2 bars;
- Exit Shock: margin 0.05, min probability 0.45, 4 bars.

Pre-2025 worst-cell CV:
- balanced accuracy = 0.759;
- macro F1 = 0.760;
- transition F1 = 0.145;
- max false transitions/day = 1.434.

This is already worse on transition F1 than v5's pre-2025 worst-cell result (~0.179).

## 2025 consumed-data diagnostic

CSI1000:
- v6 balanced accuracy 0.824 vs v5 0.815;
- v6 macro F1 0.814 vs v5 0.807;
- v6 transition F1 0.170 vs v5 0.203;
- v6 false transitions/day 1.317 vs v5 1.169.

STAR50:
- v6 balanced accuracy 0.784 vs v5 0.771;
- v6 macro F1 0.784 vs v5 0.775;
- v6 transition F1 0.167 vs v5 0.191;
- v6 false transitions/day 1.222 vs v5 1.045.

Formal adjudication: `v6_not_yet_useful`.

## Interpretation

Type-specific fixed confirmation counts improved point-state scores slightly but made transition behavior worse. The manual transition-type confirmation route is therefore not promoted.

Do not keep tuning v6's four hand-written confirmation categories after seeing these results.

## Next recognizer-A step

Return to v5 as the active baseline and replace hand-written confirmation counts with a **causal Markov persistence filter inside A**:

- keep the same linear classifier emissions;
- learn a 4x4 state transition matrix from pre-validation frozen labels only;
- use online forward filtering (no future data, no centered smoothing) to combine current emission probabilities with learned state persistence;
- tune only a small frozen persistence-strength / emission-temperature menu on the same rolling 2022-2024 scheme;
- require any promoted candidate to beat or match v5 pre-2025 transition metrics while preserving point-state floors;
- 2025 remains diagnostic only and cannot select the model.

This is still one recognizer A. The frozen v3 judge remains only the benchmark/label source.
