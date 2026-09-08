# K-line recognizer transition policy v6 — result card

V6 modifies only recognizer A's state-switch policy. Classifier, features and frozen benchmark are unchanged.

## Selected transition policy

- candidate: `v6_t0r0e1x0`
- typed candidate available under point floors: `True`

- Trend -> Range: margin `0.05`, min probability `0.45`, confirmation `4` bars
- Range -> Trend: margin `0.05`, min probability `0.45`, confirmation `3` bars
- Enter Shock: margin `0.05`, min probability `0.55`, confirmation `2` bars
- Exit Shock: margin `0.05`, min probability `0.45`, confirmation `4` bars

Selection used only rolling pre-2025 folds (2022, 2023, 2024).

## Cross-validation worst-cell summary

- minimum balanced accuracy: `0.759`
- minimum macro F1: `0.760`
- minimum transition F1: `0.145`
- maximum false transitions/day: `1.434`

## 2025 consumed-data diagnostic

| Asset | Policy | Balanced accuracy | Macro F1 | Transition precision | Transition recall | Transition F1 | False transitions/day |
|---|---|---:|---:|---:|---:|---:|---:|
| 000852.SH | v6 selected | 0.824 | 0.814 | 0.104 | 0.468 | 0.170 | 1.317 |
| 000852.SH | v5 universal | 0.815 | 0.807 | 0.126 | 0.519 | 0.203 | 1.169 |
| 000688.SH | v6 selected | 0.784 | 0.784 | 0.103 | 0.442 | 0.167 | 1.222 |
| 000688.SH | v5 universal | 0.771 | 0.775 | 0.121 | 0.455 | 0.191 | 1.045 |

## Adjudication

Outcome: **v6_not_yet_useful**

Useful-improvement gates failed:
- 000852.SH: transition_f1 below v5
- 000852.SH: false_transitions_per_day not reduced
- 000688.SH: transition_f1 below v5
- 000688.SH: false_transitions_per_day not reduced

Stronger target not yet passed:
- 000852.SH: transition_f1 < 0.30
- 000852.SH: false_transitions_per_day > 0.80
- 000688.SH: transition_f1 < 0.30
- 000688.SH: false_transitions_per_day > 0.80

## Boundary

2025 was already consumed by earlier development and is diagnostic only. This result is about chart-state recognition, not trading profitability or fresh OOS performance.
