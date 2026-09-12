# Continue here — reversal / mean-reversion research

## Latest completed task

**`DEVELOPMENT_NOISE_ACCOUNTING_COMPLETED_NOT_ALPHA_TEST`**

The user-authorized real event/control noise decomposition has executed, not merely been proposed. R1_A remains an unconfirmed historical price lead. No new significance test, preferred horizon, confirmed trading edge or production permission was issued.

Read first:

1. `docs/research/R1A_DEVELOPMENT_NOISE_REVIEW_20260912.md`
2. `docs/ops/evidence/r1a_development_noise_20260912/REPORT.md`
3. `docs/ops/evidence/r1a_development_noise_20260912/noise_receipt.json`
4. `docs/governance/R1A_DEVELOPMENT_NOISE_DECOMPOSITION_FREEZE@1.0.json`
5. `research/r1a_development_noise/README.md`

Freeze `6315a8c8f0f31b34b02d40392ea2d5b484ad5f33`; decisive code `ea7baea732a8b664509b168937c9ab45b31f22ad`; Actions `34664796626`, job `103474436130`: SUCCESS.

## Scope and source boundary

CSI1000 uses the ORIGINAL Development period 2015-01-05..2020-12-31: 350,561 minutes, 1,462 dates, 1,752 eligible matched events, 1,482 unique controls. STAR50 uses only 2020-07-23..2020-12-31: 156 pairs on 110 dates, a short context check rather than full replication.

Only seven pre2021 index price partitions were read. No 2021-2025/ETF/MO/2026 price or return table was opened by this runner. Do not call the previous 2021-2025 paired Validation ledger a Development set. The old signal engine/thresholds and matching algorithm were reused unchanged inside the Development limits; the new DEV cohort does not replace old pairs. All seven horizons share the same pre2021, 240-bar-complete cohort.

## What was learned

Individual CSI1000 pairs, h15/h30:

| Quantity | h15 | h30 |
|---|---:|---:|
| Event SD, bp | 70.745 | 99.850 |
| Control SD, bp | 49.940 | 68.887 |
| Difference SD, bp | 82.659 | 114.823 |
| Event-control correlation | 0.0943 | 0.1113 |
| Event variance contribution | 73.25% | 75.62% |
| Control variance contribution | 36.50% | 35.99% |
| Covariance contribution | -9.75% | -11.61% |

These are empirical dispersions, NOT standard errors of a mean or identified unpredictable noise.

On the actual calendar, aggregate control legs concentrate on repeated/overlapping price intervals. The daily difference-variance accounting becomes event 21.00%/24.55%, control 82.68%/79.30%, covariance -3.68%/-3.85%. This different accounting unit does not contradict the individual-pair table and is not a calibrated mean-variance estimator.

25.34% of pairs use repeated control entries, maximum reuse 10. Control minute-weight energy is 2.96x/3.73x the sum of individual-control energies at h15/h30 under a hypothetical independent-equal-minute-shock reference. Distinct overlapping control intervals, not just identical IDs, are a large component. Do not call these measured real-market design effects.

The inherited control rule is retrospective: 38.13% of control entry indices occur later than their event; median absolute calendar separation is 49 trading days. About 20% of pairs also have overlapping event/control paths at h15/h30. No future-treatment exclusions or rematching were introduced to remove these cases.

The fixed year/direction/clock strata explain only 8.66%/7.36% of difference variance BETWEEN strata; most remains within. Group means are ex-post, not a causal predictor. Tail square concentration is reported without trimming. The measured unequal marginal scales imply only 1.50x/1.48x information from infinitely many independent controls in the expressly independent reference model, not a universal limit or an attained gain.

## Next boundary — control baseline, not another test formula

This accounting is complete. The generic estimator sweep remains closed. No new formal confirmation protocol or prospective clock is authorized.

Any next proposal should address the control baseline and exposure allocation using only information available at event time, limit or account for both exact and overlapping reuse, and preserve the intended event population or explicitly disclose non-identification. Coverage and covariate balance must be checked before outcomes. Changing the finite matched-pair contrast is a NEW measurement design; it cannot retroactively improve old p-values or turn an ex-post covariance decomposition into a tradable signal.

This round does not implement that redesign. Do not silently drop difficult events, dates, sides or horizons; do not choose control rules using Validation returns. No ETF/missing-price repair, signal refit, cost/stop/target/option/futures search is implied.

## Available data and retained authority

No local data-transfer task is outstanding: the 2021-2025 ETF CSV pack remains public under `data/r1a_carrier_prices/cloud_pack_v1/`. It was not needed for this pre2021 index-only noise decomposition.

Both ETF endpoint diagnostics remain completed; the separate original full-path v1 remains PARTIAL_CARRIER_TRANSPORT under its own definition. The failed primary all-seven-endpoint common cohort stays unopened. All original evidence, data, signals, Validation pairs and closes are intact.

A 2026 CSI1000 candidate exists in the overnight repository, with repeat-use metadata and unresolved R1_A exposure; it remains metadata-only. Do not claim no 2026 data exist or call it fresh holdout.

R1/R2 certifications and closed R1_B/R2-directional/MO identities are unchanged. Prior method and feasibility reviews remain available in docs/research, as history rather than competing latest instructions.

`BLACKBOX_query_count=3`; no #4; `production_authority=false`; `fresh_oos=false`; `confirmation_protocol_frozen=false`; `confirmation_clock_started=false`; `horizon_selected=false`.

## Reproduce only into a fresh directory

```bash
PYTHONPATH=src:. python -m pytest -q tests/test_r1a_development_noise.py tests/test_development_noise_retained.py
PYTHONPATH=src:. python research/r1a_development_noise/study.py --output /tmp/r1a-dev-noise-new
PYTHONPATH=src:. python research/r1a_development_noise/verify_replay.py --reference docs/ops/evidence/r1a_development_noise_20260912 --replay /tmp/r1a-dev-noise-new --output /tmp/r1a-dev-noise-audit.json
```

A separate narrow readonly regression workflow protects the Development-only input boundary and reproduces these eight tables; the existing broader historical-regression workflow remains intact. Reproduction is not new scientific evidence.
