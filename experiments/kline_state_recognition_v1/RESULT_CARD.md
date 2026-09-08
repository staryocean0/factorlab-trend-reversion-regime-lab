# K-line state recognition v1 — result card

Primary project capability: **Level 2**

This score measures historical K-line state recognition against the frozen centered visual-reference judge. It is not a trading-profit score and not fresh OOS validation.

## Asset scorecard

| Asset | Balanced accuracy | Macro F1 | Concrete coverage | Transition F1 | Exact accuracy |
|---|---:|---:|---:|---:|---:|
| 000852.SH | 0.374 | 0.474 | 0.521 | 0.006 | 0.384 |
| 000688.SH | 0.381 | 0.473 | 0.512 | 0.013 | 0.361 |

## Maturity adjudication

Reason: end-to-end recognizer scored but Level-3 gates failed

Failed higher-level gates:
- 000852.SH: balanced_accuracy < 0.55
- 000852.SH: transition_F1 < 0.40
- 000852.SH: concrete coverage < 0.60
- 000688.SH: balanced_accuracy < 0.55
- 000688.SH: transition_F1 < 0.40
- 000688.SH: concrete coverage < 0.60

## Interpretation boundary

- Level 2: pipeline exists but recognition is not yet reliably useful by the frozen gates.
- Level 3: useful historical chart-state recognition on both indices.
- Level 4: strong and reasonably stable historical recognition on both indices.
- Level 5 cannot be awarded by this consumed-history study; it requires fresh or independently annotated evidence.

No production routing or live-trading authority is granted.
