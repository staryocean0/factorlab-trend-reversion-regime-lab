# Continue here — reversal / mean-reversion bucket

## Current authority

This repository owns reversal / mean-reversion strategy research.

Certified mechanism identities remain:

- **R1** — `rmr_cross_scale_pullback_parent_integrity_v2`;
- **R2** — `rmr_range_boundary_parent_integrity_v2`.

Reusable BLACKBOX query count remains exactly **3**: R1 PASS, R5-C FAIL, R2 PASS. No query #4 is authorized.

`production_authority=false`.

## Price-layer validation is now complete

The missing layer between mechanism certification and instrument implementation has been filled by the frozen study:

`INDEX_PRICE_VALIDITY_FREEZE@1.0`

Decision:

`PRICE_LAYER_VALIDITY_COMPLETED_NO_HORIZON_SELECTED`

The study uses only cash-index 1-minute close prices, next-observed-1m-close entry after causal confirmation, synthetic LONG/SHORT signed gross returns, zero primary transaction cost, and the predeclared horizons `1/5/15/30/60/120/240` observed bars. Every horizon is reported; no best horizon was selected.

Read:

- `docs/governance/INDEX_PRICE_VALIDITY_FREEZE@1.0.json`
- `docs/research/INDEX_PRICE_VALIDITY_STUDY_20260911.md`
- `docs/ops/evidence/index_price_validity_20260911/price_validity_receipt.json`
- `docs/ops/evidence/index_price_validity_20260911/price_response_ledger.csv`

### R1 — price-direction information supported

On CSI1000 `000852.SH` reusable VALIDATION 2021–2025:

- **R1_A** has robust positive signed price response from 1 through 120 bars under the frozen horizon-local consistency flags; 240 bars is not robust.
- **R1_B** has a delayed positive response. The strongest descriptive points in the predeclared term structure are:
  - 120 bars: mean `+11.03bp`, median `+4.49bp`, positive annual mean in `4/5` years, LONG `+11.55bp`, SHORT `+10.53bp`;
  - 240 bars: mean `+23.43bp`, median `+9.97bp`, positive annual mean in `4/5` years, LONG `+33.27bp`, SHORT `+13.77bp`.

On STAR50 `000688.SH` 2021–2025 cross-index transport using the same frozen thresholds:

- **R1_A** transports most clearly at 1, 5 and 30 bars;
- **R1_B** transports at the delayed 120/240-bar part of the term structure:
  - 120 bars: mean `+5.60bp`, median `+1.38bp`, positive annual mean in `4/5` years, LONG `+11.50bp`, SHORT `+0.70bp`;
  - 240 bars: mean `+18.19bp`, median `+1.69bp`, positive annual mean in `4/5` years, LONG `+25.55bp`, SHORT `+12.10bp`.

This establishes a **price-layer directional edge** for R1. It does not establish an executable ETF/futures/options strategy and does not authorize selecting 120 or 240 bars as a trading horizon after seeing this table.

### R2 — direct directional price translation not supported

For CSI1000, R2_A and R2_B pooled signed means are negative across all seven frozen horizons and become more adverse at longer horizons.

STAR50 transport does not repair the result: R2_A remains negative across all horizons; R2_B has a few isolated positive pooled means but fails the frozen consistency conditions and is not robust.

Therefore the current evidence supports:

`R1_PRICE_EDGE_SUPPORTED_R2_DIRECT_DIRECTIONAL_PRICE_EDGE_NOT_SUPPORTED`

Do not route R2 into ETF/options merely because its restoration-probability mechanism is certified. The probability mechanism and direct directional-price payoff are different objects.

## What the earlier option results mean now

The following option identities remain closed and their failures remain valid **instrument/payoff-mapping failures**:

- `rmr_R1B_MO_convex_impulse_mapping_v1` / single long ATM MO;
- `rmr_R1B_MO_ratio_backspread_v1` / 1x2 adjacent-OTM ratio backspread.

They must not be interpreted as evidence that R1 lacks cash-index directional information. The price-layer study now shows the opposite for R1, especially delayed R1_B.

Do not rescue the closed option identities by changing strike, DTE, ratio, width, exit, horizon, fee, year, side or filters.

## Closed — do not restart or retune

Still closed under their own definitions:

- R1 immediate structural economic-translation v1/v2/v3 family;
- R2 `rmr_R2_range_reentry_economic_translation_v1`;
- unified parent-normal-state router;
- R1_B `rmr_R1B_temporal_impulse_completion_v1`;
- both R1_B MO option payoff identities above;
- probability-threshold / probability-sizing rescue;
- broad automatic R8/R9 generation;
- R3/R4 and other closed Stage-1 lanes;
- R5-B1 and R5-C closed identities.

The new price-layer result does not reopen those definitions. It answers a different, more basic question.

## Current frontier

The current research frontier is **R1 instrument transport after price-edge validation**, not another option structure.

The correct hierarchy is now:

`certified R1 mechanism -> supported cash-index directional edge -> ETF/index-carrier transport -> executable implementation`

The repository currently contains verified 1m cash-index data for:

- `000852.SH`: 2015-01-05 .. 2025-12-31;
- `000688.SH`: 2020-07-23 .. 2025-12-31.

No ETF minute-price package is currently admitted in this repository. Therefore **ETF price transport has not yet been tested**.

A later ETF study should first admit a clearly identified CSI1000 ETF and STAR50 ETF price series, then replay the same causal event timestamps / directions and the same full predeclared horizon table without selecting a winner from the index results. ETF short returns may be synthetic for signal-transport research and must be labeled non-executable where shorting/borrow is unavailable.

Until such ETF data are admitted, the index-level conclusion above is the active empirical result.

## Data state

Verified cash-index market data are under `data/market/` and loaded through `src/regime_lab/market_data.py`, with manifest/hash checks.

The separate `data/r1b_research/` cloud package remains valid for reproducing the already-closed MO studies. The admitted MO quote route and fee contract remain archived research infrastructure, not the current frontier.

## Governance boundary

Not authorized:

- selecting a preferred 1/5/15/30/60/120/240 horizon from the price-validity table and declaring it a strategy;
- post-result stop/target/time-of-day/regime/probability tuning;
- reopening R2 directional execution against the adverse term structure;
- opening another R1_B option v3/v4 from the observed option surface;
- BLACKBOX query #4;
- production promotion.

Authorized next work:

- preserve/reproduce the frozen index price-validity result;
- obtain and admit ETF minute-price data for an R1 transport study;
- freeze any ETF transport/execution contract before reading its corresponding outcomes.

## Bucket boundary

Generic Range / UpTrend / DownTrend state recognition belongs to `factorlab-two-wave-strategy-lab`.
Unsafe / Recovering / HighVol risk-state switching belongs to `factorlab-star50-filter-lab`.

Legacy, mis-scoped and closed evidence remains under `docs/archive/` and Git history.

## Read first

1. `CONTINUE_HERE.md`
2. `docs/research/INDEX_PRICE_VALIDITY_STUDY_20260911.md`
3. `docs/governance/INDEX_PRICE_VALIDITY_FREEZE@1.0.json`
4. `docs/ops/evidence/index_price_validity_20260911/price_validity_receipt.json`
5. `docs/research/R1B_POST_BACKSPREAD_PAYOFF_THEORY_REVIEW_20260911.md`
6. `docs/research/R1B_MO_RATIO_BACKSPREAD_OUTCOME_STUDY_20260911.md`
7. `docs/RESEARCH_GOVERNANCE.md`
8. `docs/DATA.md`

`BLACKBOX_query_count=3`.
`production_authority=false`.
