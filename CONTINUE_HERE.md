# Continue here — reversal / mean-reversion research

## Latest completed task

**CONTROL_ALLOCATION_DESIGN_SCREEN_COMPLETED_NO_OUTCOMES**.

The user-authorized next gate has executed. The fixed `rmr_R1A_past_mature_caliper_interval_exclusive_design_v1` is closed at the design stage: coverage and retention of the original event population fail. Do not open its selected-pair returns or reinterpret this as R1_A alpha failure.

Read first:

1. `docs/research/R1A_CAUSAL_CONTROL_DESIGN_REVIEW_20260912.md`
2. `docs/ops/evidence/r1a_control_design_20260912/REPORT.md`
3. `docs/ops/evidence/r1a_control_design_20260912/design_receipt.json`
4. `docs/governance/R1A_CAUSAL_CONTROL_DESIGN_FREEZE@1.0.json`
5. `research/r1a_control_design/README.md`

Freeze `6ebbb80e93cd0e5d783438c41f6fe310381a3e68`; decisive code `6b453cef4546890a4576c79ef77f51b40a5cb905`; Actions `34666939631`, job `103480639603`: SUCCESS. A read-only replay at `ab03c3a415088116147d50c40ad3ad409127c08b`, Actions `34667157622`, also succeeded. Engineering SUCCESS is not a scientific PASS.

## Actual result

Original Development event populations and features were verified unchanged: CSI1000 2015-2020 has 1,752 events and 144,733 candidate controls; STAR50 short 2020 context has 156 events and 7,673 candidates. The latter is not an independent full-period confirmation.

| Scope | Past nearest shadow | Add fixed quality shadow | Primary: add exclusive 240-bar intervals |
|---|---:|---:|---:|
| CSI1000 | 1,645 / 1,752 = 93.89% | 414 / 1,752 = 23.63% | 241 / 1,752 = 13.76% |
| STAR50 context | 122 / 156 = 78.21% | 27 / 156 = 17.31% | 17 / 156 = 10.90% |

Only the last column is the proposed design. Shadows diagnose availability loss, not alternatives eligible for automatic promotion. CSI1000 no-match reasons are exactly 107 with no mature same-year/direction/clock candidate, 1,231 with no candidate inside the four-component 0.5 prefix-scale caliper, and 173 blocked by already allocated intervals. All original events remain in the denominator and ledger.

Every primary match respects maturity, caliper and zero control-control interval overlap. But selected-event composition is strongly shifted: pooled CSI1000 original-event-SD shifts are -0.532 (parent drift), -0.657 (parent efficiency), +0.681 (log parent age), and -0.321 (local volatility ratio). Paired event-control SMDs below 0.02 do not make those 241 events representative of all 1,752.

A further analytical implication, reproduced by the replay auditor, is that the same-year inclusive [c,c+240] disjoint rule can cover at most sum_year min(events_year,floor(price_rows_year/241)) events: 1,230/1,752 = 70.21% for CSI1000, even before matching quality. Thus its 80% overall coverage requirement is incompatible with this constraint conjunction. This is not a universal limit for other designs, and the actual greedy allocation is not claimed globally optimal.

## Source and outcome boundary

Only seven pre2021 index price partitions were read to reconstruct the original causal feature stream. The old structural event compiler accesses historical close/first-passage logic; do not falsely claim it never accesses rows after earlier events. The new allocator receives identity/time/covariates only, and no newly assigned paired returns, p-values or realized noise estimates are evaluated.

No 2021-2025, ETF, MO or 2026 prices/return ledgers were present in the decisive checkout. The separately named Development allocations do not replace Validation pairs, original signals or historical results. Unit-incidence overlap/energy is geometry, not measured variance reduction or independence.

## Current boundary

Stop the fixed hard-pruning design; do not widen 0.5, lower 80%, remove 2015, select a shorter horizon, switch to a shadow or compute returns for only the 241/17 selected pairs to manufacture success. The previous generic statistical-method sweep remains closed. No formal confirmation protocol or clock has started.

Before proposing any other baseline, explicitly distinguish (a) retrospective, outcome-blind attribution and (b) an event-time forecasting benchmark, while preserving the original all-event target or admitting it is not identified. An offline attribution control need not be a live-trade input. The strict maturity/exclusivity requirements here were new design choices, not universal laws of price validity. Do not create another estimator sweep or pretend that lower overlap alone solves noisy event outcomes.

The next task is an estimand/identification decision under explicit assumptions, not an authorized empirical candidate. This review does not freeze or execute a replacement. R1_A remains an unconfirmed historical lead, not a closed price mechanism.

## Preserved lineage and data

The real Development noise decomposition is retained under `docs/research/R1A_DEVELOPMENT_NOISE_REVIEW_20260912.md` and `docs/ops/evidence/r1a_development_noise_20260912/`. Individual event dispersion, concentrated calendar control exposure and uncertainty of the mean remain separate quantities.

Both ETF endpoint diagnostics remain complete. Original full-path v1 retains its separate PARTIAL_CARRIER_TRANSPORT status. The failed primary all-seven-endpoint common cohort stays unopened. All data, original pair/outcome ledgers, freezes and previous statistical/feasibility findings remain intact.

No routine local data transfer is required: actual historical ETF CSVs are in `data/r1a_carrier_prices/cloud_pack_v1/`. The known 2026 CSI1000 candidate in the overnight repository remains metadata-only, with unresolved R1_A-specific exposure; do not call it automatically fresh holdout.

R1/R2 mechanism certifications and closed R1_B/R2-directional/MO identities are unchanged. `BLACKBOX_query_count=3`; no #4; `production_authority=false`; `fresh_oos=false`; `confirmation_protocol_frozen=false`; `confirmation_clock_started=false`; `horizon_selected=false`.

## Reproduce without reopening the design

Use the fresh-directory commands in `research/r1a_control_design/README.md`. The read-only `control-design-regression` workflow preserves seven-file Development source isolation and verifies exact allocation IDs/counts/flags and tightly bounded continuous differences. Reproduction is not new research evidence.
