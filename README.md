# FactorLab Trend–Reversion Regime Lab

This repository is the current FactorLab bucket for **reversal / mean-reversion strategy research**.

## Current authority

Certified mechanism identities:

- **R1** — intact parent trend + lower-scale counter-move recovery;
- **R2** — intact parent range + boundary overshoot / failed acceptance / re-entry.

Both mechanism certifications remain valid. Their tested economic translations are separate questions and may fail without invalidating the mechanism evidence.

Current program state:

`CERTIFIED_R1_R2_MECHANISMS_NO_AUTHORIZED_EMPIRICAL_PAYOFF_CANDIDATE`

`BLACKBOX_query_count=3`. No query #4 is authorized.

`production_authority=false`.

## Latest result

Two separately frozen R1_B directional-option payoff objects have now failed:

1. single long deterministic ATM MO option — `FAIL_IDENTITY_CLOSED`;
2. 1x2 adjacent-OTM MO ratio backspread — `FAIL_IDENTITY_CLOSED`.

The second identity was introduced only after the first was closed, frozen before its own outcomes, and executed in GitHub Actions with conservative synchronized bid/ask fills. It achieved 93.51% joint-fill coverage but had pooled mean net **-376.61 CNY**, negative annual means in 2023/2024/2025, and only 2/12 positive voting quarters.

The post-backspread theory review therefore concludes:

`R1B_LISTED_DIRECTIONAL_OPTION_PAYOFF_PROGRAM_CLOSED_NO_NEW_EMPIRICAL_IDENTITY`

This is not a claim that every option strategy is impossible. It is a governance decision that another strike, ratio, width, DTE, vertical, calendar or volatility structure cannot now be chosen from the already observed payoff surface without an independent new mechanism/theory.

## Cloud-ready research data

Historical cloud execution no longer depends on the local DataHub lake.

`data/r1b_research/` contains:

- CSI1000 `000852.SH` 1m underlying through 2025-12-31;
- `contract_master.csv`;
- slim MO L1 bid/ask/status quote CSVs for the joinable 2022-07-22..2025-12-31 window.

The primary DataHub MO quote route is admitted and the active fee contract is frozen at 14 CNY per contract per leg.

2026 MO quotes are not currently event-joinable in cloud research because no separately admitted 2026 underlying 1m package is present.

## Start here

1. [`CONTINUE_HERE.md`](CONTINUE_HERE.md)
2. [`PROMPT.md`](PROMPT.md)
3. [`docs/research/R1B_POST_BACKSPREAD_PAYOFF_THEORY_REVIEW_20260911.md`](docs/research/R1B_POST_BACKSPREAD_PAYOFF_THEORY_REVIEW_20260911.md)
4. [`docs/research/R1B_MO_RATIO_BACKSPREAD_OUTCOME_STUDY_20260911.md`](docs/research/R1B_MO_RATIO_BACKSPREAD_OUTCOME_STUDY_20260911.md)
5. [`docs/research/R1B_MO_OUTCOME_STUDY_20260911.md`](docs/research/R1B_MO_OUTCOME_STUDY_20260911.md)

## Explicit boundary

Do not automatically open an R1_B option v3/v4. A new empirical payoff identity requires a genuinely independent theory or economic use-case and a new pre-outcome freeze.

Generic Range / UpTrend / DownTrend causal classification belongs to `factorlab-two-wave-strategy-lab`.
Unsafe / Recovering / HighVol bottom-layer risk-state research belongs to `factorlab-star50-filter-lab`.

Closed and mis-scoped work is preserved under `docs/archive/` and Git history.
