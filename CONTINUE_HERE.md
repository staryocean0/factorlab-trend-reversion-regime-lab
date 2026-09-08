# Continue here — State-conditioned frequency adaptation v1

Date: 2026-09-08

This entry is the active handoff for the cross-thread task on **CSI1000 (000852.SH) / STAR50 (000688.SH) strategy-frequency adaptation under `Unsafe` / `Recovering` states**. It is intentionally separate from the frozen reversal execution line (`v0.15` IM hedge-release replay), which remains unchanged.

## Recovered cross-thread state

The previous conversation had already moved past the initial question "does volatility rise?" and into the narrower hypothesis:

> higher-volatility / `Unsafe` conditions may enlarge the fee/friction budget enough for shorter physical horizons to become economically viable, even though shorter horizons are normally more vulnerable to costs.

The following are **consumed exploratory handoff facts from the prior conversation, not independently reproduced by this branch yet**:

- 1-minute theoretical one-sided friction capacity increased from `Recovering` to `Unsafe`:
  - STAR50: approximately `3.10 -> 5.50 bp`;
  - CSI1000: approximately `2.71 -> 4.77 bp`;
  - uplift ratio approximately `1.76–1.78x`.
- A simple fixed frequency grid `1/2/3/5/10/15/30 min` with transparent trend/reversal controls did **not** establish that higher frequency is stably more profitable.

Therefore v1 does not repeat the false implication "higher volatility => shortest horizon wins". The next question is whether the **state-conditioned economic viability curve** shifts toward shorter horizons after fixed costs, without selecting a winning strategy from the same outcomes.

The old conversational labels `RD1 / SA1 / SA2` are not present in repository evidence and are not treated as authoritative stage IDs here. Repository commits, frozen protocol, hashes and result cards are the source of truth.

## Active branch and parent

```text
branch = research/state-frequency-adaptation-v1
parent = 5477340e66c124df7a4691328f796e83f1802255
```

The parent contains the complete prior trend/reversion research tree through the v0.14.2 3-second execution-clock bridge plus already-preregistered v0.15 IM documents. This branch must not modify the v0.15 protocol/data contract/quote manifest.

## Current frozen action

Read and execute:

`docs/research/STATE_FREQUENCY_ADAPTATION_V1_PROTOCOL.md`

The protocol is results-blind with respect to any new state-by-frequency replay. UK/英国预警验证 is explicitly out of scope for this stage.

## Hard input gate

The state pool used by the other conversation is not currently identifiable from the accessible GitHub default-branch artifacts. Before empirical replay, require an immutable state-pool identity with at least:

```text
symbol
market_time_shanghai
state                 # Unsafe or Recovering
state_available_at
source_revision / artifact hash
```

`state_available_at` must be no later than the decision timestamp. No state may be reconstructed from future returns or from the frequency-test outcomes.

If the state-pool artifact is unavailable, stop at the frozen protocol + executable harness gate and record the minimal missing input; do not manufacture replacement labels.

## Scope constraints

- supplied history is consumed development material, not fresh OOS;
- 2026 remains excluded;
- no UK validation in this stage;
- no production registration or live orders;
- no new winner selected by maximizing total P&L;
- no mutation of other FactorLab repositories;
- do not use GitHub Actions as default research compute.

## Intended next evidence

1. validate the state-pool identity and point-in-time availability;
2. run the fixed `1/2/3/5/10/15/30m` frequency grid for the two fixed sign-based control families;
3. persist gross edge, turnover, break-even one-way friction budget and fixed-cost survival by state;
4. test whether `Unsafe` expands the viable short-horizon set relative to `Recovering`;
5. preserve the null result if shorter horizons do not become robustly viable.
