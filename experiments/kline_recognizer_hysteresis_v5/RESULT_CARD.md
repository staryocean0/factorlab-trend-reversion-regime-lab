# K-line recognizer hysteresis v5 — result card

V5 modifies the same recognizer A. It does not add another evaluator layer.

## Selected probability-switch policy

- switch margin: `0.05`
- minimum new-state probability: `0.45`
- confirmation bars: `4`
- point-state floor eligibility: `True`

Selection used only rolling pre-2025 folds (2022, 2023, 2024).

## Cross-validation worst-cell summary

- minimum balanced accuracy: `0.754`
- minimum macro F1: `0.756`
- minimum transition F1: `0.179`
- maximum false transitions/day: `1.240`

## 2025 consumed-data diagnostic (not a new holdout)

| Asset | Policy | Balanced accuracy | Macro F1 | Transition F1 | False transitions/day | Exact accuracy |
|---|---|---:|---:|---:|---:|---:|
| 000852.SH | v5 selected | 0.815 | 0.807 | 0.203 | 1.169 | 0.796 |
| 000852.SH | v4 policy | 0.857 | 0.842 | 0.140 | 1.753 | 0.843 |
| 000688.SH | v5 selected | 0.771 | 0.775 | 0.191 | 1.045 | 0.774 |
| 000688.SH | v4 policy | 0.815 | 0.810 | 0.139 | 1.671 | 0.817 |

## Interpretation boundary

The selected hysteresis parameters were not chosen on 2025. However 2025 was already inspected in v4, so the 2025 comparison is development diagnostic evidence only, not fresh OOS validation.
