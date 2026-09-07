# Phase 0 — Trend / Reversion Regime Preregistered Protocol

Status: **preregistered before any new strategy/backtest result is inspected**  
Project: `factorlab-trend-reversion-regime-lab`  
Subjects: STAR50 `000688.SH`, CSI1000 `000852.SH`  
Evidence role: supplied history is `consumed_development_material`, not fresh OOS.

## 1. Research question

Primary question:

> After controlling for the common volatility environment and clock/session effects, can information available at time `t` distinguish whether the market's current directional move is more likely to **continue**, **reverse**, or remain **ambiguous/transitionary** over a fixed future physical horizon?

This is intentionally narrower than directly searching for the most profitable TrendScore/ReversionScore. The first objective is **state predictability**, not strategy optimization.

The project separates four layers:

1. **state measurement** from past-only observations;
2. **future behavioral target** describing continuation/reversal without execution assumptions;
3. **simple policy differential** as a secondary economic diagnostic;
4. **real executable strategy** only after the first three survive robustness tests.

## 2. Core falsifiable hypotheses

### H0 — volatility is amplitude, not regime direction

A model using only realized-volatility level/ratio and session/time-of-day controls should not be treated as sufficient evidence for Trend vs Reversion selection.

**Failure of the research thesis:** if richer past-path variables do not add stable predictive information beyond this volatility-only baseline, stop before building a complex gate.

### H1 — path persistence has incremental information

Lagged path-dependence variables such as rolling return autocorrelation, variance ratio, and path efficiency should provide incremental predictive power for future continuation vs reversal after volatility controls.

Expected direction:

- higher positive dependence / higher directional efficiency -> more continuation;
- stronger negative dependence / low directional efficiency -> more reversal or transition.

No fixed numerical threshold is assumed.

### H2 — shock morphology matters conditional on equal volatility

At similar realized-volatility levels, a displacement concentrated in one/few bars should behave differently from a displacement distributed across many bars.

Primary interaction to test:

- **distributed directional displacement + breakout acceptance** -> continuation prior increases;
- **isolated shock + rejection / return into prior range** -> reversal or transition prior increases.

A large move alone is not defined as either trend or mean reversion.

### H3 — volatility expansion interacts with path structure

Volatility expansion is hypothesized to be conditional rather than directional:

- expansion following efficient directional movement / accepted breakout -> continuation more likely;
- expansion with inefficient path / rejection / isolated shock -> reversal or transition more likely.

### H4 — amount is conditional evidence, not a standalone direction variable

`amount` may add information only through interaction with price acceptance/rejection and path morphology. `amount_z` alone is not expected to have a stable universal sign.

The dataset has no share volume, turnover, OFI, depth, or signed trade direction; these must not be synthesized.

### H5 — scale consistency is required

A useful state relationship should survive at matched **physical horizons** across 5m (primary) and 1m (robustness) data. Effects that exist only at one grid and collapse when the same physical horizon is measured on another grid are downgraded as microstructure/grid-sensitive.

3s observations are diagnostic support only in the first phase, not a model-search grid.

### H6 — cross-index transport matters more than pooled fit

A relationship is stronger evidence if its sign/rank structure transports between STAR50 and CSI1000, even if calibration differs. A pooled fit improvement that relies on index identity interactions but fails within-index transport is not sufficient.

## 3. Data roles and sample boundaries

### 3.1 Primary comparable sample

Use the common 1m/5m availability window:

- start: `2020-07-23`
- end: `2025-12-31`

Both indices must use intersected trading days for direct cross-index comparisons.

### 3.2 CSI1000 earlier history

CSI1000 pre-`2020-07-23` history is reserved for **backward temporal transport / historical robustness** only. It must not be used to tune a shared STAR50/CSI1000 model and then described as independent OOS.

### 3.3 Project-local chronological roles

Because all supplied history is already consumed material, these names describe only this project's internal discipline:

- `development_fit`: `2020-07-23` through `2022-12-30`
- `development_calibration`: calendar year `2023`
- `development_validation`: calendar year `2024`
- `historical_confirmation_consumed`: calendar year `2025`

`2025` must not be used for threshold/model-family selection before the phase-1 specification is frozen. It is **not** fresh OOS.

### 3.4 Session rule

Initial tests use continuous auction sessions only. Auction / after-hours observations are excluded unless a later protocol explicitly studies them.

Lunch and overnight gaps are not silently converted into ordinary adjacent intraday returns. Features and labels must explicitly define whether a horizon is allowed to cross a session boundary.

Primary phase-1 target family: **same-session horizons only**. Cross-session behavior is a later extension.

## 4. Frequency and physical-horizon contract

Primary frequency: **5m**.  
Robustness frequency: **1m**.  
Diagnostic-only frequency: **3s**.

No new DataHub-style wall-clock OHLC product will be created locally.

Predeclared future horizons (trading minutes):

- `h = 30m`
- `h = 60m`
- `h = 120m`
- `h = 240m` only where the same-session contract is valid; otherwise omit rather than bridge silently.

Predeclared trailing state lookbacks:

- `L = 60m`
- `L = 120m`
- `L = 240m`

These are a coarse scientific grid, not a fine optimizer. No one-minute threshold sweep is allowed in phase 1.

## 5. Direction-independent state target and continuation target

The project will not define regime using the PnL of a complex strategy.

Two complementary future targets are preregistered.

### 5.1 Future path efficiency target

For future subreturns inside horizon `h`:

`future_efficiency = abs(P[t+h] - P[t]) / sum(abs(delta P))`

or the log-price equivalent.

Purpose: measure whether the future path is directionally efficient or oscillatory. This target does **not** decide bullish/bearish direction.

### 5.2 Continuation / reversal target relative to the current leg

Define a trailing direction signal using only past data:

`d_t(Ls) = sign(log(P[t]) - log(P[t-Ls]))`

with preregistered signal lookbacks:

- `Ls = 15m`
- `Ls = 30m`
- `Ls = 60m`

Then define:

`continuation_return(t,h,Ls) = d_t(Ls) * (log(P[t+h]) - log(P[t]))`

Interpretation:

- `> 0`: continuation of the current leg;
- `< 0`: reversal relative to the current leg;
- near zero: ambiguous / transition.

For comparability across volatility regimes, the primary analysis also reports a volatility-normalized form using a **past-only** scale estimator. Future volatility must not enter the feature normalization at decision time.

Near-zero prior legs are not forced into Trend or Reversion. They form an explicit weak-direction / transition stratum.

## 6. Initial feature families

All features must be point-in-time and past-only.

### B0 — mandatory baseline controls

- time-of-day / session segment;
- past realized volatility level;
- short/long volatility ratio;
- recent absolute-return level;
- index identity when pooled analyses are used.

### F1 — persistence / anti-persistence

- rolling lag-1 return autocorrelation;
- coarse variance-ratio measures;
- path efficiency ratio;
- signed streak / bar-direction continuity where causally defined.

### F2 — shock concentration and morphology

- max absolute return / sum absolute returns;
- max squared return / sum squared returns;
- number/share of bars responsible for 50% and 80% of absolute displacement;
- large-body ratio, close-location value, wick rejection;
- gap-like/session-opening features only in explicitly separate analyses.

### F3 — breakout acceptance / rejection

- close relative to lagged rolling high/low;
- distance outside prior range;
- intrabar break followed by close back inside prior range;
- persistence after break over already-closed bars only.

### F4 — amount interactions

- rolling robust z/rank of log `amount`;
- amount x close-location / breakout acceptance;
- amount x rejection / shock concentration.

`amount` is never renamed or interpreted as share volume/turnover.

## 7. Candidate and search budget

Phase 1 is deliberately small.

Permitted model ladder:

1. conditional bin / quantile tables;
2. additive linear/logistic or ridge model;
3. one shallow nonlinear benchmark (e.g. depth-limited tree ensemble) **only after** the first two are frozen and reported.

Not permitted in phase 1:

- deep learning;
- HMM/change-point family sweep;
- fine threshold optimization;
- feature selection by full-sample Sharpe;
- separate ad-hoc rule patches for specific years/events.

Model-family budget: maximum **3** families above.  
Feature-family ablations: `B0`, `B0+F1`, `B0+F2`, `B0+F3`, `B0+F4`, `B0+F1+F2+F3+F4`.  
Primary frequency/horizon grid is frozen by Sections 4–5.

Every attempted specification must be logged; failed attempts remain in the repository.

## 8. Primary evaluation metrics

### State/behavior prediction

For continuous targets:

- Spearman rank IC;
- conditional mean by predicted-score quintile/decile;
- monotonicity of continuation/reversal outcome across score buckets;
- cross-year and cross-index sign stability.

For optional discretized Trend / Reversion / Transition labels:

- balanced accuracy;
- macro F1;
- one-vs-rest AUC;
- calibration / Brier score;
- confusion matrix by volatility bucket and index.

Thresholds used to create discrete labels must be estimated on fit/calibration data only.

### Incremental-value requirement

Every richer specification must be compared against `B0` volatility/session controls.

A research family is not promoted because its standalone score looks significant. It must show incremental and reasonably stable improvement over `B0`.

## 9. Secondary policy differential

Only after the behavioral targets show stable structure, evaluate two transparent diagnostic policies sharing the same direction signal:

- Trend control: follow `d_t`;
- Reversion control: take `-d_t`.

The regime gate is evaluated by whether it improves the **difference** between these two controls in the predicted regime, not by inventing a separate direction signal for each.

These are index-direction diagnostics, not directly tradable A-share cash strategies.

Costs are reported only when a concrete execution carrier is specified; until then, gross index-direction results must be labelled as diagnostic.

## 10. Purge, overlap, and dependence

- labels extending `h` into the future require at least `h` purge at fold boundaries;
- overlapping horizons are dependent observations and must not be treated as IID sample-size inflation;
- standard errors / resampling must use temporal blocks at least as long as the effective label horizon;
- normalization, quantiles, and thresholds are fitted inside the allowed fit/calibration region only.

No random train/test shuffle is permitted.

## 11. Failure / stop conditions

Stop or narrow the research if any of the following occurs:

1. `F1–F4` fail to improve materially over volatility/session baseline `B0` across years;
2. effect signs flip repeatedly between STAR50 and CSI1000 without an interpretable calibration explanation;
3. a result appears only on 1m but disappears at matched 5m physical horizons and is consistent with microstructure noise;
4. performance depends on one narrow threshold or one isolated event cluster;
5. 2025 confirmation materially contradicts the frozen 2020–2024 result;
6. the apparent regime advantage exists only when the same return information is reused as both feature and target in a temporally invalid way.

A failed result is a research result and must be retained.

## 12. Literature role

The initial mechanism prior is motivated by the repository's literature map, especially:

- `R-A1` — time-series momentum and horizon dependence;
- `R-M1/R-M2` — variance-ratio / mean-reversion evidence;
- `R-M3/R-M5` — liquidity-driven reversal vs information/news continuation;
- `R-C5` — market-state dependence of momentum sign in China;
- `R-S1/R-S2/R-S3` — multiple testing / backtest-overfitting controls.

This protocol does **not** claim that the current AI session has read the privately supplied PDF full texts. It uses the repository framework and bibliographic metadata plus publicly visible abstracts/official summaries for phase-0 design.

## 13. Phase-1 acceptance criteria

Phase 1 is complete only when the repository contains:

1. a causal feature/target whitepaper with exact formulas and observation timing;
2. unit tests for synthetic monotone, oscillatory, isolated-shock, distributed-trend and failed-breakout paths;
3. a data audit for both indices/frequencies/session filters;
4. preregistered attempt ledger entries;
5. baseline `B0` and feature-family ablation results for 2020–2024;
6. only after freeze, the 2025 consumed historical confirmation;
7. a RESULT_CARD stating failures, limitations, and whether phase 2 is justified.

No strategy promotion or production registration is authorized by this protocol.
