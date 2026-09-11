# Reversal / Mean-Reversion Strategy Bucket

Read `CONTINUE_HERE.md` and `PROMPT.md` before making changes.

## Authority

- R1 and R2 remain certified mechanism identities.
- `BLACKBOX_query_count=3`; no query #4.
- `production_authority=false`.
- The frozen pure cash-index price-validity study is complete.
- Current empirical state: `R1_PRICE_EDGE_SUPPORTED_R2_DIRECT_DIRECTIONAL_PRICE_EDGE_NOT_SUPPORTED`.

## Price-layer result

The current authoritative price study is:

- freeze: `docs/governance/INDEX_PRICE_VALIDITY_FREEZE@1.0.json`;
- report: `docs/research/INDEX_PRICE_VALIDITY_STUDY_20260911.md`;
- receipt: `docs/ops/evidence/index_price_validity_20260911/price_validity_receipt.json`.

It uses synthetic cash-index LONG/SHORT signed gross returns, next-observed-1m-close entry and all frozen horizons `1/5/15/30/60/120/240`. No best horizon was selected.

Key interpretation:

- R1_A has a reproducible short/medium-horizon positive cash-index response.
- R1_B has a delayed response; 120/240-bar positive price response transports from CSI1000 to STAR50, with both LONG and SHORT mean returns positive in both indices.
- R2_A/R2_B do not show a robust direct directional cash-index price edge.

This is signal/price validity only. It is not an executable instrument or production result.

## Closed identities remain closed

Do not use the new index result to reopen old definitions:

- R1 structural economic translations v1/v2/v3;
- R2 `rmr_R2_range_reentry_economic_translation_v1`;
- R1_B temporal impulse completion;
- R1_B single-long ATM MO;
- R1_B 1x2 adjacent-OTM MO ratio backspread;
- other archived closed lanes.

The two option failures remain specific payoff-mapping failures. Do not search strike, DTE, ratio, width, exit, horizon, year, side or filters to rescue them.

## Current frontier

The correct research hierarchy is now:

`R1 certified mechanism -> cash-index price edge supported -> ETF/index-carrier transport -> executable implementation`

The repository has verified 1m data for `000852.SH` and `000688.SH`, but no admitted ETF minute-price package. ETF price transport is therefore not yet tested.

If ETF data are added, freeze the ETF identity/data mapping before reading the corresponding results and replay the causal event directions across the full predeclared horizon set. Do not choose a horizon from the completed index table first.

Do not route R2 into ETF/options as a direct directional strategy under current evidence.

## Bucket boundary

Generic range/up/down state recognition belongs to `factorlab-two-wave-strategy-lab`.
Unsafe/Recovering/HighVol risk-state work belongs to `factorlab-star50-filter-lab`.

Preserve closed/mis-scoped evidence under `docs/archive/` or Git history.
