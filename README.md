# FactorLab Trend–Reversion Regime Lab

## Current bucket authority: reversal / mean-reversion strategies

This repository is the **real reversal / mean-reversion strategy bucket** for the current FactorLab split.

Current canonical strategy family:

- **R1** — intact parent trend + lower-scale counter-move recovery;
- **R2** — intact parent range + boundary overshoot / failed acceptance / re-entry;
- preserved earlier MR/REV work (`MR0`, `MR1`, `REV0`, robust re-entry, first-passage, clock/stability/execution studies) remains research lineage for these strategy questions.

Start with:

1. [`CONTINUE_HERE.md`](CONTINUE_HERE.md)
2. [`docs/research/R1_R2_MIGRATION_NOTE_20260909.md`](docs/research/R1_R2_MIGRATION_NOTE_20260909.md)
3. preserved package under `docs/archive/rmr_migrated_from_star50_20260909/`
4. runnable legacy entries under `scripts/rmr_parent_state_legacy/`

## Explicit bucket boundary

This repository is **not** the current home for:

- generic causal classification of K-line state into range / uptrend / downtrend — that belongs to `factorlab-two-wave-strategy-lab`;
- STAR50 / CSI1000 bottom-layer volatility, Unsafe/Recovering, HighVol or risk-state switching research — that belongs to `factorlab-star50-filter-lab`;
- the mis-scoped `kline-recognizer` v1-v13 lineage that was developed on research branches here. That lineage is preserved as historical Git evidence and its authority/result package is migrated to the Two-Wave bucket as supporting state-classification research. It does **not** define this repository's current authority.

The original broad trend-vs-reversion seed framework remains in `RESEARCH_FRAMEWORK.md` as historical background; it no longer overrides the bucket split above.

`production_authority=false`. No live trading or production authority is granted by this repository.
