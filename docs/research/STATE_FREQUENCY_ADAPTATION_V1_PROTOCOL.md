# State-conditioned frequency adaptation v1 — frozen protocol

Date frozen: 2026-09-08  
Assets: CSI1000 `000852.SH`, STAR50 `000688.SH`  
States: `Unsafe`, `Recovering`  
Status: **results-blind for any new state-by-frequency replay**

## 1. Research question

Test the user's specific hypothesis without turning it into a winner-search:

> When the market enters an `Unsafe` high-volatility/risk state, does the larger available price movement expand the economic viability of shorter physical trading horizons enough to overcome their higher friction sensitivity, relative to `Recovering`?

This is different from either of the following stronger claims, which are **not** assumed:

1. `Unsafe` always favors trend rather than reversion;
2. the shortest frequency is the most profitable frequency.

The prior exploratory handoff already suggests a material increase in 1-minute theoretical friction capacity in `Unsafe`, while a simple `1/2/3/5/10/15/30m` scan did not establish stable higher-frequency profitability. Those observations are consumed development evidence and may not be used to alter the frozen grid below.

## 2. Primary hypotheses and falsifiers

### H1 — friction-budget expansion

For each asset and each fixed control family separately, `Unsafe` should show a larger break-even one-way friction budget than `Recovering` at short horizons (`1/2/3/5m`).

**Falsifier:** the short-horizon friction-budget uplift is absent, sign-inconsistent across the two assets, or only appears in one isolated horizon after multiplicity-aware uncertainty.

### H2 — short-horizon viability-set expansion

At a fixed one-way cost assumption, the set of short horizons with positive net edge should be at least as broad in `Unsafe` as in `Recovering`, and the state difference should not depend on choosing the best-performing strategy family after seeing outcomes.

Primary fixed cost: `3 bp` per one-way position change.  
Sensitivity only: `1, 2, 5 bp`.  
`0 bp` is descriptive gross evidence only.

**Falsifier:** the positive-net short-horizon set does not expand in `Unsafe`, or the apparent expansion disappears under the seasonality-matched comparison.

### H3 — frequency-shift claim requires more than higher volatility

A claim that `Unsafe` genuinely shifts preferred frequency shorter is allowed only if the state-by-horizon relationship survives all of:

- both assets reported separately;
- fixed strategy-family reporting (no ex-post family selection);
- time-of-day seasonality control;
- overlap-aware uncertainty;
- fixed-cost sensitivity;
- no single-horizon dependence.

**Falsifier:** `Unsafe` merely raises gross movement/friction capacity while the net-edge curve remains flat, noisy, or favors equal/longer horizons.

## 3. Data role and hard state-pool gate

Market inputs must come from the repository's verified bounded reader `regime_lab.market_data.load_market_data` and the immutable `data/manifest.json` package. Use `1m` bars as the primary physical clock. `3s` observations are not needed for the primary state-frequency test and must not be used to create a more favorable intraminute outcome definition.

Allowed historical range is bounded by supplied data and ends `2025-12-31`. `2026` is excluded.

The state pool is an external prerequisite from the previous conversation. Before any empirical outcome calculation, freeze and persist:

```text
artifact/path identity
SHA256 or immutable Git identity
state-generation source revision
symbol
market_time_shanghai
state
state_available_at
```

Allowed primary labels are exactly `Unsafe` and `Recovering`. Other labels may be counted in an audit but are not silently remapped.

Point-in-time requirement:

```text
state_available_at <= decision_time
```

Any violation fails closed. Do not regenerate a missing state label from future volatility, future returns, the tested frequency's outcomes, or a centered smoother.

UK/英国预警验证 and UK-derived validation results are explicitly excluded from this stage.

## 4. Frozen horizon grid

The complete candidate grid is fixed before new replay:

```text
H = {1, 2, 3, 5, 10, 15, 30} trading minutes
short = {1, 2, 3, 5}
long  = {10, 15, 30}
```

No additional horizon may be inserted because an observed curve looks promising. Lunch break and overnight time are not counted as trading minutes. An observation whose required past or future physical horizon crosses a session discontinuity is excluded from that horizon and recorded as such.

## 5. Fixed transparent control families

This study is a **strategy-adaptation diagnostic**, not a search for a deployable signal. Use two symmetric fixed controls at each horizon `h`:

### Continuation / trend control

At decision time `t`, define the completed past-horizon log return:

```text
r_past(h,t) = log(C_t / C_{t-h})
signal_trend = sign(r_past)
```

Forward gross signed return:

```text
edge_trend(h,t) = signal_trend * log(C_{t+h} / C_t)
```

### Reversion control

```text
signal_reversion = -sign(r_past)
edge_reversion(h,t) = signal_reversion * log(C_{t+h} / C_t)
```

Zero past return produces zero position and is retained in coverage counts but contributes no directional edge.

No threshold, z-score cutoff, stop, target, confirmation, model fit, or asset-specific parameter is introduced in v1. This prevents frequency results from being confounded with signal optimization.

These controls are diagnostic return transforms on index history, not directly executable index strategies.

## 6. Decision clock and overlap control

Primary sampling uses a deterministic non-overlapping clock **within each horizon**:

- anchor each continuous-auction session segment at its first eligible completed minute;
- sample decisions every `h` trading minutes;
- require a complete past `h` and future `h` within the same continuous session segment;
- state is read only at the sampled decision time.

This produces different counts by horizon but avoids pretending heavily overlapping forward windows are independent.

A dense every-minute replay may be produced only as a secondary descriptive overlay with block/bootstrap or day-clustered uncertainty. It cannot replace the primary non-overlapping result.

## 7. Seasonality control

Because `Unsafe` can concentrate around opening periods or other high-volatility clock locations, the primary state contrast must include a seasonality-matched view.

Within each asset and horizon, stratify by:

```text
calendar year
month
AM/PM session segment
minute-of-segment bucket (15-minute bucket)
```

Report raw state results and matched/weighted results. Do not match on contemporaneous or future volatility because volatility/risk state is part of the hypothesis itself.

If a stratum contains only one state, it contributes to raw coverage but not the matched state contrast.

## 8. Economic metrics

For each `(asset, state, family, horizon)` report at minimum:

```text
n_decisions
active_fraction
mean_gross_edge_bp
median_gross_edge_bp
win_rate_when_active
gross_edge_day_cluster_SE
turnover_units_per_decision
break_even_oneway_cost_bp
net_edge_bp at c = 1,2,3,5 bp
q05 / q01 signed-edge tails
```

Turnover is computed from the sampled position path, not assumed constant. Position is in `{-1,0,+1}`. A transition from `-1` to `+1` costs two one-way units; `0` to `+1` costs one.

For a sample with total gross signed return `G_bp` and total one-way turnover units `T`:

```text
break_even_oneway_cost_bp = G_bp / T
```

when `T > 0`. If `T == 0`, report undefined rather than infinity.

`break_even_oneway_cost_bp` is the primary friction-capacity metric. It is not a broker fee estimate and not evidence of executable profitability.

## 9. Primary state-frequency summaries

Do not select a single best horizon. Persist the whole curve.

For each asset/family:

1. `B_Unsafe(h)` and `B_Recovering(h)` — break-even one-way cost curves;
2. `Delta_B(h) = B_Unsafe(h) - B_Recovering(h)`;
3. `Ratio_B(h)` where denominator is positive and numerically stable;
4. number of short horizons with positive net edge at `3 bp`;
5. weighted mean net edge over the fixed short set and over the fixed long set, with equal horizon weights;
6. state × `log(h)` slope/interactions as descriptive curve summaries, not as the sole acceptance test.

No "best of trend/reversion" aggregate is permitted in the primary table. Families stay separate.

## 10. Statistical uncertainty and multiplicity

The unit of dependence is at least the trading day. Use trading-day clustered uncertainty or a day-block bootstrap for state contrasts.

The seven horizons are a frozen family. Report simultaneous/multiplicity-aware uncertainty for the seven `Delta_B(h)` contrasts per `(asset, family)` using a transparent family-wise procedure (Holm or max-statistic bootstrap). Raw p-values alone are insufficient.

This is consumed historical development evidence. Statistical significance does not make it fresh OOS.

## 11. Integrity audits before interpretation

Persist and pass:

- market manifest/hash validation;
- state-pool artifact hash and schema;
- exact timezone (`Asia/Shanghai`);
- state availability audit;
- duplicate state timestamp audit;
- one state per `(symbol, decision_time)`;
- session-boundary exclusion counts by horizon;
- no 2026 rows;
- no UK rows/input dependency;
- no future-return columns or tested outcomes in the state-pool feature surface;
- deterministic rerun identity.

Any failure above blocks scientific interpretation rather than being silently repaired.

## 12. Required outputs

Write new outputs only under:

```text
experiments/state_frequency_adaptation_v1/
```

Required files:

```text
RESULT_CARD.md
summary.json
input_identity.json
state_pool_audit.json
frequency_curve.csv
seasonality_matched_curve.csv
cost_survival.csv
uncertainty.csv
execution_receipt.json
```

`execution_receipt.json` must record code commit, command, Python/package versions, input hashes, start/end times, exit code and output hashes.

## 13. Allowed adjudications

Exactly one primary adjudication should be used:

- `unsafe_expands_short_horizon_economic_viability`
- `unsafe_expands_friction_budget_but_not_short_horizon_viability`
- `state_frequency_shift_is_asset_or_family_specific`
- `no_robust_state_conditioned_frequency_shift`
- `state_pool_or_temporal_integrity_gate_failed`

Do not invent a more favorable verdict after results are seen.

## 14. What v1 cannot claim

Even a positive result does not establish:

- executable CSI1000/STAR50 index trading profits;
- actual IM/ETF spread/slippage/market-impact economics;
- a production strategy router;
- that `Unsafe` should always use the shortest bar;
- that trend or reversion is universally superior;
- fresh out-of-sample validation.

A positive v1 result only supports a narrower claim: **the state changes the economic viability curve across fixed physical horizons in a reproducible historical diagnostic.**

## 15. Immediate execution order

1. freeze this protocol and takeover entry;
2. identify/import the exact non-UK state-pool artifact from the prior thread without altering it;
3. implement the fail-closed runner and unit tests against synthetic state/price paths;
4. run integrity gates;
5. run the fixed historical replay once;
6. write all results including nulls/failures;
7. only then decide whether an executable carrier study is warranted.
