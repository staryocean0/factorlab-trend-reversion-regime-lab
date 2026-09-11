# R1_A endpoint method review and empirical closeout

## Decision

Latest completed measurement: `ENDPOINT_DIAGNOSTIC_COMPLETE_DESCRIPTIVE`.

Program interpretation: **R1_A's short-horizon price response and matched-parent increment are visible in observed ETF endpoints; robustness and execution remain unestablished.**

The original full-path `PARTIAL_CARRIER_TRANSPORT` result is unchanged. It is a historical answer to a different, stricter observability requirement, not a blocker to mislabel as an endpoint alpha failure.

## Why a separate protocol was justified

For an unchanged pair and fixed horizon h:

`delta_h = d*(ETF[e+h]/ETF[e]-1) - d*(ETF[c+h]/ETF[c]-1)`.

Only four ETF endpoint prices appear. Interior missing/zero-volume observations do not enter this terminal-return identity. They do matter for complete-path extrema, MFE/MAE or a path-triggered exit. The original protocol tied those estimands together by requiring every event and control minute through 240 observations to have positive-volume prices.

The new protocol therefore separates terminal measurement from full-path measurement. It does not fill missing endpoints, manufacture positive volume or claim a full-path PASS. The old freeze/runner/receipts and all delivered CSV bytes were retained untouched.

**The new diagnostic changes the estimand and sampling contract.** Its annual 95% check is record coverage, not the old positive-volume coverage check. Zero-volume records count only as records, never as usable return endpoints. Both the pooled and each-year endpoint-pair reporting threshold remain 80%. This is not a claim that the old 95% positive-volume requirement passed.

Each horizon uses its own four-endpoint eligible pairs. Index comparators are recomputed on exactly those pairs. A second prespecified sensitivity intersects eligibility across all seven horizons and is reported only when its own pooled/per-year 80% rule passes.

## Freeze and execution

- Freeze: `docs/governance/R1A_ENDPOINT_PRICE_DIAGNOSTIC_FREEZE@1.0.json`.
- Freeze commit: `6687f9fa7000e02b03a0d5a7a4a65d9a63359116`.
- Freeze SHA256: `1a323e101136228cbe58df0710e5c4ef04c52726a6deeffcf003024672a2344a`.
- Decisive code commit: `dcc41db484c2fc5f8783aee9012c6de49484191c`.
- GitHub Actions run: `34630965766`; job `103367406954`: SUCCESS.
- 17 new synthetic endpoint tests and existing carrier boundary tests ran before outcomes.
- Complete evidence: `docs/ops/evidence/r1a_endpoint_diagnostic_20260912/REPORT.md` and `endpoint_receipt.json`.

The freeze explicitly records that prior index and STAR50 ETF outcomes and source coverage had already been seen. New CSI1000 ETF endpoint returns had not been measured before this freeze. This remains reused historical research, not fresh independent OOS.

## CSI1000 / 512100.SH

All seven horizon-specific endpoint reporting gates passed. Pooled coverage ranges 97.15%-98.07%; the worst year/horizon is 85.48%, above the fixed new 80% pair gate. No year was removed.

| Index observation bars | Pairs / 1296 | ETF event mean bp | ETF control mean bp | ETF increment bp | Identical-sample index increment bp |
|---:|---:|---:|---:|---:|---:|
| 1 | 1271 | +0.344 | +1.206 | -0.861 | -0.449 |
| 5 | 1268 | +1.926 | +0.942 | +0.984 | +1.112 |
| 15 | 1268 | +5.007 | +0.638 | +4.368 | +3.894 |
| 30 | 1259 | +7.739 | +0.665 | +7.074 | +6.527 |
| 60 | 1261 | +6.901 | -0.076 | +6.976 | +7.198 |
| 120 | 1265 | +7.236 | +0.209 | +7.026 | +6.697 |
| 240 | 1261 | +5.371 | +1.240 | +4.131 | +4.397 |

At 15/30 bars, positive incremental annual means occur in 4/5 and 5/5 years. LONG increments are +4.795/+6.237bp; synthetic SHORT increments +3.970/+7.855bp. ETF event-return medians are +4.041/+7.454bp and positive fractions 52.13%/53.61%. These are descriptive facts, not a selected 15/30-bar holding rule or a new significance declaration.

The very short 1-bar increment is negative; the 240-bar synthetic SHORT increment is -6.667bp, and longer-horizon annual consistency is weaker. Do not claim that every direction/horizon is uniformly supported.

### Selection was checked, not assumed away

At 30 bars the full-original-pair index increment is +6.074bp, whereas the eligible subset is +6.527bp. Thus about +0.453bp of the difference is attributable to observable index sample composition; ETF transport contributes a further approximately +0.547bp to reach +7.074bp. Excluded-pair index increments are -9.333bp on average. These observations require selection caution even with high pooled coverage.

At 15 bars full-index/eligible-index/ETF increments are +3.845/+3.894/+4.368bp. The observable composition shift is smaller there. Neither comparison identifies missing ETF outcomes or proves the sample is random.

The all-seven-endpoint common intersection is 1192/1296 overall (91.98%) but only 60.22% in 2021. Its frozen common-sample gate FAILS. **No primary common-sample ETF return table was opened.** Horizon-specific rows must not be plotted/interpreted as if they were all the same cohort or used to select a winner.

## STAR50 / 588000.SH

All seven horizon-specific gates passed with 1801-1802/1802 pairs. The 15/30-bar ETF increments are +3.118/+3.963bp versus same-sample index +2.128/+2.195bp. Both directional means are positive there, but positive incremental annual means are only 3/5 years at both locations.

The common-endpoint sensitivity passes with 1799/1802 pairs and every-year coverage >=99.31%. On that identical cohort 15/30-bar ETF increments are +3.024/+3.813bp versus index +2.055/+2.054bp. This is supportive secondary transport, not independent confirmation of CSI1000 alpha. Long horizons still exhibit strong LONG/SHORT asymmetry and weak annual consistency.

## What remains unresolved

1. Observation selection: eligible endpoints include future exit availability and are not a tradable entry screen. No MCAR/MAR assumption or all-event effect is identified.
2. Dependence and repeated research: overlapping holding windows, reused controls, historical research reuse and multiple horizons need a separately frozen robustness/inference treatment. This run intentionally adds no significance tests.
3. Source semantics: delivered canonical timestamps and action tables are inherited. Recorded volume=0 versus actual exchange no-trade remains unverified at the upstream level.
4. Trading implementation: zero-cost signed ETF close changes are not executable bid/ask PnL. No path risk, stop/target, T+1, borrow, inventory or costs were tested here.

The immediate research frontier is **dependence/selection robustness of the fixed R1_A endpoint surface**, not another ETF, a changed signal, a chosen horizon or an option payoff. No additional routine local data transfer is required.

## Reproduction

```bash
PYTHONPATH=src:. python research/r1a_carrier_transport/endpoint_diagnostic.py --output /tmp/r1a-endpoint-new
```

Use a fresh output directory; preserve decisive evidence. The original full-path runner remains available under its own unchanged freeze.

Implementation reference for exact reindexing with missing values retained: pandas official documentation, https://pandas.pydata.org/pandas-docs/version/2.2/reference/api/pandas.DataFrame.reindex.html . Filling methods are not used.

`BLACKBOX_query_count=3`; no query #4; `production_authority=false`; `fresh_oos=false`. R1_B, R2 directional and closed MO identities are not reopened.
