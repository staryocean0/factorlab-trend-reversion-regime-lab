# Continue here — reversal / mean-reversion bucket

## Current authority

This repository's current job is **real reversal / mean-reversion strategy research**.

Canonical migrated strategy identities:

- **R1**: intact parent trend + lower-scale counter-move recovery;
- **R2**: intact parent range + boundary overshoot / re-entry.

Read first:

1. `docs/research/R1_R2_MIGRATION_NOTE_20260909.md`
2. `docs/archive/rmr_migrated_from_star50_20260909/`
3. `scripts/rmr_parent_state_legacy/`

The older reversal research branches (`research/reversal-*`) remain historical strategy evidence and may be mined for mechanisms, failures and execution constraints.

## Bucket boundary

Do not restart a generic K-line state recognizer here. Range/up/down causal state recognition belongs to `factorlab-two-wave-strategy-lab`.

Do not restart bottom-layer volatility/risk-state switching here. Unsafe/Recovering/HighVol risk research belongs to `factorlab-star50-filter-lab`.

The `kline-recognizer` v1-v13 research branches in this repository are mis-scoped historical evidence. They remain in Git history but no longer define current authority; their key result/authority package is migrated to the Two-Wave bucket for possible reuse.

`production_authority=false`.
