# Reversal / Mean-Reversion Strategy Bucket

Read `CONTINUE_HERE.md` and `PROMPT.md` before making changes.

## Authority

- R1 and R2 are certified mechanism identities. Do not restart broad discovery.
- Their closed economic translations remain closed.
- R1_B temporal impulse completion remains closed.
- R1_B single-long ATM MO remains closed.
- R1_B 1x2 adjacent-OTM MO ratio backspread remains closed.
- Current state: `CERTIFIED_R1_R2_MECHANISMS_NO_AUTHORIZED_EMPIRICAL_PAYOFF_CANDIDATE`.
- Post-backspread decision: `R1B_LISTED_DIRECTIONAL_OPTION_PAYOFF_PROGRAM_CLOSED_NO_NEW_EMPIRICAL_IDENTITY`.
- `BLACKBOX_query_count=3`; no query #4.
- `production_authority=false`.

## Latest closed identity

`rmr_R1B_MO_ratio_backspread_v1`

Frozen candidate:

`R1B_MO_1x2_ADJACENT_OTM_RATIO_BACKSPREAD_SAME_CAUSAL_EXIT`

The study changed the payoff object without changing the certified R1_B event clock: short one deterministic ATM directional MO option and buy two immediately adjacent OTM options, same type/expiry, synchronized executable quotes only.

Result:

- 385 joinable events;
- 360 completed synchronized packages;
- 93.51% coverage;
- pooled mean -376.61 CNY;
- annual mean negative in 2023, 2024 and 2025;
- only 2/12 voting quarters positive;
- decision `FAIL_IDENTITY_CLOSED`.

Do not rescue it by changing ratio, width, strike distance, DTE, exit, horizon, filters or fees.

## Current research frontier

There is no open empirical payoff identity.

Allowed work is results-blind theory work that is genuinely independent of already observed option outcomes. A new empirical lane requires a new economic mechanism/use-case that determines the payoff object before outcome inspection and a new freeze before execution.

Do not turn the failed option surface into a search grid for:

- another strike / delta / DTE;
- another backspread ratio or width;
- debit/credit verticals selected after the fact;
- calendars/diagonals without a separately justified volatility-term-structure mechanism;
- probability filters, year filters, side filters or timing filters.

## Data

Cloud historical research is self-contained under `data/r1b_research/` for the joinable 2022-07-22..2025-12-31 window.

The admitted DataHub MO route and 14 CNY/contract/leg fee contract remain valid research infrastructure. 2026 MO quotes must not be event-joined until a separately admitted 2026 underlying 1m package exists.

## Bucket boundary

Generic range/up/down state recognition belongs to `factorlab-two-wave-strategy-lab`.
Unsafe/Recovering/HighVol risk-state work belongs to `factorlab-star50-filter-lab`.

Closed/mis-scoped evidence belongs under `docs/archive/` or Git history, not as a reason to restart an old lane.
