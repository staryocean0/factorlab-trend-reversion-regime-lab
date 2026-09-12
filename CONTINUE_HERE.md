# Continue here — reversal / mean-reversion research

## Latest completed experiment

**WALKFORWARD_PREDICTION_DIAGNOSTIC_COMPLETED_NO_CONFIRMATION_AUTHORITY**.

The user-authorized R1_A relative-to-parent walk-forward prediction diagnostic is frozen, implemented, executed and audited. It does NOT merely propose the next experiment. The fixed two-model specification is complete; no automatic feature/model/lambda/horizon search follows.

Read first:
1. `docs/research/R1A_WALKFORWARD_PREDICTION_REVIEW_20260912.md`
2. `docs/ops/evidence/r1a_walkforward_prediction_20260912/REPORT.md`
3. `docs/ops/evidence/r1a_walkforward_prediction_20260912/receipt.json`
4. `docs/governance/R1A_WALKFORWARD_PREDICTION_FREEZE@1.0.json`
5. `research/r1a_walkforward_prediction/README.md`

Freeze `606d25933debcdb986fb19b4489e5c61407b52b3`; decisive code `be103560415ccb4426a6c4ec79bd0df2af85d252`; Actions `34668445944`, job `103485041666`: SUCCESS. Engineering success is not predictive/strategy certification.

## What actually ran

CSI1000 original Development 2015-2020 only, six source partitions. Original 1,752 events preserved: 645 warm-up events in 2015 remain unscored and visible; ALL 1,107 events in information years 2016-2020 are scored at all seven horizons (7,749 rows). Five actual price-prefix checks reproduced known event identities/features exactly. No post2020, ETF, MO or 2026 prices were read.

Training uses original eligible event and non-event parent-state rows once each, not selected matched controls. Parent-only and parent+one-R1_A-indicator linear ridge models use identical rows and weights. Lambda=0.001 fixed. Five annual expanding folds x seven horizons x two models =70 successful fits. Per-horizon labels must finish before the fold cutoff; all normalization is past-only. No failed-fit fallback or difficult-event deletion occurred.

The new object is same-outcome prediction-error improvement, NOT event-minus-control return, matched treatment effect, or PnL. The indicator adds a representation relative to the finite feature set; it is not information beyond the entire price history. Original terminal 240-bar cohort limitations and restricted non-event pool remain disclosed.

## Results — do not promote the strongest cell

| h | Relative event MSE reduction | Positive years | Both directions improve |
|---:|---:|---:|---|
| 1 | +0.3333% | 3/5 | yes |
| 5 | -1.2549% | 1/5 | no |
| 15 | +0.2837% | 3/5 | yes |
| 30 | +0.2872% | 2/5 | no |
| 60 | +0.5953% | 5/5 | yes |
| 120 | +0.5524% | 4/5 | no |
| 240 | -0.2623% | 4/5 | no |

h60 is only a DESCRIPTIVE consistency flag. Enhanced event MSE=9931.1136bp^2 is still above zero forecast MSE=9915.8333bp^2. Do not choose a 60-bar holding period or declare a pass. h15/h30 beat simple pooled references slightly but lack year/side consistency. The baseline is weak: its non-event pooled MSE exceeds zero at every horizon. No universal failure of R1_A or nonlinear prediction is inferred.

Per horizon, 2/1107 events are outside prior mixed-training coordinate ranges and 11/1107 outside prior background ranges; all remain scored. No prior clock/direction background stratum is missing. These are limited support diagnostics, not identification proof. Daily loss sums preserve all 1218 dates, overlap and tails; no new SE/p-value or fresh-OOS claim exists.

## Decision and next boundary

Do not launch confirmation or execution on this result. Preserve R1_A as an unconfirmed historical lead, not a certified strategy and not disproved in all possible formulations. This fixed walk-forward diagnostic is closed as a completed comparison; no automatic replacement empirical candidate is authorized.

Any further scientific proposal must independently justify its question and acknowledge weak benchmark quality, representation limits, historical reuse and remaining dependence. Do not continue this run by changing lambda, feature interactions, class weights, warm-up, years, side or horizon until the old history improves. Do not relabel consumed Development as fresh OOS or use the 2026 candidate automatically.

## Preserved work and data

Old strict past/caliper/exclusive-control design remains closed at design stage; its selected 241/17 paired-return table stays unopened. The new all-event prediction experiment does not revive that contrast. Real-noise decomposition, bounded method/feasibility studies, old Validation/ETF outcomes, all source bytes and freezes remain intact.

Both ETF endpoint diagnostics remain completed. Original full-path v1 retains PARTIAL_CARRIER_TRANSPORT under its separate definition; that old label is not the global latest research status. The failed primary all-seven-endpoint common cohort remains unopened.

Historical ETF CSVs are already public; no routine local transfer is needed. The known 2026 CSI1000 candidate remains metadata-only with unresolved R1_A-specific exposure. R1/R2 certification and closed R1_B/R2-directional/MO identities remain.

`BLACKBOX_query_count=3`; no #4; `production_authority=false`; `fresh_oos=false`; `confirmation_protocol_frozen=false`; `confirmation_clock_started=false`; `horizon_selected=false`.

Use the fresh-directory commands in `research/r1a_walkforward_prediction/README.md`. Read-only regression verifies original identities/counts/flags and audits tightly bounded continuous floating differences without overwriting reference evidence. Reproduction is not a second market experiment.
