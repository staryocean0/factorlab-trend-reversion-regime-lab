# Research Frontier — Reversal / Mean-Reversion after v0.1–v0.7

Date: 2026-09-07  
Branch: `research/phase0-regime-protocol`  
Scope: STAR50 `000688.SH`, CSI1000 `000852.SH`, 5m common history `2020-07-23`–`2024-12-31`  
Evidence role: consumed historical development material; **not fresh OOS**. 2025 remains unopened in these iterations.

## Executive state

The owner-directed strategy-first pivot has now produced a useful negative/conditional research frontier.

We have **not** found a robust standalone reversal or mean-reversion strategy yet.

What has been learned is more specific:

1. fading absolute index displacement is strongly wrong on average;
2. single-bar failed breakout is not a reliable turning point;
3. waiting one generic reversal-direction bar does not rescue the event;
4. requiring a close through the failed-break bar's opposite extreme still does not rescue trend-reversal candidates;
5. replacing ATR stretch with a robust residual distribution improves the *center* of some very-short-horizon MR cells, but tail continuation keeps the mean non-positive;
6. simply demanding a more extreme residual does not produce a general monotonic improvement;
7. a separate cross-index relative-value MR mechanism is also negative overall, but its sign flips materially across years: 2022–2023 are relatively MR-friendly while 2020/2024 are not.

Therefore the immediate research problem is no longer "find the best reversal threshold." It is:

> **Why does a re-entry event become genuine mean reversion in some historical environments but persistent continuation in others?**

This question should be answered from the reversal side's observable pre-entry variables first. Do **not** import the separate trend strategy or build a Trend-vs-Reversion gate yet.

---

## v0.1 — absolute-price MR0 / MR1 / REV0

### Mechanisms

- `MR0`: fade `|stretch_atr| >= 2` relative to a causal prior-close EMA.
- `MR1`: MR0 plus same-bar failed acceptance of the lagged range.
- `REV0`: established efficient/displaced 60m leg plus same-bar failed breakout; trade opposite the leg.

### Result

All primary 30/60/120m strategy/index cells were negative.

Representative means in bps:

| Strategy | Index | 30m | 60m | 120m |
|---|---|---:|---:|---:|
| MR0 | STAR50 | -3.81 | -5.77 | -10.46 |
| MR0 | CSI1000 | -3.65 | -4.57 | -7.46 |
| REV0 | STAR50 | -4.80 | -8.31 | -16.40 |
| REV0 | CSI1000 | -2.64 | -4.52 | -8.74 |

MR0 was also excessively dense: roughly 16.8 signal bars per active day in STAR50 and 20.5 in CSI1000. Cluster-onset-only results stayed negative, so overlap was not the sole cause.

**Decision:** reject naked ATR-stretch fade and same-bar failed-break reversal as trading candidates.

---

## v0.2 — short-horizon path anatomy

Question: did the signal briefly revert at 5–15m and only fail because 30–120m fixed holding was too long?

### Result

No. Mean return was already negative at 5m:

- MR0 STAR50 ≈ -0.70 bps;
- MR0 CSI1000 ≈ -1.07 bps;
- MR1 STAR50 ≈ -0.28 bps;
- MR1 CSI1000 ≈ -0.06 bps;
- REV0 STAR50 ≈ -0.47 bps;
- REV0 CSI1000 ≈ -0.28 bps.

Frozen-anchor distance also tended to worsen from the first short horizon.

**Decision:** the main problem is not simply "hold shorter." Candidate/confirmation geometry is wrong.

---

## v0.3 — one completed reversal-direction bar

Candidate at close `t-1`; require the next completed close-to-close bar to move in the intended fade direction; then enter at open `t+1`.

No magnitude threshold was added, so the experiment isolated confirmation timing.

### Result

No robust rescue. REV0 became worse at longer horizons. CSI1000 MR variants reached only near-zero short-horizon cells, not stable positive edge.

**Decision:** reject the idea that the baseline is only "one bar too early."

---

## v0.4 — structural confirmation / absolute re-entry

- `MR_REENTRY`: previous ATR-stretch was outside ±2 and current completed bar crossed back inside the same band.
- `REV_STRUCT`: prior REV0 candidate, then next close must cross the candidate bar's opposite extreme.

### Result

`REV_STRUCT` remained negative at every tested horizon in both indices, e.g.:

- STAR50 5m ≈ -1.27 bps, 120m ≈ -11.66 bps;
- CSI1000 5m ≈ -1.05 bps, 120m ≈ -18.88 bps.

`MR_REENTRY` showed a small CSI1000 short-horizon positive pocket but did not transport to STAR50 or longer horizons.

**Decision:** pause the current **trend-reversal event family**. Do not keep stacking confirmations on failed breakout. Continue the mean-reversion line with a better definition of abnormal displacement.

---

## v0.5 — robust absolute residual re-entry

Kept the causal prior-close EMA anchor but replaced single-bar ATR displacement with:

`residual_t = close_t - anchor_t`

and standardized current residual against the strictly prior 240-trading-minute residual distribution using rolling median and `1.4826 * MAD`.

Signal occurs only when the robust residual z-score re-enters from outside ±2.

### Result

Still no positive all-sample mean, but failure changed character.

Examples:

- CSI1000 5m: mean ≈ -0.20 bps, **median +0.64 bps**, win rate 51.95%, central-90% mean ≈ +0.08 bps;
- STAR50 30m: mean ≈ -0.31 bps, **median +0.45 bps**, win rate 50.51%, central-90% mean ≈ +0.26 bps.

This is materially different from v0.1: ordinary events can show weak central reversion, while continuation tails erase it.

Year transport remains poor. Example CSI1000 5m mean:

- 2020 ≈ -1.08 bps;
- 2021 ≈ +0.08;
- 2022 ≈ +1.01;
- 2023 ≈ +0.74;
- 2024 ≈ -2.08.

**Decision:** retain robust residual re-entry as a useful research coordinate, not a strategy winner. Tail continuation becomes a primary failure object.

---

## v0.6 — severity surface

Question: if an extreme is a genuine MR setup, does re-entry after a *more severe* prior robust residual extreme monotonically improve returns?

Frozen coarse thresholds: `2.0 / 2.5 / 3.0`. All cells retained; no winner search.

### Result

The global monotonicity hypothesis fails.

- STAR50: strict mean improvement only at 5m; false at 10/15/30/60/120m.
- CSI1000: strict mean improvement at 5m and 10m only; false at 15/30/60/120m.

At 5m:

- STAR50: -0.15 / -0.13 / +0.02 bps for z 2/2.5/3;
- CSI1000: -0.20 / +0.25 / +0.71 bps.

But longer-horizon CSI1000 can become *more negative* as severity increases; at 120m the means were approximately -7.18 / -9.25 / -10.78 bps.

**Decision:** reject "more extreme => more mean reverting" as a general law. Do not select z=3 as a winner from the ultra-short CSI pocket.

Run: `34100286128`.  
Artifact: `robust-mr-threshold-surface-v0-6`, ID `10010203295`, digest `sha256:746c707bf0774829b1c15db664d174cda1a9ea895e9e2d9f8d65f7ad68535303`.

---

## v0.7 — cross-index relative-value mean reversion

This is a distinct MR family, not a trend filter.

### State

On synchronized 5m STAR50 / CSI1000 bars:

1. measure the same-day 60-trading-minute relative log return
   `STAR return - CSI return`;
2. do not allow the 60m state window to bridge trading days;
3. standardize against the most recent 48 **valid, strictly prior** relative-dislocation observations with robust median/MAD;
4. signal only on re-entry from outside ±2;
5. +1 = long STAR / short CSI; -1 = short STAR / long CSI;
6. equal-notional gross diagnostic enters both legs at next-bar open.

Audit:

- 51,792 synchronized rows;
- 1,079 common trading days;
- 38,844 valid same-day 60m relative-dislocation rows;
- 38,796 valid causal z rows;
- 1,613 signals across 835 days;
- 787 long-STAR and 826 short-STAR signals.

### All-sample result

| Horizon | Mean bps | Median bps | Win rate | Central-90% mean bps |
|---:|---:|---:|---:|---:|
| 5m | -0.28 | -0.18 | 49.40% | -0.11 |
| 10m | -0.12 | +0.04 | 50.13% | +0.10 |
| 15m | -0.64 | +0.22 | 50.45% | -0.04 |
| 30m | -1.04 | +0.10 | 50.13% | -0.12 |
| 60m | -1.49 | -0.79 | 48.61% | -0.79 |
| 120m | -3.76 | -0.90 | 48.93% | -2.57 |

So relative-value MR also fails as a stable standalone baseline.

### Critical year dependence

The same rule changes sign materially by year.

Mean bps by year:

| Year | 5m | 10m | 15m | 30m | 60m | 120m |
|---|---:|---:|---:|---:|---:|---:|
| 2020 | -0.65 | -1.48 | -1.85 | -1.92 | -9.98 | -17.37 |
| 2021 | -0.61 | +0.13 | -0.53 | -2.22 | -4.28 | -6.24 |
| 2022 | +0.48 | +0.63 | +0.86 | +0.54 | +0.89 | +0.01 |
| 2023 | +0.07 | +0.38 | +0.16 | +0.35 | +2.64 | +1.89 |
| 2024 | -0.98 | -1.18 | -2.82 | -2.82 | -2.21 | -5.03 |

The sign flip is too systematic to ignore, but too unstable to promote.

All-sample directional mean also differs:

- long STAR / short CSI: negative at all tested horizons;
- short STAR / long CSI: roughly flat/positive at 10–60m but negative at 5m and 120m.

This asymmetry is descriptive evidence, not permission to select one side after seeing the result.

**Decision:** reject v0.7 as a stable strategy. Promote **environment dependence of re-entry success** to the current research frontier.

Run: `34100826456`.  
Head: `1ea6ca281ad2b4515e02711e746a86d488138d42`.  
Artifact: `relative-mean-reversion-v0-7`, ID `10010413195`, digest `sha256:e97c18050054914de0055c5a140b012181312a39d9387065106a27b6de0c8427`.

---

# What is now rejected / paused

## Rejected as current trading candidates

- naked absolute-price ATR stretch fade;
- same-bar failed-breakout reversal;
- one generic reversal-direction confirmation bar;
- opposite-extreme structural confirmation of the same REV0 family;
- robust absolute residual re-entry as a universal rule;
- "more severe robust-z extreme => stronger MR" as a universal rule;
- first simple cross-index relative-dislocation re-entry as a universal rule.

## Paused

The current **trend-reversal event family** is paused. It has received multiple logically stronger confirmations and remained negative. Do not continue adding more candlestick-style confirmation clauses unless a new mechanism justifies reopening it.

---

# Current live hypothesis

The best surviving research statement is deliberately weaker than a strategy:

> **A re-entry event can contain weak short-horizon mean reversion, but whether it turns into genuine reversion or renewed continuation is strongly environment-dependent.**

Evidence supporting this statement:

- v0.5 produces positive medians / central means in selected short-horizon cells while full means stay non-positive;
- v0.6 shows severity alone does not resolve the continuation tail;
- v0.7 shows a particularly clear calendar sign flip, with 2022–2023 much more MR-friendly than 2020/2024.

This is exactly the type of problem that may later become complementary with the independent trend research. **Do not perform that merge yet.** First describe the reversal-side failure environment using only variables available before entry.

---

# Next phase: failure atlas, not strategy gating

The next experiment should **not change the entry rule**. Freeze v0.5 and v0.7 events and characterize winners vs continuation failures using pre-entry coordinates only.

Priority coordinates:

1. **common volatility state** — prior-only realized volatility level;
2. **volatility expansion** — short prior RV / long prior RV;
3. **relative/path efficiency** — was the preceding move distributed and efficient or oscillatory?;
4. **common-market displacement** — did both indices move strongly in the same direction while the relative leg diverged?;
5. **cross-index return correlation** — prior-only correlation level;
6. **shock concentration** — whether recent movement is dominated by one/few bars;
7. **relative severity** — keep as a descriptive coordinate even though v0.6 falsified it as a universal monotonic rule;
8. **time of day / session position**;
9. **direction** — long-STAR vs short-STAR, long-index vs short-index absolute MR;
10. `amount` interactions only with correct semantics (CNY amount, not volume/turnover).

The first objective is a **failure atlas**, not a classifier:

- report conditional return distributions;
- report event counts and year transport;
- identify whether failure conditions are stable across STAR/CSI and absolute/relative MR;
- keep every tested coordinate in the attempt ledger;
- do not call a condition a "trend regime" merely because MR loses there.

Only if one or more pre-entry failure coordinates remain stable across years and mechanisms should a later phase test whether they can act as a causal MR abstention/risk-control rule. The independent trend project can be compared only after that evidence exists.
