# Reversal / Mean-Reversion Strategy Bucket

Read `CONTINUE_HERE.md`, `PROMPT.md`, `docs/research/R1_R2_MIGRATION_NOTE_20260909.md`, `docs/DATA.md`, and `docs/RESEARCH_GOVERNANCE.md` before research.

## Current scope

This repository is the current FactorLab bucket for **real reversal / mean-reversion strategy research**, including the migrated R1/R2 lineage and earlier MR/REV mechanism work.

- **R1**: intact parent trend + lower-scale counter-move recovery.
- **R2**: intact parent range + boundary overshoot / failed acceptance / re-entry.
- Historical MR0/MR1/REV0, robust re-entry, first-passage, clock/stability/execution studies may be mined for mechanisms, failures and contributions.

## Cross-bucket boundary

Do not develop a generic `Range / UpTrend / DownTrend` causal state recognizer here; that belongs to `factorlab-two-wave-strategy-lab`.

Do not develop STAR50/CSI1000 Unsafe/Recovering/HighVol bottom-layer risk-state switching here; that belongs to `factorlab-star50-filter-lab`.

The `kline-recognizer` v1-v13 research branches in this repository are mis-scoped historical evidence. They are not current authority and must not be continued here. Their key authority/result package has been migrated to the Two-Wave bucket as supporting evidence.

## Research discipline

- Subjects remain CSI1000 `000852.SH` and STAR50 `000688.SH` where relevant to the preserved strategy research.
- Supplied history is consumed development/validation evidence, not fresh OOS by virtue of repository placement.
- Preregister mechanism, timing, data roles and candidate budget before empirical selection.
- Keep failed experiments and extract reusable contributions; a failed challenger never erases the current best strategy.
- Index diagnostics are not directly executable account returns; tradable carrier and costs require explicit contracts.
- No production registration, live orders or production authority.
- Historical Git evidence is preserved during scope repair; fix current authority rather than rewriting the past.

`production_authority=false`.
