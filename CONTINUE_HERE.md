# Continue here — reversal / mean-reversion research

## Latest completed stage

**`CONFIRMATION_FEASIBILITY_COMPLETED_NOT_READY_TO_START`**

The user-authorized sample-size/power, null-calibration and new-data-role checks have executed. This is not a plan awaiting execution. R1_A remains a historical short-horizon lead, not a confirmed trading edge and not a disproved mechanism.

Decisive run `34661221824`, job `103463958578`: SUCCESS. Freeze commit `4c1b30995e02e00d335b83a050a45e9cb309d502`; computation commit `25cf8ffa9d45995b8d24c63184d3dd8b73af1c00`.

Read first:

1. `docs/research/R1A_CONFIRMATION_FEASIBILITY_REVIEW_20260912.md`
2. `docs/ops/evidence/r1a_confirmation_feasibility_20260912/planning/REPORT.md`
3. `docs/ops/evidence/r1a_confirmation_feasibility_20260912/planning/feasibility_receipt.json`
4. `docs/ops/evidence/r1a_confirmation_feasibility_20260912/data_role/REPORT.md`
5. `docs/ops/evidence/r1a_confirmation_feasibility_20260912/data_role/csi1000_2026_candidate_review.json`
6. `docs/governance/R1A_CONFIRMATION_FEASIBILITY_FREEZE@1.0.json`

## What was measured

All 28 layer/index/horizon designs were evaluated: INDEX uses every frozen original pair regardless of ETF availability; ETF uses its already measured horizon-specific observed-endpoint pairs. Old means were not plugged in as true effects. Fixed true-effect assumptions are 2/4/6bp; targets 80%/90%; comparison families 1/7/14/28; four inherited variance specifications.

Retained tables include 112 noise specifications, 2,688 sample-size scenarios, 6,720 fixed-budget scenarios, 140 annual pair rates and 112 calibration rows. The calibration represents 224,000 synthetic datasets, not new market observations.

At primary 20-day/origin-0 variance and family 14, for 80% positive detection of a true 4bp index increment:

| CSI1000 location | Expected paired observations | Required trading days | Historical-information-equivalent years |
|---|---:|---:|---:|
| 15 bars | 4,858 | 4,543 | 18.74 |
| 30 bars | 13,062 | 12,215 | 50.39 |

These are conditional noise/rate extrapolations, NOT forecasts, final sample-size commitments, instructions to wait decades, or claims of market stationarity over that span. ETF quantities are larger (5,260/14,996 pairs). A 243-day index budget has 80%-power detectable effects about 17.29/28.36bp, not 2-6bp. The model's assumptions and subsequent calibration limits make an immediate confirmatory launch unjustified.

## Calibration finding

Nominal-5% null rejection across the 28 fixed geometries:

- IID Gaussian: 2.95%-4.85%.
- Shared independent block Gaussian: 4.60%-7.45%.
- Shared independent block t5: 3.20%-7.25%.
- Off-graph AR(1)=0.6 block dependence: 6.80%-22.20%; 26/28 severe warnings under the frozen Monte Carlo criterion.

The AR model is imposed, not estimated market truth. This shows sensitivity to an explicit dependence violation, not that the real false-positive rate equals 22.20%. Easier-case performance is not certification either. The prior graph/t estimator is not validated for prospective use by a green CI. No historic p-value was retuned, no means changed, no new alpha PASS issued.

## Data-role audit — 2026 candidate exists but is not admitted as fresh

Five public default-branch trees and 37 bounded metadata files were inspected, plus branch names. No candidate new price or strategy-outcome file was read. The overnight repository hit the predeclared 12-of-34 metadata limit; the audit does not claim exhaustive local/private/branch/artifact exposure coverage.

Relevant existing candidate:

`staryocean0/factorlab-overnight-open-lab/data/gap_fill_repeat_2026/csi1000_1m_20260105_to_20260821.parquet`

Its manifest declares `000852.SH`, 2026-01-05..2026-08-21, 154 trading days, 36,960 rows; `fresh_oos=false` and use in a gap-fill repeat-validation evaluator. A source metadata-only review is retained. It was NOT copied or opened as prices here.

Decision: `KNOWN_REPEAT_USE_NOT_CERTIFIED_R1A_HOLDOUT`; R1_A-specific exposure is UNKNOWN. Another study's use does not automatically contaminate R1_A, but absence of an R1_A usage log does not establish non-exposure. No paired admitted 2026 ETF package or qualified confirmation set was established. Do not say no 2026 data exist; do not call this file independent validation.

## Current next boundary

**Do not launch a formal small-effect confirmation campaign yet.** No final confirmation protocol or observation clock has started. The feasibility freeze is not a prospective study start.

The next bounded task is method-only calibration/measurement feasibility, on synthetic data and already disclosed historical nuisance geometry. Address serial/calendar dependence and information efficiency before spending scarce potentially confirmatory data. Require an explicit resource budget and disclosed estimand. Do not search real-history p-values across estimators, matching rules, horizons or filters. Any substantive matching/estimand change is a new design, never a retroactive edit of the old outcomes.

Keep 2026 at metadata-only status until that design and source/exposure role are justified. No automatic purchase, local data-transfer request, live-account action, options or futures study is triggered.

## Preserved evidence and authority

Retrospective endpoint robustness remains completed and non-promoting; 0/14 primary adjusted lower bounds were positive. That is inconclusive evidence, not a zero-effect finding. Both ETF endpoint diagnostics remain completed; the original full-path v1 remains PARTIAL_CARRIER_TRANSPORT under its original definition. CSI1000's failed all-seven-endpoint common-cohort ETF table remains unopened.

All original R1_A signals, pairs, directions, carriers, seven horizons and historical CSVs remain unchanged. Source-observation and missing-outcome assumptions are not resolved by sample-size calculations. R1/R2 certifications and closed R1_B/R2-directional/MO identities are preserved.

Actual historical ETF data remain public in `data/r1a_carrier_prices/cloud_pack_v1/`. Do not ask for another routine transfer of those files.

## Reproduction

```bash
PYTHONPATH=src:. python research/r1a_confirmation_feasibility/study.py --output /tmp/r1a-feasibility-new
PYTHONPATH=src:. python -m pytest -q tests/test_r1a_*.py
```

Use a fresh output directory. The live metadata audit is deliberately not rerun by ordinary regression CI; its original tree/blob hashes are retained. Repeating it is a new timestamped inventory, not confirmation.

`BLACKBOX_query_count=3`; no query #4; `production_authority=false`; `fresh_oos=false`; `confirmation_protocol_frozen=false`; `confirmation_clock_started=false`; `horizon_selected=false`.
