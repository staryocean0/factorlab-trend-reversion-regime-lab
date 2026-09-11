# FactorLab Trend–Reversion Regime Lab

This repository is the current FactorLab bucket for **reversal / mean-reversion strategy research**.

## Current authority

Certified mechanism identities remain:

- **R1** — intact parent trend + lower-scale counter-move recovery;
- **R2** — intact parent range + boundary overshoot / failed acceptance / re-entry.

The previously missing cash-index price layer has now been tested under a pre-result freeze.

Current empirical state:

`R1_PRICE_EDGE_SUPPORTED_R2_DIRECT_DIRECTIONAL_PRICE_EDGE_NOT_SUPPORTED`

`BLACKBOX_query_count=3`; no query #4 is authorized.  
`production_authority=false`.

## Latest result — pure index price validity

The frozen study measures zero-cost synthetic LONG/SHORT cash-index returns from the next observed 1m close after each causal R1/R2 event across all predeclared horizons `1/5/15/30/60/120/240`. No horizon was selected after results.

CSI1000 `000852.SH`, 2021–2025:

- R1_A has a consistent short/medium-horizon positive price response;
- R1_B has a delayed positive response, including `+11.03bp` mean at 120 bars and `+23.43bp` at 240 bars; both LONG and SHORT means are positive at those horizons;
- R2_A/R2_B direct signed returns are negative across the frozen horizon set and deteriorate with horizon.

STAR50 `000688.SH` 2021–2025 transport:

- R1_A transports at several short/medium horizons;
- R1_B transports at 120/240 bars (`+5.60bp` / `+18.19bp` mean);
- R2 does not form a robust directional price edge.

This supports **R1 signal validity at the cash-index price layer**. It does not yet prove ETF/futures/options executability or authorize a preferred holding horizon.

## Instrument-mapping history

The previously tested R1_B MO single-long and 1x2 adjacent-OTM backspread identities remain closed. Their failures are now interpreted correctly as **specific option payoff-mapping failures**, not as evidence that R1 lacks directional price information.

Do not reopen those option identities by searching strike, DTE, ratio, width, horizon or filters.

## Current frontier

The next missing layer is **ETF price transport / executable carrier mapping for R1**.

Verified cash-index data already in the repository:

- `000852.SH` 1m: 2015-01-05 .. 2025-12-31;
- `000688.SH` 1m: 2020-07-23 .. 2025-12-31.

No ETF minute-price package is currently admitted in this repository, so ETF transport has **not** yet been tested.

## Start here

1. [`CONTINUE_HERE.md`](CONTINUE_HERE.md)
2. [`docs/research/INDEX_PRICE_VALIDITY_STUDY_20260911.md`](docs/research/INDEX_PRICE_VALIDITY_STUDY_20260911.md)
3. [`docs/governance/INDEX_PRICE_VALIDITY_FREEZE@1.0.json`](docs/governance/INDEX_PRICE_VALIDITY_FREEZE@1.0.json)
4. [`docs/ops/evidence/index_price_validity_20260911/price_validity_receipt.json`](docs/ops/evidence/index_price_validity_20260911/price_validity_receipt.json)
5. [`PROMPT.md`](PROMPT.md)

## Explicit boundary

Do not choose a best horizon from the completed price-validity table and call it a strategy. Any ETF or executable implementation requires a separate pre-outcome freeze.

Generic Range / UpTrend / DownTrend causal classification belongs to `factorlab-two-wave-strategy-lab`.
Unsafe / Recovering / HighVol bottom-layer risk-state research belongs to `factorlab-star50-filter-lab`.

Closed and mis-scoped work remains preserved under `docs/archive/` and Git history.
