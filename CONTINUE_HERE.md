# Continue here — R1_A price research in reserve

## Current program disposition

**`R1A_CURRENT_PRICE_FORMULATION_RESERVED_ACTIVE_DEVELOPMENT_PAUSED`**

The user-authorized cross-study reconciliation and existing forecast-error decomposition have executed. The CURRENT R1_A price-strategy formulation is retained as an unconfirmed historical lead, with automatic active development paused. This is a resource judgment, not proof of zero alpha, closure of the original R1/R2 mechanisms, or termination of the whole reversal/mean-reversion project.

Read first:

1. `docs/research/R1A_EVIDENCE_CLOSEOUT_REVIEW_20260912.md`
2. `docs/governance/R1A_PRICE_RESEARCH_DISPOSITION_20260912.json`
3. `docs/ops/evidence/r1a_evidence_closeout_20260912/receipt.json`
4. `docs/governance/R1A_EVIDENCE_CLOSEOUT_FREEZE@1.0.json`
5. `research/r1a_evidence_closeout/README.md`

Audit decision: `EVIDENCE_RECONCILIATION_COMPLETED_NO_NEW_ALPHA_TEST`.
Freeze: `29bd543948f6de0f0860ecede71a10e78b9f31c8`.
Decisive code: `d6109a11ec93efa26bbd2eca5ad1f15c1009c9e9`.
Decisive Actions: `34669948608`, job `103489303243`.

## What has been verified

Nineteen pinned existing sources were read: nine historical reports, the original forecast receipt and its eight CSVs, and the original Development event identity file. Raw market data were excluded from this audit checkout. No model fits, new signal generation, new strategy returns or new inference were performed.

All 1,752 original CSI1000 Development events remain accounted for: 645 warm-up and 1,107 scored at all seven horizons. The 7,749 existing forecasts reconcile 126 event score groups and 2,268 numeric fields; maximum field difference is about 7.3e-11. Existing label-maturity/prefix records and 1,225 stored parameter rows were checked. No material discrepancy was detected WITHIN this evidence/arithmetic scope. This is not independent raw-source verification or a proof that every prior methodological assumption was correct.

## What the decomposition actually shows

Use e=y-parent prediction and g=enhanced-parent prediction. Existing loss gain equals 2eg-g^2. MSE also decomposes exactly into squared mean residual plus centered residual variance, with ddof=0.

At h15/h30, old total MSE gains are +8.2309/+18.6596 bp^2. Event-count-weighted within-year mean-bias-square reductions are +8.3068/+20.9374 bp^2, while within-year centered-error variance changes contribute -0.0758/-2.2778 bp^2. All seven horizons have negative weighted within-year centered-error improvement. Pooled centering includes between-year effects and is a different decomposition of the same total.

The added R1_A flag is constant across event rows inside each annual model. It primarily provides a fold-level offset, with shared coefficients also changed by the OLD joint fit. This is not a test of every possible within-event ranking/nonlinear representation. Do not call ex-post group mean correction an attained future predictor or infer economic causation.

h15/h30 mean prediction adjustments were negative in 2016-2019 and positive in 2020. Some gains corrected parent-model overforecasting, rather than predicting a larger positive return. Small relative MSE gains alone are not evidence of economic insignificance, and bp^2 is not trading bp.

## Evidence precedence and non-comparability

The early 2021-2025 raw index responses and matched/ETF increments remain recorded. Their target, dates and samples differ from 2016-2020 forward forecast scoring. Retrospective uncertainty checks altered confidence, not the old observed means. Early supported/robust headings are historical context, not current confirmatory authority.

The complete ten-stage evidence map is `docs/ops/evidence/r1a_evidence_closeout_20260912/cross_study_evidence.csv`. No unequal estimands, years or repeated replays are pooled into a new alpha test.

## Default next action

There is **no automatic next empirical candidate**. Do not append another model, lambda, feature, interaction, matching, horizon, side/year filter, cost/exit or option experiment to this completed chain. Do not compute the failed strict-control scheme's selected 241/17 returns. No confirmation clock has started.

A later concrete scientific question or reproducible material error can be proposed with explicit user authorization, a clear target, qualified data role, resource budget and stop rule. Preserve all old results and disclose historical reuse. This reserve judgment is not a permanent ban on new authorized research or other project mechanisms.

## Preserved data and authority

All raw data, freezes, original identities/pairs/results and existing regression workflows remain. Historical ETF CSVs are already public; no local transfer is pending. Both ETF endpoint diagnostics remain complete; old full-path v1 keeps PARTIAL_CARRIER_TRANSPORT only under its separate definition. The failed primary all-seven common cohort stays unopened.

The known 2026 CSI1000 candidate remains metadata-only with unresolved R1_A-specific exposure. Do not call it automatically fresh or open it by default. R1/R2 mechanism records and closed R1_B/R2-directional/MO identities are unchanged.

`BLACKBOX_query_count=3`; no #4; `production_authority=false`; `fresh_oos=false`; `confirmation_protocol_frozen=false`; `confirmation_clock_started=false`; `horizon_selected=false`.

## Maintenance only

Use `research/r1a_evidence_closeout/README.md` to reproduce the no-fit accounting into a fresh directory. Replays verify exact identities/counts and tightly bounded numeric differences, never overwrite decisive receipts, and never constitute new research evidence.
