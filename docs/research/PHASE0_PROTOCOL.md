# Phase 0 — Reversal / Mean-Reversion Strategy-First Protocol

Status: **supersedes the initial two-sided Trend-vs-Reversion gate design before any new strategy result is inspected**  
Project: `factorlab-trend-reversion-regime-lab`  
Subjects: STAR50 `000688.SH`, CSI1000 `000852.SH`  
Evidence role: supplied history is consumed development material, not fresh OOS.

## 1. Owner-directed scope

The current research track is intentionally one-sided:

> **Build and iterate trend-reversal / mean-reversion strategies first. Do not research a trend-following strategy and do not force a Trend-vs-Reversion regime gate yet.**

A separate external research track is studying trend. This repository should discover the reversal side on its own terms. Only after reversal/MR produces a stable policy and a clear failure atlas should the two research tracks be compared for complementarity.

Therefore phase 1 does **not** optimize a `TrendScore`, does **not** evaluate a symmetric trend control, and does **not** predefine a final strategy arbitration rule.

## 2. Two related but distinct objects

### Mean reversion

Mean reversion means price is materially displaced from a causal reference level and subsequently moves back toward that reference.

It requires:

1. a causal anchor available at decision time;
2. a scale for "far from anchor";
3. a return-to-anchor outcome or economically equivalent convergence measure.

### Trend reversal

Trend reversal means an already-observed directional leg stops being accepted and a move in the opposite direction follows.

It requires:

1. an already-established directional leg;
2. evidence that continuation failed or was rejected;
3. an opposite-direction outcome.

The two mechanisms can overlap. A failed upside breakout far above a causal anchor can be both a trend-reversal event and a mean-reversion event. Phase 1 will measure them separately before deciding whether they should be unified.

## 3. Strategy-first research thesis

The initial candidate mechanism is:

> **displacement -> failed acceptance / rejection -> return toward a causal anchor**

This is deliberately stronger than "large move -> fade it".

The first iteration should expose where this simple idea fails. Those failures are not to be repaired immediately with a trend gate. They become a structured failure atlas for later comparison with the external trend research.

## 4. Baseline strategy family

The exact formulas and observation timing are in `docs/research/REVERSAL_MR_WHITEPAPER.md`.

### MR0 — stretch-only mean reversion

At completed bar `t`:

- causal anchor: prior-close EMA over 120 trading minutes;
- scale: ATR estimated from bars strictly before `t`, over 120 trading minutes;
- stretch: `(close_t - anchor_t) / ATR_past_t`;
- baseline trigger: `|stretch| >= 2.0`;
- direction: trade toward the anchor.

This intentionally weak baseline tests whether "extreme displacement alone" has value. It is expected to reveal catching-a-falling-knife / fading-a-breakout failure modes.

### MR1 — stretch plus failed acceptance

MR0 plus:

- positive stretch must also have an upside break of the lagged 60-minute range that closes back inside;
- negative stretch must also have a downside break of the lagged 60-minute range that closes back inside.

MR1 asks whether explicit rejection materially improves MR0.

### REV0 — failed breakout after an established leg

A directional leg is measured over 60 trading minutes.

Baseline requirements:

- leg path efficiency >= 0.60;
- absolute leg displacement >= 1.50 prior ATR;
- the current bar attempts to break the lagged 60-minute range in the leg direction;
- the bar closes back inside that prior range.

The trade is opposite the prior leg.

These constants are first-iteration engineering baselines, not claimed natural thresholds. They are recorded before empirical strategy results and should receive only coarse robustness perturbations after the baseline is reported.

## 5. Timing and diagnostic execution

A signal is observed only after bar `t` is closed.

Primary diagnostic execution:

- entry: open of bar `t+1`;
- exit: close after 30, 60, or 120 trading minutes;
- no same-bar fill;
- no intrabar stop/target ordering assumptions in the first iteration;
- diagnostic returns are masked when they require crossing into another trading day.

The first phase is an **index-direction diagnostic**, not a claim that the cash index is directly tradable.

A second outcome is the probability/time for future price to touch the **anchor frozen at signal time**. The anchor must not move retrospectively to make a trade look successful.

## 6. Primary data plane

Primary: 5m bars.  
Robustness: 1m bars at matched physical trading-minute horizons.  
3s: diagnostic only until a separate high-frequency contract is justified.

Direct cross-index comparisons use the common history beginning `2020-07-23`.

Project-local chronology:

- development: `2020-07-23` through `2022-12-30`;
- iteration/calibration: calendar `2023`;
- validation: calendar `2024`;
- consumed historical confirmation: calendar `2025`.

All supplied history remains previously consumed material. `2025` is not fresh OOS.

## 7. What the first result table must contain

For every baseline and horizon, separately for STAR50 / CSI1000 and up-reversal / down-reversal:

- signal/event count;
- gross next-bar-open event return: mean and median;
- win rate;
- return quantiles and tail loss;
- probability of touching the frozen causal anchor;
- bars-to-anchor conditional on a hit;
- yearly stability;
- event clustering concentration;
- performance by volatility bucket;
- performance by shock concentration;
- performance by prior-leg efficiency;
- performance by failed-break vs accepted-break context.

The purpose is not to maximize a single Sharpe number. The purpose is to discover whether a reproducible reversal mechanism exists and where it breaks.

## 8. Failure atlas

Every materially losing or unstable event family should be assigned to an observable failure bucket when possible.

Initial buckets:

1. **accepted breakout** — price leaves the old range and does not return;
2. **persistent efficient leg** — stretch becomes larger after entry;
3. **isolated shock without rejection**;
4. **volatility regime expansion**;
5. **session-edge / overnight contamination**;
6. **event clustering** — many signals are effectively one market episode;
7. **direction asymmetry** — long reversals and short reversals behave differently;
8. **grid sensitivity** — 5m and matched 1m disagree;
9. **cost fragility** — gross edge too small to survive plausible friction.

A failure bucket may later map naturally to a trend-side strength. That mapping is explicitly deferred until this repository has measured the failure itself.

## 9. Iteration discipline

The research loop is:

1. run MR0 and REV0 unchanged;
2. produce complete baseline and failure atlas;
3. run MR1 to test the single hypothesis "rejection confirmation matters";
4. change **one mechanism at a time**;
5. keep failed iterations in the attempt ledger;
6. prefer structural fixes over a growing list of event exceptions;
7. only after a stable reversal policy exists, compare its failure surface with the external trend research.

No fine threshold grid is permitted before the baseline/failure report exists.

## 10. Early robustness budget

After the unchanged baseline is recorded, only the following coarse perturbations are allowed in the first robustness pass:

- stretch threshold: `1.5 / 2.0 / 2.5`;
- leg efficiency: `0.50 / 0.60 / 0.70`;
- leg displacement: `1.0 / 1.5 / 2.0 ATR`;
- fixed diagnostic holding: `30 / 60 / 120 trading minutes`;
- 5m primary vs matched 1m.

This is a sensitivity surface, not a winner search. Every cell is retained.

## 11. Evidence and execution guards

- `amount` is CNY transaction amount for the index source, not share volume or turnover.
- No OFI, order-book depth, signed trades, IV, or news are available; do not synthesize them.
- Price/feature normalization must be causal.
- Signals at close `t` cannot fill before next tradable bar.
- Random time shuffles are not valid train/test splits.
- Overlapping event horizons are dependent observations.
- 2026 data are outside the supplied package and must not be opened from other repositories.
- No production registration or live trading authority is implied.

## 12. Phase-1 completion

Phase 1 is complete only when the repository has:

1. exact strategy whitepaper and causal timing;
2. implemented MR0/MR1/REV0 feature + signal code;
3. synthetic tests including prefix invariance and failed-break behavior;
4. two-index 5m/1m data/session audit;
5. baseline result tables and plots;
6. failure atlas;
7. coarse robustness surface;
8. 2025 consumed historical confirmation only after earlier iterations are frozen;
9. `RESULT_CARD.md` plus full attempt ledger.

The next phase will be determined by what actually fails, not by a pre-written Trend-vs-Reversion arbitration architecture.
