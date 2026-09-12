# Actual Development difference-noise accounting

Read `docs/governance/R1A_DEVELOPMENT_NOISE_DECOMPOSITION_FREEZE@1.0.json` and `docs/research/R1A_DEVELOPMENT_NOISE_REVIEW_20260912.md`.

The runner uses only the original CSI1000 2015-2020 Development prices and STAR50 short 2020 context. It checks original source and code identities, applies the inherited signal/matching engine inside those limits, and retains a distinct DEV cohort. No old Validation pair is rematched or overwritten. The same pairs are used for all seven horizons.

```bash
PYTHONPATH=src:. python -m pytest -q tests/test_r1a_development_noise.py tests/test_development_noise_retained.py
PYTHONPATH=src:. python research/r1a_development_noise/study.py --output /tmp/r1a-dev-noise-new
PYTHONPATH=src:. python research/r1a_development_noise/verify_replay.py \
  --reference docs/ops/evidence/r1a_development_noise_20260912 \
  --replay /tmp/r1a-dev-noise-new --output /tmp/r1a-dev-noise-audit.json
```

Fresh output directory required. The dedicated readonly CI performs the same computation with only seven permitted pre2021 price partitions accessible, then verifies all eight tables against sealed references. The older broader regression workflow is preserved. No one-off data-acquisition or result-push workflow remains needed.

Outputs distinguish empirical individual-pair covariance, within/between-stratum covariance, exact simple-return minute/calendar contributions, primitive independent-shock exposure-energy assumptions, fixed daily lag products and hypothetical extra-control marginal-scale scenarios. No mean standard error, confidence interval or new p-value is computed. The Development leg ledger is reproducibility evidence, not fresh confirmation.

Daily contributions include zero-exposure trading dates and are normalized by the fixed full-cohort pair-per-day rate. Their mean equals the corresponding pair mean, but they do not represent a feasible trading portfolio: control selection uses a retrospective same-year pool. Stratum means are ex-post; primitive energy ratios assume independent equal-variance elementary shocks; scenario tables impose event-control covariance zero. None establishes causal noise removal.

Reference bytes and identities stay pinned; replay floats are reconciled at atol=1e-8 and rtol=1e-10, separately from exact discrete identifiers and counts. The original CSVs use 12 significant digits. The categorical K='infinity' label is not an invalid numeric observation.

`BLACKBOX_query_count=3`; `production_authority=false`; `fresh_oos=false`; no 2026 read or confirmation clock.
