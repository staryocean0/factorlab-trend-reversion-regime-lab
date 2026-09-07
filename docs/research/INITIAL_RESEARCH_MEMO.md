# Initial Research Memo — Strategy-First Reversal / Mean Reversion

Date: 2026-09-07  
Branch: `research/phase0-regime-protocol`  
Status: research direction revised by owner before new empirical strategy results.

## Executive conclusion

The repository should **not** spend its first cycle building a balanced Trend-vs-Reversion classifier.

Trend is being studied externally. This repository's job is now narrower and more useful:

> **Make the reversal / mean-reversion side work as far as it can work, preserve its failures, and let those failures reveal the eventual boundary with trend.**

This changes the role of the earlier continuation/reversal classification idea. It remains useful as a diagnostic, but it is no longer the primary product.

## 1. Why strategy-first is appropriate here

A regime gate built before either side is well understood tends to encode assumptions about where each strategy ought to work.

That creates two risks:

1. the gate can hide a weak reversal strategy by avoiding its hard cases;
2. the eventual "trend vs reversal" boundary can become a hand-designed narrative rather than an empirical complementarity.

A better sequence is:

1. build a simple reversal/MR strategy;
2. measure exactly where it wins and loses;
3. improve it only when the failure suggests a concrete mechanism;
4. later compare the reversal failure surface with the independently discovered trend strength surface.

If the two surfaces are complementary, the final gate will emerge naturally.

## 2. The first unifying mechanism to test

The working mechanism is:

**displacement -> failed continuation -> return toward a causal reference**

This immediately distinguishes three objects that are often conflated:

- a large move;
- evidence that the move is no longer accepted;
- actual reversion toward an equilibrium reference.

A large move by itself is not enough.

## 3. Two baselines, not one abstract classifier

### MR0

Fade price only when it is far from a causal prior-price anchor.

Purpose: establish how dangerous/useful naked mean reversion actually is.

This baseline should not be "protected" from strong trends at first. If it repeatedly loses in accepted breakouts or efficient directional legs, that is valuable evidence.

### REV0

Require an established directional leg, then a failed breakout/rejection in the same direction, then trade the reversal.

Purpose: test whether explicit evidence of failed continuation provides a cleaner turning-point mechanism than stretch alone.

### MR1

Add failed-acceptance confirmation to MR0.

Purpose: test one specific improvement: whether rejection is the missing ingredient in naked mean reversion.

## 4. Why the causal anchor matters

Mean reversion requires a mean/reference.

The first anchor is deliberately plain: an EMA of **prior closes**, not including the signal bar, with a 120-trading-minute physical horizon.

Distance is normalized by prior ATR.

The anchor is frozen at signal time when evaluating "did price revert?", so a moving reference cannot chase price and manufacture a success.

Later iterations may test rolling median, prior-range midpoint, or multi-scale anchors, but only if the first failure atlas gives a reason.

## 5. What we want to learn from failure

The most important first-cycle output may be the losing trades.

For each failure, ask:

- Was the breakout actually accepted?
- Was the prior path unusually efficient?
- Did volatility expand after entry?
- Was the event one part of a large clustered episode?
- Did short-side and long-side reversals behave differently?
- Did the signal disappear on matched 1m/5m measurement?
- Was the gross edge too small relative to plausible costs?

These are future handoff variables to the trend research.

We should not import a trend filter merely because one of these conditions looks dangerous. First measure the danger.

## 6. Minimal implementation already selected

Phase 1 uses:

- 5m primary;
- 1m matched-horizon robustness;
- causal 120m EMA anchor;
- prior 120m ATR scale;
- prior 60m breakout range;
- 60m directional leg for REV0;
- next-bar-open entry;
- fixed 30m / 60m / 120m diagnostic exits;
- frozen-anchor touch outcome.

Initial constants are engineering baselines rather than fitted optimums.

After baseline results are recorded, only coarse perturbations are allowed.

## 7. What is explicitly out of scope

For now this repository will not:

- develop or optimize a trend-following strategy;
- build a Trend-vs-Reversion gating model;
- optimize a two-sided score;
- use PnL to retroactively define the regime;
- patch individual historical episodes with special rules;
- claim fresh OOS from the supplied history;
- claim direct executability of an index-direction diagnostic.

## 8. Immediate implementation order

1. replace the old two-sided protocol with the reversal/MR-first protocol;
2. write exact causal formulas and timing;
3. implement MR0/MR1/REV0 baseline measurements;
4. add synthetic/prefix-invariance tests;
5. audit the real 5m/1m fields and session/quality filters;
6. execute the unchanged baseline;
7. publish the failure atlas before adding filters;
8. iterate one mechanism at a time;
9. only after this side is understood, compare with the separate trend research.

## 9. Current execution limitation

The authorized GitHub integration can read and write the repository. The general execution container used in the earlier handoff could not resolve `github.com`, so full repository validation and empirical runs have not yet been truthfully executed in this session.

The new source and synthetic tests can be prepared and reviewed through GitHub, but no empirical result is claimed until an actual execution path records it.
