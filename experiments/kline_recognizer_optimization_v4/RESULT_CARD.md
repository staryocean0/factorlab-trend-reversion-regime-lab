# K-line recognizer optimization v4 — result card

Outcome: **recognizer_not_yet_improved**

V4 directly optimizes one recognizer. The v3 independent judge is frozen as the target/benchmark; no new evaluator layer is introduced.

## Selected recognizer

- family: `linear`
- confirmation bars: `3`
- C: `1.0`

Selected only on 2023-2024 validation. The configuration was then locked, refit through 2024 when applicable, and evaluated once on 2025.

## Validation score used for selection

| Asset | Balanced accuracy | Macro F1 | Transition F1 | False transitions/day |
|---|---:|---:|---:|---:|
| 000852.SH | 0.846 | 0.840 | 0.154 | 1.762 |
| 000688.SH | 0.809 | 0.810 | 0.139 | 1.719 |

## 2025 temporal holdout

| Asset | Model | Balanced accuracy | Macro F1 | Transition F1 | False transitions/day | Exact accuracy |
|---|---|---:|---:|---:|---:|---:|
| 000852.SH | optimized | 0.857 | 0.842 | 0.140 | 1.753 | 0.843 |
| 000852.SH | v3 baseline | 0.750 | 0.740 | 0.121 | 0.757 | 0.702 |
| 000688.SH | optimized | 0.815 | 0.810 | 0.139 | 1.671 | 0.817 |
| 000688.SH | v3 baseline | 0.731 | 0.711 | 0.139 | 0.844 | 0.679 |

## Adjudication

Frozen improvement gates not all passed:
- 000852.SH: transition_f1 < 0.25
- 000852.SH: false_transitions_per_day > 0.70
- 000688.SH: transition_f1 < 0.25
- 000688.SH: false_transitions_per_day > 0.70

## Boundary

2025 is a temporal holdout inside already-consumed historical material, not fresh future OOS. This is chart-state recognition optimization, not a profitability or live-trading claim.
