# R5-B1 limited diagnostic result

Date: 2026-09-10

Adjudication: `R5_B1_limited_diagnostic_not_supported_close_B1`

## Exact input identity

Frozen source SHA256: `bea21fa9dd9532e21605511e07561b33d5569f86f69f5a487507531593b14c48`.
Rows: 70,114; dates: 2015-01-05..2020-12-31.
Current annual market partitions were not used; their exact equivalence to the frozen R5 single-file source remains unestablished.

## Diagnostic 1 — breadth across validation days

Supported: **True**.
Positive days: 267/487 (54.83%).
2019 total SSE gain: 26.5744727624.
2020 total SSE gain: 6.46012540028.
Top 10% positive-day concentration: 46.12%.

## Diagnostic 2 — anti-persistence monotonic shape

Supported: **False**.
Adjacent non-increasing slope steps: 3 / 4.
Spearman(anti-persistence, empirical slope): -0.7.
Strongest quintile more negative than weakest: True.

Validation pooled slopes by TRAIN-frozen anti-persistence quintile:

- Q1: n=7178, median anti=-0.063627197, slope=0.090478032
- Q2: n=4827, median anti=-0.034815464, slope=0.098045427
- Q3: n=3565, median anti=-0.019861613, slope=0.091382144
- Q4: n=3815, median anti=-0.0034426678, slope=0.05126875
- Q5: n=2043, median anti=0.017364184, slope=-0.0024427426

## Authority

- TRAIN/VALIDATION reusable evidence only.
- BLACKBOX not read or allocated.
- No PnL/Sharpe or trading mapping.
- `production_authority=false`.
