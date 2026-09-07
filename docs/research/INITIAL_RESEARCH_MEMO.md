# Initial Research Memo — What Should Be Tested First?

Date: 2026-09-07  
Branch: `research/phase0-regime-protocol`  
Status: conceptual phase-0 research; **no new empirical strategy result yet**.

## Executive conclusion

The repository's broad research direction is valid, but the first experiment should **not** be a direct implementation or optimization of a hand-built `TrendScore` versus `ReversionScore`.

The most defensible first question is:

> **Conditional on the same volatility environment, does past path structure identify whether the market's current directional leg is more likely to continue or reverse over a fixed future physical horizon?**

This reframing matters because volatility, trendability, direction, liquidity/news mechanism, and strategy profitability are different objects. A high-volatility move may be either a genuine directional transition or a temporary shock; volume/amount may accompany either; and a single K-line shape cannot resolve the distinction by itself.

The first-stage research therefore treats the problem as a **conditional continuation/reversal classification problem with an explicit transition region**, then asks whether that state information has economic value for simple symmetric control policies.

## 1. Main methodological correction to the seed framework

The seed framework contains useful candidate variables — autocorrelation, variance ratio, efficiency ratio, volatility ratio, breakout, CLV, wick rejection, amount interactions — but its illustrative point system and thresholds (`rho`, `VR`, score >= 6, etc.) should remain examples rather than become the first model.

Why:

1. threshold scores can silently convert a literature narrative into dozens of tuning degrees of freedom;
2. if the score is optimized against strategy PnL, the state label becomes circular;
3. different physical horizons may naturally have opposite persistence signs;
4. a single full-sample winner can hide year, index, volatility-bucket, and grid instability.

The first phase should instead use continuous targets, coarse preregistered horizons, simple models, and ablations against a volatility-only baseline.

## 2. The key observable axis: continuation vs reversal of the current leg

At time `t`, define a past-only current-leg direction from a fixed trailing window `Ls`:

`d_t = sign(log(P_t) - log(P_{t-Ls}))`.

For future horizon `h`, define:

`CR_t = d_t * (log(P_{t+h}) - log(P_t))`.

This creates a direct behavioral axis:

- positive `CR`: continuation;
- negative `CR`: reversal;
- near-zero `CR`: transition / no strong directional resolution.

This is preferable to labeling a regime from the profit of a complex strategy. It says what the future path did relative to the already-observed leg, without assuming an execution vehicle.

A second, direction-free target — future path efficiency — is required as a cross-check. If `CR` says continuation but future efficiency is very low, the result may reflect a noisy endpoint rather than a clean trend path.

## 3. The first genuinely interesting hypothesis is not “high vol = trend”

The strongest phase-0 hypothesis is an **interaction**:

### Distributed displacement

If recent displacement is spread across many bars, path efficiency is high, and price is accepted outside a prior range, continuation should become more likely.

### Isolated shock

If the same total realized volatility is dominated by one/few bars, followed by rejection or close back inside the prior range, reversal/transition should become more likely.

Therefore the experiment should compare paths at approximately similar volatility but different **shock concentration / displacement morphology**.

Candidate measurements:

- `max(abs(r_i)) / sum(abs(r_i))`;
- `max(r_i^2) / sum(r_i^2)`;
- number/share of bars accounting for 50% or 80% of absolute movement;
- path efficiency;
- breakout acceptance / failed breakout;
- close-location and wick rejection.

This is a more falsifiable statement than “large bar trends” or “large bar reverts.”

## 4. Volatility should be the mandatory baseline, not the answer

The minimum baseline `B0` should contain:

- realized-volatility level;
- short/long volatility ratio;
- recent absolute-return level;
- time-of-day/session controls;
- index identity for pooled diagnostics.

Every proposed regime feature family must show **incremental information over B0**.

This means a feature is not promoted because it has a standalone t-stat or a nice quintile chart. It must improve predictive ordering, calibration, or conditional continuation/reversal separation beyond what volatility and clock effects already explain.

## 5. Persistence metrics should be tested as a family, not as sacred formulas

The natural first family is:

- lag-1 autocorrelation;
- coarse variance ratio;
- path efficiency;
- bar-direction continuity / signed streak.

The literature motivates these as measures of persistence or random-walk deviation, but none should be treated as a universal trading signal.

The relevant test is:

> Do these lagged path measures predict the **sign and magnitude of future continuation/reversal**, after controlling for volatility, and does the relationship transport across STAR50 / CSI1000 and 5m / 1m at matched physical horizons?

If not, the research should not rescue them by adding ever more thresholds.

## 6. Amount should enter only through interactions

The supplied index dataset contains `amount`, not share volume or turnover. It also lacks news, order flow, book depth, signed trades, and IV.

Therefore phase 1 should not claim to distinguish “information trades” from “liquidity trades” causally.

The defensible question is weaker:

> Conditional on price-path morphology, does unusual `amount` help distinguish accepted movement from rejected movement?

Test examples:

- `amount_rank x breakout_acceptance`;
- `amount_rank x CLV`;
- `amount_rank x wick_rejection`;
- `amount_rank x shock_concentration`.

A standalone `high amount -> trend` rule should be considered a null candidate, not the default prior.

## 7. Why 5m should be primary

Phase 1 should use 5m as the primary research plane, 1m as matched-horizon robustness, and 3s only as diagnostic support.

Reasons:

- 1m is more exposed to grid-specific bounce/noise and quality flags;
- 3s has changing observation density and same-second multiple rows, so treating it as a uniform 3-second clock would be invalid;
- 5m provides enough intraday resolution to study 30–120 minute behavior while reducing the temptation to overfit microstructure noise.

An effect that appears only on 1m and fails on matched 5m physical horizons should be downgraded rather than celebrated.

## 8. Cross-index design

STAR50 begins much later than CSI1000, so the primary comparative panel should use the common period beginning 2020-07-23.

The desired evidence order is:

1. estimate the relationship within each index;
2. compare sign / monotonic ordering across indices;
3. test pooled specification with index calibration terms;
4. only then ask whether a common gate is justified.

CSI1000's earlier history can test backward temporal transport, but it is not fresh OOS and should not be mixed into the shared training pool before the common-period relationship is frozen.

## 9. Phase-1 minimal experiment matrix

Primary frequency/horizon grid:

| Item | Frozen candidates |
|---|---|
| Frequency | 5m primary; 1m robustness |
| Past state lookback `L` | 60m, 120m, 240m |
| Current-leg direction `Ls` | 15m, 30m, 60m |
| Future horizon `h` | 30m, 60m, 120m; 240m only if same-session valid |
| Baseline | volatility + absolute return + clock + index |
| Feature ablations | persistence; morphology; breakout; amount interactions; all |
| Model ladder | bins -> linear/ridge -> one shallow nonlinear benchmark |

The purpose of the grid is not to find one magic cell. It is to reveal a **surface**: where continuation/reversal relationships are stable, where they flip with scale, and where evidence is weak.

## 10. What would count as a meaningful phase-1 result?

A promising result would have most of these properties:

1. score buckets show monotonic movement in `CR` or future efficiency;
2. incremental value over volatility baseline exists in multiple years;
3. sign/ordering is similar in both indices, with calibration differences allowed;
4. matched physical-horizon results survive from 5m to 1m;
5. the relationship is not dominated by one event cluster;
6. 2025 project-local historical confirmation does not reverse the frozen conclusion;
7. a simple regime gate improves the relative behavior of symmetric Trend vs Reversion controls without requiring a large parameter search.

A weak or failed result should stop the model ladder early.

## 11. Immediate implementation order

1. Write the exact causal feature/target math whitepaper.
2. Audit 5m/1m session structure and quality flags for both indices.
3. Implement synthetic-path tests before touching empirical model selection:
   - monotone path;
   - oscillatory path;
   - isolated shock then flat;
   - isolated shock then reversal;
   - distributed trend;
   - breakout then failure.
4. Implement `B0` and feature-family measurements.
5. Produce 2020–2024 ablation tables and stability panels.
6. Freeze candidate family.
7. Open 2025 project-local historical confirmation.
8. Only if phase 1 survives, design a phase-2 economic gate/backtest.

## 12. Evidence status and execution limitation

The GitHub repository is readable and writable through the authorized integration. The current general execution container, however, could not resolve `github.com`, so `git clone`, `scripts/validate_seed.py`, and `pytest` have **not** been executed in this session. No execution result is claimed.

The phase-0 design used the repository research framework / bibliography and publicly visible paper abstracts or official summaries. The privately supplied PDF full texts were not available to this session, so no claim of full-text review is made.
