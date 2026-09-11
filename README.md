# FactorLab Trend–Reversion Regime Lab

This repository is the current FactorLab bucket for **reversal / mean-reversion strategy research**.

## Current authority

Certified mechanism identities:

- **R1** — intact parent trend + lower-scale counter-move recovery;
- **R2** — intact parent range + boundary overshoot / failed acceptance / re-entry.

The current active frontier is:

`rmr_R1B_MO_convex_impulse_mapping_v1`

Status:

`R1B_MO_CONVEX_PAYOFF_THEORY_ACCEPTED_DATA_ADMISSION_REQUIRED`

The long-directional CSI1000 option (`MO`) payoff theory is approved **for data admission only**. No event-conditioned MO option PnL or parameter search is authorized yet.

Start here:

1. [`CONTINUE_HERE.md`](CONTINUE_HERE.md)
2. [`PROMPT.md`](PROMPT.md) — local execution-agent handoff
3. [`docs/research/R1B_MO_CFFEX_ACQUISITION_SPEC_20260910.md`](docs/research/R1B_MO_CFFEX_ACQUISITION_SPEC_20260910.md)
4. [`docs/research/R1B_MO_CIIS_CURRENT_ORDER_ROUTE_20260910.md`](docs/research/R1B_MO_CIIS_CURRENT_ORDER_ROUTE_20260910.md)
5. [`docs/governance/R1B_MO_CIIS_DELIVERY_EPOCH_FREEZE_20260910.json`](docs/governance/R1B_MO_CIIS_DELIVERY_EPOCH_FREEZE_20260910.json)
6. GitHub issue **#7**

## Current engineering gate

The public CIIS sample recovery path is exhausted, but the official CIIS/CFFEX Level-2 delivery route remains active. The 2022-07-22..2026-09-10 acquisition window crosses a documented 2024-07-08 delivery-format transition, so legacy and post-transition files are mapped and validated as separate physical epochs before canonical concatenation.

Active code is under:

`research/r1b_mo_data_admission/`

CI run `34450248565` passed the admission/adapter test suite after the multi-epoch adapter was added.

## Explicit bucket boundary

This repository is **not** the current home for:

- generic Range / UpTrend / DownTrend causal classification — see `factorlab-two-wave-strategy-lab`;
- Unsafe / Recovering / HighVol bottom-layer risk-state research — see `factorlab-star50-filter-lab`.

Mis-scoped or closed work is preserved under `docs/archive/` and Git history, not kept on the active research surface.

`BLACKBOX_query_count=3`.

`production_authority=false`.
