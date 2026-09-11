# R1_B MO 1x2 adjacent-OTM ratio-backspread outcome study — 2026-09-11

Research identity: `rmr_R1B_MO_ratio_backspread_v1`

Candidate: `R1B_MO_1x2_ADJACENT_OTM_RATIO_BACKSPREAD_SAME_CAUSAL_EXIT`

Decision: **FAIL_IDENTITY_CLOSED**

`fresh_oos=false`  
`BLACKBOX_query_count=3`  
`production_authority=false`

Freeze: `docs/governance/R1B_MO_BACKSPREAD_PRE_EXECUTION_FREEZE@1.0.json`  
Recovered decisive receipt: `docs/ops/evidence/r1b_mo_backspread_20260911/outcome_receipt.json`  
Actions run: `34612892387`, job `103307532666`

## Research boundary

This was frozen before any new backspread outcome was opened. It did not change the certified R1_B event engine, S2/S3 thresholds, parent direction, underlying entry clock, causal success/failure exit, 1200-bar safety horizon, expiry rule, historical fee rate, year set, or any probability filter.

The only new payoff object was:

- upward parent: short 1 deterministic ATM call + long 2 immediately adjacent OTM calls;
- downward parent: short 1 deterministic ATM put + long 2 immediately adjacent OTM puts;
- same expiry for both legs;
- no ratio search and no spread-width search;
- entry/exit required both contracts to be executable at the same quote timestamp;
- entry = short bid / long ask; exit = short ask / long bid;
- 14 CNY per contract per leg; six contract executions per completed package = 84 CNY total fee.

The purpose was to test whether financing part of the premium burden while retaining net tail convexity could better represent R1_B's sparse large-restoration component than the already-closed single-long ATM option.

## Execution integrity

Results-blind preflight run `34612801045` passed all 5 synthetic tests before the empirical study.

In the decisive workflow, checkout, package installation, preflight re-run, and the frozen historical outcome step all completed successfully. The workflow was marked failed only afterward because `git add` refused newly generated evidence files outside the sparse-checkout definition. The aggregate adjudication below is recovered exactly from the immutable Actions job log; the empirical runner was not re-run and no gate was changed.

The ephemeral row-level event ledger was not persisted. This does not affect the frozen decision because three economic gates fail by wide margins.

## Inventory

- joinable underlying events: **385**
- completed joint-fill backspreads: **360**
- joint-fill coverage: **93.5065%**
- descriptive pooled mean net: **-376.61 CNY**
- descriptive pooled median net: **-884.00 CNY**
- descriptive win rate: **22.22%**

The coverage gate passed, so this is not a liquidity/missing-quote rejection.

## Sealed gates

| Gate | Frozen requirement | Result |
|---|---|---|
| joint-fill coverage | >= 80% | **PASS** — 93.51% |
| pooled mean net | > 0 CNY | **FAIL** — -376.61 CNY |
| positive annual mean | >= 2 of 2023/2024/2025 | **FAIL** — 0/3 |
| positive quarterly mean | >= 6 of 12 quarters in 2023–2025 | **FAIL** — 2/12 |

All gates were conjunctive. Therefore the identity fails.

## Annual mean net CNY

| Year | Mean |
|---|---:|
| 2023 | -408.57 |
| 2024 | -131.43 |
| 2025 | -484.82 |

There is no positive annual mean in the three voting years.

## Quarterly mean net CNY

| Quarter | Mean |
|---|---:|
| 2023Q1 | -280.00 |
| 2023Q2 | -718.00 |
| 2023Q3 | -474.40 |
| 2023Q4 | -268.00 |
| 2024Q1 | +159.68 |
| 2024Q2 | -720.55 |
| 2024Q3 | +1476.77 |
| 2024Q4 | -782.18 |
| 2025Q1 | -202.12 |
| 2025Q2 | -660.19 |
| 2025Q3 | -758.29 |
| 2025Q4 | -349.88 |

Only 2024Q1 and 2024Q3 are positive. The large 2024Q3 right-tail episode is not enough to create a stable payoff identity.

## Scientific interpretation

The proposed financing transformation does not solve the R1_B monetization problem. It reduces neither the sign instability nor the broad typical-event loss enough to create positive pooled or cross-time expectancy. The sparse favorable tail remains visible, but it is even less defensible as a reusable economic identity because all three voting years are negative and 10 of 12 quarters are negative.

This result strengthens the conclusion that the unresolved R1_B signal is a restoration-probability / path-shape fact rather than a currently certified listed-directional-option payoff.

## Closed — no rescue

Do not continue this identity by changing:

- 1x2 to another ratio;
- adjacent OTM to two or more strikes away;
- call/put delta or strike width;
- expiry or DTE;
- entry delay;
- causal exit, stop, target or horizon;
- fees;
- year, quarter, side, regime or time-of-day filters;
- midpoint/last-price execution;
- probability filtering or sizing.

Such changes would be outcome-conditioned rescue of this failed identity.

## Program consequence

The single-long ATM MO candidate and the simple financed-tail 1x2 adjacent-OTM backspread have now both failed under separately frozen definitions. Further nearby listed-option structures are not automatically authorized. A genuinely new payoff object/mechanism theory must be independently motivated before any additional empirical option outcome is opened.

`BLACKBOX_query_count=3` remains unchanged. No query #4 and no production authority.
