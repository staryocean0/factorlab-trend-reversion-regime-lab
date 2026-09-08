# K-line independent judge v3 — result card

Independent algorithmic agreement: **weak_independent_algorithmic_agreement**

This v3 judge is structurally different from the recognizer: it uses an 80-minute centered OHLC geometry view based on line fit, channel displacement/location, turning points and high-low range expansion. It does not use BDCI, DII, signed efficiency or realized volatility.

## Independent-judge score

| Asset | Balanced accuracy | Macro F1 | Concrete coverage | Transition F1 | Exact accuracy |
|---|---:|---:|---:|---:|---:|
| 000852.SH | 0.758 | 0.753 | 0.921 | 0.194 | 0.731 |
| 000688.SH | 0.756 | 0.734 | 0.940 | 0.161 | 0.712 |

## Same-family v2 internal score (context only)

| Asset | V2 balanced accuracy | V2 transition F1 |
|---|---:|---:|
| 000852.SH | 0.994 | 0.780 |
| 000688.SH | 0.991 | 0.720 |

## Adjudication

Reason: at least one frozen useful gate failed

Failed gates:
- 000852.SH: transition_f1 < 0.30
- 000688.SH: transition_f1 < 0.30

## Interpretation boundary

This is an independent **algorithmic** judge, not independent human annotation. A positive result supports robustness to a different chart description, but still does not establish human-equivalent recognition, fresh OOS validity, trading profitability, production routing, or Level 5.
