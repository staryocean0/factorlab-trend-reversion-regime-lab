# K-line recognizer temporal-blend v10 — result card

V10 integrates the retained v9 temporal-context contribution into the v5 champion. The v5 decoder remains unchanged.

## Champion before v10

- version: `v5_probability_hysteresis`
- result commit: `e4ddffd3c190ba18739587aabf73844b3daa2230`
- min balanced accuracy: `0.754`
- min macro F1: `0.756`
- min transition F1: `0.179`
- max false transitions/day: `1.240`

## Pre-2025 contribution-integration decision

V10 candidate passed promotion gate: **True**

- selected: `blend_h6_a0.30`
- temporal horizon: `6` bars
- blend alpha: `0.30`
- auxiliary C: `0.1`
- min balanced accuracy: `0.755`
- min macro F1: `0.759`
- min transition F1: `0.198`
- max false transitions/day: `1.207`

## 2025 consumed-data safety diagnostic

| Asset | Recognizer | Balanced accuracy | Macro F1 | Transition F1 | False transitions/day |
|---|---|---:|---:|---:|---:|
| 000852.SH | v10 blend | 0.814 | 0.811 | 0.231 | 1.091 |
| 000852.SH | v5 champion | 0.815 | 0.807 | 0.203 | 1.169 |
| 000688.SH | v10 blend | 0.789 | 0.791 | 0.220 | 1.016 |
| 000688.SH | v5 champion | 0.771 | 0.775 | 0.191 | 1.045 |

2025 safety veto: **False**

Champion update eligibility: **True**

## Governance boundary

The runner is forbidden from editing the champion registry. A champion change, if eligible, is a separate reviewed governance action.
2025 is already-consumed evidence and is not a fresh-OOS claim.
