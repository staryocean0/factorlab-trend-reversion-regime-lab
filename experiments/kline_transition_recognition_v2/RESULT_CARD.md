# K-line transition recognition v2 — result card

Primary project capability: **Level 4**

V2 keeps the v1 raw recognizer thresholds unchanged. The primary score aligns the centered offline judge to the time its six future bars are actually observable and applies the frozen two-bar causal persistence decoder.

## Primary availability-aligned score

| Asset | Balanced accuracy | Macro F1 | Concrete coverage | Transition F1 | Exact accuracy |
|---|---:|---:|---:|---:|---:|
| 000852.SH | 0.994 | 0.995 | 1.000 | 0.780 | 0.995 |
| 000688.SH | 0.991 | 0.992 | 1.000 | 0.720 | 0.993 |

## V1 baseline for comparison

| Asset | V1 balanced accuracy | V1 coverage | V1 transition F1 |
|---|---:|---:|---:|
| 000852.SH | 0.374 | 0.521 | 0.006 |
| 000688.SH | 0.381 | 0.512 | 0.013 |

## Adjudication

Reason: all frozen Level-4 gates passed

## Boundary

This is consumed historical development evidence. It measures chart-state recognition at matched information availability; it is not a trading-profit score, future-return predictor, production router, or Level-5 independent validation.
