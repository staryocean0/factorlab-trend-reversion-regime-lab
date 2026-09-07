# Reversal / Mean-Reversion Failure Atlas — v0.1 through v0.10

Date: 2026-09-07  
Research line: reversal / mean-reversion only  
Subjects: STAR50 `000688.SH`, CSI1000 `000852.SH`  
Evidence role: consumed historical development material; **not fresh OOS**.

## Executive conclusion

The first ten iterations do **not** support a broad statement such as “extreme index moves mean-revert” or “failed continuation is generally profitable to fade.”

The empirical picture is narrower:

1. **STAR50:** every simple reversal/MR family tried so far is negative or at best locally near zero. The 1m path-resolution experiments show that 5m OHLC ambiguity was not hiding a profitable reversal; for several cases it was hiding adverse continuation.
2. **CSI1000:** there is a small, very-short-horizon lead after robust residual re-entry, most visible with a symmetric 10 bps first-passage diagnostic. The structural magnitude is sub-bp before any costs and is strongly dependent on time of day.
3. Therefore the current research object is **not yet a strategy**. It is a thin lead that must survive clock/year/side stability and friction tests before it deserves economic interpretation.
4. Trend research remains out of scope. The reversal side should first expose its own failure boundary; only then should that boundary be compared with the independent trend research.

The most important methodological change since v0.1 is that the question has moved from:

> “Which reversal entry rule wins?”

into:

> “Does a causal displacement/re-entry event contain a repeatable, monetizable path asymmetry before adverse continuation?”

That narrower question has produced more information than adding increasingly elaborate entry filters.

---

## 1. Research loop and governance

All iterations below use only supplied consumed history. `2025` remains unopened for this research line. No result below is fresh OOS.

The research loop is intentionally one-mechanism-at-a-time:

1. run a simple baseline;
2. preserve the failure;
3. change one mechanism suggested by the failure;
4. keep the full surface rather than only the winner;
5. do not import a trend gate to hide losing reversal cases.

Primary measurement began on 5m bars. When 5m OHLC could not order target/stop touches, the same frozen 5m signal was projected onto supplied 1m bars. The 1m projection is a **path-resolution tool**, not a new 1m strategy search.

---

## 2. Iteration map

| Version | Single question changed | Main result | Research consequence |
|---|---|---|---|
| v0.1 | Do naked stretch fade / failed-break reversal work? | Both broadly negative on STAR50 and CSI1000 | Do not protect the baseline; understand how it loses |
| v0.2 | Is there favorable excursion before terminal loss? | Many events show positive MFE but fixed exits give it back | Exit/path may matter more than a stronger entry threshold |
| v0.3 | Does one-bar confirmation rescue entry? | No; results remain negative/near zero | Simple confirmation is not the missing mechanism |
| v0.4 | Does extreme -> re-entry improve MR? | CSI1000 briefly positive at 5–10m; STAR50 negative | Re-entry is more interesting than naked fade, but effect is short-lived |
| v0.5 | Is re-entry robust to a rolling robust residual anchor? | Mostly near-zero/negative; long horizons deteriorate | Preserve robust re-entry as a diagnostic signal, not a winning policy |
| v0.6 | Does deeper extremeness strengthen MR monotonically? | Only very short horizons show partial monotonicity; 15–120m do not | “More extreme = better fade” rejected as a general rule |
| v0.7 | Does subtracting the common cross-index move reveal relative MR? | Mean return still negative at every tested horizon | Common-market removal is not sufficient |
| v0.8 | Is transient MFE monetizable via first-passage target/stop? | STAR no edge; CSI slight clean 10bps advantage, but 5m ordering ambiguous | Intrabar ordering becomes the central uncertainty |
| v0.9 | What happens when the same 5m signal is resolved with 1m paths? | STAR anti-edge confirmed; CSI 10bps keeps a small 5–30m target-first asymmetry | The CSI lead is real enough to localize, but still sub-bp and fragile |
| v0.10 | Is the CSI 10bps lead uniform through the trading day? | No; strong clock dependence, with repeated positive and negative half-hours | Next test is stability of the clock surface, not a clock-filter winner |

---

## 3. v0.1 — naked baselines fail

### MR0 — stretch-only mean reversion

Mean gross next-bar-open event returns, bps:

| Symbol | 30m | 60m | 120m |
|---|---:|---:|---:|
| STAR50 | -3.81 | -5.77 | -10.46 |
| CSI1000 | -3.65 | -4.57 | -7.46 |

### REV0 — directional leg plus failed continuation

| Symbol | 30m | 60m | 120m |
|---|---:|---:|---:|
| STAR50 | -4.80 | -8.31 | -16.40 |
| CSI1000 | -2.64 | -4.52 | -8.74 |

Interpretation: a large displacement or failed breakout is not enough evidence to fade. The loss gets worse with horizon, which is consistent with many “reversal” entries actually being continuation episodes.

---

## 4. v0.2 — favorable excursion exists, but fixed holding gives it back

The path diagnostic exposed a useful distinction between **terminal return** and **best favorable excursion available only with hindsight**.

MR0 terminal means remained negative across 5/10/15/30/60/120m:

- STAR50: approximately `-0.70, -1.39, -2.06, -3.81, -5.77, -10.46` bps.
- CSI1000: approximately `-1.07, -1.80, -2.37, -3.65, -4.57, -7.46` bps.

Yet median MFE grows substantially with horizon.

This does **not** prove a tradable exit. It only generated the next falsifiable question: does a causal target get reached before a symmetric adverse barrier often enough to monetize the excursion?

---

## 5. v0.3–v0.6 — common intuitive repairs do not solve the problem

### One-bar confirmation

A one-bar confirmation layer does not materially rescue the reversal family. CSI1000 produces only tiny near-zero short-horizon pockets before reverting to negative results.

### Re-entry

Requiring price to leave an extreme state and re-enter the normal band is a materially better idea than fading the first extreme print. CSI1000 briefly reaches about `+0.52 bps` at 5m and `+0.19 bps` at 10m in the initial re-entry formulation, while STAR50 remains negative.

### Robust residual re-entry

After switching to a robust residual state, even the short-horizon result weakens:

- STAR50 means at 5/10/15/30/60/120m: approximately `-0.15, -0.60, -1.44, -0.31, -2.25, -4.86` bps.
- CSI1000: approximately `-0.20, -0.75, -1.38, -0.68, -1.63, -7.18` bps.

### Severity surface

Thresholds 2.0 / 2.5 / 3.0 do not show a stable “deeper extreme -> stronger reversal” relation. Only STAR50 5m and CSI1000 5–10m show partial monotonic improvement. The relation fails at longer horizons and often reverses.

Research conclusion: **raising the extremeness threshold is not the solution.**

---

## 6. v0.7 — relative-value MR also fails as a broad solution

A cross-index relative re-entry construction was tested to remove common market motion. Mean returns, bps:

| Horizon | Mean bps |
|---:|---:|
| 5m | -0.280 |
| 10m | -0.117 |
| 15m | -0.637 |
| 30m | -1.038 |
| 60m | -1.487 |
| 120m | -3.763 |

Some 10–30m medians are slightly positive, but the means remain negative and deterioration resumes with horizon.

Research conclusion: **common-market removal is not sufficient to manufacture mean reversion.**

---

## 7. v0.8 — first-passage reframes the exit problem

The v0.5 robust re-entry signal was frozen. No new entry family was searched.

Entry: next 5m bar open.  
Barriers: symmetric ±5 bps and ±10 bps.  
Caps: 30m / 60m.  
If both barriers occur in one 5m OHLC bar, ordering is explicitly `ambiguous_same_bar`.

### STAR50

No first-passage advantage appears. Clean target-first share is approximately 48% for both 5bps and 10bps barriers. Treating ambiguous bars conservatively makes it worse.

### CSI1000

The 10bps surface is marginally more interesting:

- 30m clean target-first share ≈ 50.75%;
- 60m clean target-first share ≈ 51.00%.

But roughly 4–5% of observations remain order-ambiguous at 5m, and target/stop median resolution is just one 5m bar.

This means the 5m experiment cannot tell whether the apparent advantage occurs before or after the adverse move inside the first bar.

---

## 8. v0.9 — 1m path resolution preserves entry and removes most ambiguity

The **same completed-5m signal** was projected onto the 1m timeline. Entry remains next minute open, and an explicit audit confirmed the projected 1m entry matches the next 5m open exactly in all audited finite cases:

- STAR50 exact-match rate: 100%; max point difference: 0.
- CSI1000 exact-match rate: 100%; max point difference: 0.

Therefore this is a cleaner path observation, not an entry-timing change.

### STAR50

The 1m path confirms an anti-edge:

- 5bps clean target-first share stays around 47.7–48.0%;
- 10bps clean target-first share stays around 47.4–47.6%.

The subset that had been ambiguous on 5m is particularly adverse at 10bps: by 30m, target-first is about 39.2% versus stop-first about 57.3%.

### CSI1000

5bps is essentially noise:

- clean target-first ≈ 50.13% at 5m;
- ≈ 50.22% at 10m;
- ≈ 49.51% at 30m.

10bps keeps a small asymmetry:

| Cap | Target first | Stop first | Neither | Clean target share |
|---:|---:|---:|---:|---:|
| 5m | 32.43% | 29.35% | 38.17% | 52.49% |
| 10m | 43.07% | 40.86% | 16.03% | 51.32% |
| 30m | 50.13% | 48.20% | 1.63% | 50.98% |

A rough symmetric-barrier hit imbalance is only about:

- +0.31 bps at 5m;
- +0.22 bps at 10m;
- +0.19 bps at 30m.

This is **before** assigning returns to time-outs, spread, fees, impact or mapping the index diagnostic to a real tradable vehicle.

Research conclusion: the CSI1000 result is a **thin structural lead, not alpha**.

---

## 9. v0.10 — the thin CSI1000 lead is clock-dependent

The v0.9 configuration was frozen:

- 5m robust re-entry signal;
- 1m path resolution;
- symmetric 10bps barrier;
- 5/10/30m caps.

The continuous auction was partitioned into all eight half-hour blocks. This is a result-driven failure-localization analysis and **must not be treated as independent validation**.

### STAR50

The clock surface does not rescue STAR50. Most blocks are below 50% clean target share. There are small isolated late-day pockets, but they are not persistent across caps and should not be promoted into a rule.

### CSI1000

Selected descriptive values are shown below only to summarize the complete clock table; no winner is being chosen.

#### 5m cap, clean target-first share

| Block | Share | Events | Barrier-hit imbalance |
|---|---:|---:|---:|
| 09:30–10:00 | 55.16% | 339 | +0.855 bps |
| 10:00–10:30 | 50.49% | 436 | +0.069 bps |
| 10:30–11:00 | 48.13% | 361 | -0.222 bps |
| 11:00–11:30 | 56.72% | 263 | +0.684 bps |
| 13:00–13:30 | 50.00% | 162 | 0.000 bps |
| 13:30–14:00 | 54.95% | 200 | +0.550 bps |
| 14:00–14:30 | 53.21% | 206 | +0.340 bps |
| 14:30–15:00 | 53.52% | 142 | +0.352 bps |

At 10m and 30m, 09:30–10:00 and 11:00–11:30 remain positive, while 10:30–11:00 remains negative. 13:00–13:30 becomes negative at 10/30m. Other afternoon blocks are mixed.

This is exactly the kind of pattern that can become a dangerous backtest story if the best clock windows are simply selected after inspection.

Research conclusion: **clock structure is now a hypothesis generator, not a trading filter.**

---

## 10. Literature bridge — what the supplied papers justify, and what they do not

The private literature pack is not uploaded to this public repository. The following points are used only to guide hypothesis discipline.

### Intraday Chinese reversal is clock-dependent in prior literature

The Chinese intraday study by Chu, Gu and Zhou divides the day into half-hour intervals and reports materially different continuation/reversal relations across intervals. That makes a full clock stability audit scientifically reasonable.

It does **not** prove our CSI1000 robust-reentry signal should work in the same intervals: the assets, predictor and outcome definitions differ.

### Exit/holding definition can change candlestick/reversal conclusions

Lu, Chen and Hsu emphasize that profitability conclusions for candlestick patterns can depend materially on the holding/exit specification. That is consistent with the empirical distinction uncovered here between favorable excursion and terminal return.

It does **not** license choosing the best exit ex post.

### Short reversal may be conditional liquidity compensation

Nagel and related liquidity/reversal work motivate the idea that short-term reversal may be compensation for absorbing liquidity demand and can be state-dependent. Chiang, Kirby and Nie further distinguish news-driven continuation from liquidity-demand reversal.

Our index package lacks signed order flow, depth and contemporaneous news. Therefore the current data cannot identify a liquidity shock or an information shock causally. Any such explanation remains a hypothesis, not a label.

### Multiple-testing discipline matters here

Because v0.10 exposes eight clock blocks across several caps, a clock winner selected now would be a classic post-selection problem. The next step must report stability of the **entire predeclared clock surface**, rather than optimize clock boundaries.

---

## 11. Current failure surface

### STAR50

Current evidence says:

- naked fade loses;
- failed-break reversal loses;
- confirmation does not rescue it;
- robust re-entry does not rescue it;
- more extreme residuals do not create a stable edge;
- 1m path resolution confirms target is generally reached less often than stop;
- clock slicing produces isolated pockets but no stable general rescue.

Until a new mechanism is justified by evidence, STAR50 reversal/MR should be regarded as **negative evidence**, not a strategy waiting for another threshold tweak.

### CSI1000

Current evidence says:

- naked fade loses;
- re-entry is materially better than first-touch fade;
- any advantage is confined to very short horizons;
- 5bps barriers show essentially no first-passage edge;
- 10bps barriers show a small target-first asymmetry;
- the magnitude is sub-bp before frictions;
- the asymmetry is strongly dependent on intraday clock.

The current candidate phenomenon is therefore:

> **a narrow, very-short-horizon, clock-dependent CSI1000 re-entry effect with gross structural magnitude too small to call tradable before further stability and cost tests.**

---

## 12. Next experiment — v0.11 year × clock × side stability

Do **not** add a clock filter yet.

Freeze:

- CSI1000 and STAR50 both reported;
- the existing 5m robust-reentry signal;
- 1m path resolution;
- 10bps symmetric barrier;
- the same eight half-hour clock bins;
- 5/10/30m caps;
- 2025 unopened.

Then report the complete matrix by:

- calendar year / partial 2020 common sample;
- clock block;
- LONG vs SHORT reversal side;
- event count;
- target-first / stop-first / ambiguous / neither;
- clean target share;
- symmetric barrier-hit imbalance;
- median time to target/stop.

The goal is **not** to require an arbitrary “4 of 5 years” pass rule after seeing the data. The goal is to establish whether the apparent H1/H4 CSI1000 strength and H3/H5 weakness are broad phenomena or merely sample composition.

Only if the clock pattern is reasonably persistent across years and reversal sides should a later iteration preregister a clock-mask candidate and test an actual exit policy plus conservative friction stress.

If the clock pattern collapses by year/side, stop specializing the clock and return to the failure atlas rather than adding more sub-bins.

---

## 13. What is explicitly **not** concluded

Nothing through v0.10 establishes:

- a profitable mean-reversion strategy;
- a production-ready reversal strategy;
- fresh OOS evidence;
- a tradable sub-bp index edge after costs;
- a causal liquidity mechanism;
- a final Trend-vs-Reversion gate;
- a reason to import or optimize a trend-following policy in this repository.

The value of the first ten iterations is that the research problem is now much narrower than at v0.1. That is progress even though the broad strategy hypothesis has not passed.
