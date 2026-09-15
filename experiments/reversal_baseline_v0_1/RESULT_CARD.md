# RESULT CARD — Reversal / Mean-Reversion Baseline v0.1

Date: 2026-09-07  
Status: **completed negative baseline; retain as falsification evidence**  
GitHub Actions run: `34098004890`  
Runner head: `82a96cab6b6134b25fdf2b797a2469f819bcea40`  
Artifact: `reversal-baseline-v0-1`, artifact id `10009360330`, digest `sha256:4bd1ce96b979a849610a4afd5550b6fe8c611db3dc5f061d412a2f1a223d46f9`

## 1. Question

Do the first deliberately simple reversal / mean-reversion policies show positive gross index-direction behavior before any fine parameter search?

- **MR0**: fade a close more than 2 prior-ATR units from a causal 120-trading-minute prior-close EMA anchor.
- **REV0**: after a 60-minute directional leg with efficiency >= 0.60 and displacement >= 1.50 prior ATR, fade a breakout in the leg direction if the signal bar closes back inside the lagged 60-minute range.

Signal is observed only at completed bar close `t`; diagnostic entry is open `t+1`.

## 2. Evidence identity

- Frequency: 5m primary bars.
- History opened: `2020-07-23` through `2024-12-31` only.
- 2025 was not opened by this baseline runner.
- Both indices have 51,792 bars and 1,079 trading days in the common window.
- Supplied history is consumed development material, not fresh OOS.
- Results are gross index-direction diagnostics, not a directly executable A-share cash strategy.

The actual 5m export loaded by the runner contains standard OHLC/amount/metadata fields but does **not** contain `high_frequency_analysis_eligible`, `causal_flat_fill`, or `source_minute_count`. Therefore the optional strict-quality predicates based on those fields cannot further filter this particular 5m export; all 51,792 rows per index survived the session/available quality mask.

## 3. Execution evidence

Research-branch sealed-seed subset check: **passed**, 111 sealed seed files unchanged.  
Original main snapshot exact-set validator: **passed**, 111 files / 52 data partitions.  
Full pytest: **21 passed in 0.54s**.  
Baseline empirical runner: **passed**.  
Artifact upload: **passed**.

An earlier run failed because the original seed validator intentionally requires the exact initial public-file set and therefore rejects legitimate research extensions. The research workflow was corrected without weakening the sealed snapshot: the branch checks every sealed file hash and scans the full tree for forbidden public payloads, while the untouched original exact-set validator is run against a main worktree.

## 4. Primary all-year results

Mean/median are gross basis points from next-bar-open entry to the fixed future close.

| Strategy | Index | Horizon | Valid events | Mean bps | Median bps | Win rate | Frozen-anchor hit |
|---|---|---:|---:|---:|---:|---:|---:|
| MR0 | STAR50 | 30m | 15,930 | -3.81 | -4.84 | 44.75% | 10.48% |
| MR0 | STAR50 | 60m | 13,881 | -5.77 | -7.57 | 44.47% | 19.34% |
| MR0 | STAR50 | 120m | 10,033 | -10.46 | -13.52 | 43.77% | 30.43% |
| MR0 | CSI1000 | 30m | 19,293 | -3.65 | -4.03 | 44.48% | 10.96% |
| MR0 | CSI1000 | 60m | 16,497 | -4.57 | -5.34 | 45.00% | 21.13% |
| MR0 | CSI1000 | 120m | 11,424 | -7.46 | -10.35 | 43.84% | 33.30% |
| REV0 | STAR50 | 30m | 1,174 | -4.80 | -6.04 | 42.59% | 8.69% |
| REV0 | STAR50 | 60m | 1,030 | -8.31 | -11.12 | 41.75% | 17.09% |
| REV0 | STAR50 | 120m | 675 | -16.40 | -18.51 | 39.41% | 24.74% |
| REV0 | CSI1000 | 30m | 1,066 | -2.64 | -3.22 | 45.22% | 10.60% |
| REV0 | CSI1000 | 60m | 913 | -4.52 | -3.42 | 45.45% | 19.61% |
| REV0 | CSI1000 | 120m | 598 | -8.74 | -8.93 | 43.65% | 30.27% |

**All twelve primary strategy/index/horizon cells are negative.** Losses become more negative as the fixed holding horizon increases.

## 5. Cross-year evidence

MR0 is negative in every calendar-year cell for both indices and all three horizons.

REV0 is negative in every STAR50 calendar-year cell. CSI1000 has a small positive pocket in 2023 (about +0.50 / +2.07 / +0.36 bps at 30/60/120m), but this does not transport across STAR50 or persist reliably into other CSI1000 years. It is therefore not promoted.

This is not a one-crash or one-year failure.

## 6. Direction asymmetry

Both long-reversal and short-reversal sides are negative overall.

Examples at 30m:

- MR0 STAR50: long -2.60 bps, short -5.21 bps.
- MR0 CSI1000: long -2.32 bps, short -4.92 bps.
- REV0 STAR50: long -4.83 bps, short -4.77 bps.
- REV0 CSI1000: long -0.72 bps, short -4.26 bps.

Short-side fades are generally worse, but removing one side would not rescue the overall thesis.

## 7. Event-density / clustering diagnosis

MR0 is far too common to deserve the intuitive label "rare extreme":

- STAR50: about 16.8 signal bars per active day;
- CSI1000: about 20.5 signal bars per active day.

Consecutive same-side 5m MR0 signal clusters average about 4.34 bars in STAR50 and 4.95 bars in CSI1000. The median cluster is 2 bars and 3 bars respectively; the maximum is 24 bars.

This exposes an anchor/scale design problem: 2 x single-bar ATR away from a 120-minute EMA is routinely satisfied during ordinary intraday directional movement.

However event overlap is **not the sole reason for negative returns**. Restricting the 30m diagnostic to the first signal in each consecutive same-side cluster remains negative:

- STAR50 MR0 cluster starts: about -3.80 bps;
- CSI1000 MR0 cluster starts: about -4.10 bps.

REV0 is much less clustered (about 1.11 bars per cluster overall) and is still negative.

## 8. Does failed acceptance rescue MR0?

The already-produced event artifact allows the preregistered MR1 subset to be inspected without changing its signal definition: long MR0 events must also be failed downside breaks; short MR0 events must also be failed upside breaks.

MR1 remains negative:

| Index | 30m | 60m | 120m |
|---|---:|---:|---:|
| STAR50 mean bps | -3.97 | -7.32 | -13.18 |
| CSI1000 mean bps | -2.59 | -2.55 | -4.31 |

Therefore a **single-bar close back inside the prior range is not sufficient reversal confirmation**.

## 9. What v0.1 falsifies

The evidence rejects the following simple forms in this sample/implementation:

1. `large causal-anchor stretch -> fade`;
2. `efficient displaced leg + same-bar failed breakout -> fade`;
3. adding the same single-bar failed-acceptance condition to MR0 as the sole confirmation;
4. assuming a 30–120 minute holding horizon will naturally reveal the reversion.

The failure is especially informative because the negative sign is stable across both indices and generally strengthens with horizon.

This does **not** prove a profitable trend strategy. It only says that these supposed reversal triggers are followed, on average, by further movement against the fade over the measured horizons.

## 10. Main hypotheses generated by the failure

The next iteration should diagnose mechanisms before changing thresholds:

### H1 — horizon mismatch

A reversal may occur briefly over 5–15 minutes and then be overwhelmed by resumed directional movement. Fixed 30/60/120-minute closes cannot distinguish this from "no reversal ever occurred".

### H2 — confirmation timing is too early

A breakout bar closing back inside a lagged range may be a pause/retest, not a completed reversal. A genuine turning point may require persistence of rejection into one or more subsequently closed bars.

### H3 — the MR anchor/scale is mis-specified

Single-bar ATR is a movement scale, not necessarily the right distributional scale for distance from a moving equilibrium. Its use here creates extremely high signal density.

### H4 — exit mechanics matter

A mean-reversion strategy may need to realize transient favorable excursion or anchor contact rather than hold mechanically for 30–120 minutes.

## 11. Next action

Do **not** add a trend filter and do **not** fine-tune the baseline thresholds yet.

Run a v0.2 path diagnostic on the unchanged MR0/MR1/REV0 event definitions:

- 5m / 10m / 15m / 30m / 60m / 120m terminal returns;
- maximum favorable and adverse excursion after next-bar-open entry;
- partial distance-to-frozen-anchor convergence;
- time/order of favorable excursion, anchor contact, and adverse continuation;
- cluster-onset vs repeated-event behavior;
- long/short and year splits.

Only after this path anatomy is known should v0.2 alter the signal or exit mechanism.

## 12. Decision

**v0.1 is rejected as a trading candidate but accepted as useful falsification evidence.**

The project continues because the negative result exposed specific, testable problems in signal confirmation, anchor scaling, and holding/exit design. No Trend-vs-Reversion gate is introduced at this stage.
