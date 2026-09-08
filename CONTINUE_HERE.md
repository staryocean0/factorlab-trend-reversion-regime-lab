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

## Frozen protocol

Read and execute:

`docs/research/STATE_FREQUENCY_ADAPTATION_V1_PROTOCOL.md`

The protocol is results-blind with respect to any new state-by-frequency replay. UK/英国预警验证 is explicitly out of scope for this stage.

## Thread-3 continuation progress

Thread 3 resumed from the thread-2 GitHub handoff instead of starting a new research line. The executable harness is now complete through the pre-input stage:

- existing fail-closed measurement core:
  - `src/regime_lab/state_frequency_adaptation.py`
- added frozen inference/statistics helpers:
  - `src/regime_lab/state_frequency_inference.py`
- added inference guardrail tests:
  - `tests/test_state_frequency_inference.py`
- added formal replay runner:
  - `scripts/run_state_frequency_adaptation_v1.py`

The inference layer freezes:

- year/month/AM-PM/15-minute seasonality strata;
- equalized state mass inside matched strata;
- fixed short set `1/2/3/5m` and long set `10/15/30m`;
- trading-day block bootstrap with the same resampled day multiplicities across all seven horizons inside each asset/family;
- Holm family-wise correction across the seven `Delta_B(h)` contrasts;
- no best-of family selection.

The formal runner requires explicit `state-pool path + SHA256 + source revision`, rejects future/tested-outcome surface columns, validates PIT timing, and writes the protocol output bundle under `experiments/state_frequency_adaptation_v1/`.

No empirical state-frequency outcome has been generated yet.

## Hard input gate — still active

The exact state pool used by the prior conversation is still not identifiable from the accessible GitHub tree, issues, commit history, or recovered cross-thread context. Before empirical replay, require an immutable state-pool identity with at least:

```text
symbol
market_time_shanghai
state                 # Unsafe or Recovering
state_available_at
source_revision / artifact hash
```

`state_available_at` must be no later than the decision timestamp. No state may be reconstructed from future returns or from the frequency-test outcomes.

If the state-pool artifact is unavailable, remain at the executable-harness gate; do not manufacture replacement labels.

## Current validation status

Synthetic inference-helper preflight has been exercised outside the repository clone for deterministic matching/contrast/cost-survival/bootstrap logic. The current cloud shell still cannot clone GitHub because DNS resolution fails, so this handoff does **not** claim full repository `python -m pytest -q` success and does not use GitHub Actions as substitute compute.

## Scope constraints

- supplied history is consumed development material, not fresh OOS;
- 2026 remains excluded;
- no UK validation in this stage;
- no production registration or live orders;
- no new winner selected by maximizing total P&L;
- no mutation of other FactorLab repositories;
- do not use GitHub Actions as default research compute.

## Next executable evidence

1. restore the exact prior-thread state-pool artifact without altering it;
2. verify artifact SHA256/source revision and point-in-time availability;
3. run `python scripts/validate_seed.py` and `python -m pytest -q` in a real clone;
4. execute `scripts/run_state_frequency_adaptation_v1.py` once on the frozen `1/2/3/5/10/15/30m` grid;
5. persist raw/matched curves, cost survival, day-block uncertainty, hashes and execution receipt;
6. choose exactly one of the five frozen protocol adjudications only after reading those fixed outputs;
7. preserve the null result if shorter horizons do not become robustly viable.
