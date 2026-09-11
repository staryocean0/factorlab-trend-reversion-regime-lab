# Reversal / Mean-Reversion Strategy Bucket

Read `CONTINUE_HERE.md` and `PROMPT.md` before making changes.

## Authority

- R1 and R2 are certified mechanism identities. Do not restart broad discovery.
- Closed linear economic translations, unified router, R1_B temporal impulse completion and R5-B1 stay closed.
- Active identity: `rmr_R1B_MO_convex_impulse_mapping_v1`.
- Status: `R1B_MO_CONVEX_PAYOFF_THEORY_ACCEPTED_DATA_ADMISSION_REQUIRED`.
- `BLACKBOX_query_count=3`; no query #4.
- `production_authority=false`.

## Current execution frontier

Only MO instrument-data acquisition/admission and fee-contract completion are authorized. No event-conditioned MO option outcomes or PnL are authorized.

Primary source target: CFFEX / CIIS historical Level-2 Snapshot for all listed MO contracts.

Frozen physical delivery epochs:

- `LEGACY_CFFEX_SNAPSHOT`: 2022-07-22 .. 2024-07-07
- `POST_TRANSITION_CFFEX_DELIVERY`: 2024-07-08 .. 2026-09-10

Each epoch requires an independent source mapping and schema/provenance check. No canonical concatenation unless both pass.

Use:

- `docs/governance/R1B_MO_DATA_ADMISSION_PROTOCOL_V1.json`
- `docs/governance/R1B_MO_CIIS_DELIVERY_EPOCH_FREEZE_20260910.json`
- `research/r1b_mo_data_admission/adapt_cffex_snapshot.py`
- `research/r1b_mo_data_admission/adapt_cffex_snapshot_epochs.py`
- `research/r1b_mo_data_admission/validate_mo_quote_source.py`

Adapters are fail-closed and never create empirical authority. CI run `34450248565` passed after the multi-epoch adapter/test addition.

## Data discipline

- Preserve raw delivered bytes and checksums before any event join.
- Resolve bid/ask, sizes, status, zero/missing semantics and contract expiry from real documentation; never guess.
- No midpoint/last-price substitution for missing executable quotes.
- Historical through 2026-09-10 is reusable instrument-development evidence; prospective validation begins 2026-09-11 only for genuinely post-freeze observations.
- Complete exchange effective-period fee history and actual broker/customer commission independently. Do not invent broker markup.

## Bucket boundary

Generic range/up/down state recognition belongs to `factorlab-two-wave-strategy-lab`.
Unsafe/Recovering/HighVol risk-state work belongs to `factorlab-star50-filter-lab`.

Closed/mis-scoped evidence belongs under `docs/archive/` or Git history, not active `research/`.
