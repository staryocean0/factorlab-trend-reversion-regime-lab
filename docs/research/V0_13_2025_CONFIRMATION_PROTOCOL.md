# v0.13 Preregistered 2025 Historical Confirmation

Frozen before opening 2025 in this project research line.  
Date: 2026-09-07

## Evidence identity

`2025` is a **project-local historical confirmation segment only**. The supplied data package is consumed historical material, so this is **not fresh OOS** even though v0.1–v0.12 deliberately did not inspect 2025.

No 2026 data is authorized or opened.

## Candidate frozen from v0.12

Primary instrument: CSI1000 `000852.SH`.

Primary event must satisfy all conditions using data available when the completed 5m signal bar closes:

1. current trading-day open is below the prior continuous-auction trading-day close (`overnight_gap_log < 0`);
2. event timestamp is in `09:30 <= time < 10:00` Asia/Shanghai;
3. v0.5 robust residual re-entry signal is `LONG` (`+1`), with the already-frozen threshold `2.0`;
4. no gap-magnitude threshold is added;
5. no clock boundary is changed;
6. no SHORT candidate is promoted.

The signal is still computed on 5m bars. The supplied 1m series is used only for post-signal path / exit resolution.

## Entry

Entry is the **next 1m open** after the completed 5m signal timestamp.

Prior v0.9 audit showed this matches the next 5m open exactly for audited events. v0.13 must repeat the alignment audit for the candidate events.

## Primary exit policy — frozen before 2025

Primary horizon cap: **10 trading minutes**.

Barrier from entry:

- target: `+10 bps`;
- stop: `-10 bps`.

Starting with the first 1m bar after the signal:

- if target is touched and stop is not touched: exit at target, gross event PnL `+10 bps`;
- if stop is touched and target is not touched: exit at stop, gross event PnL `-10 bps`;
- if both are touched inside the same 1m OHLC bar: intrabar order is unknowable, **conservatively score the event as stop-first and gross event PnL `-10 bps`**;
- if neither barrier is touched by the end of the 10th post-signal 1m bar: exit at that bar's close and score actual long return from entry to time-out close.

No slippage, commission, vehicle basis or market impact is assumed in the gross policy result. Instead report the mean gross bps per event as the **maximum break-even all-in round-trip cost hurdle** before the sample mean turns non-positive.

## Frozen robustness caps

Also report the same policy at:

- 5 trading minutes;
- 30 trading minutes.

These are robustness diagnostics only. **10m remains primary regardless of which 2025 number is best.**

## Required 2025 outputs

For primary 10m and robustness 5m/30m:

- event count and trading-day count;
- target-first, stop-first, same-1m-bar ambiguous, time-out counts;
- clean target-first share;
- conservative target share with ambiguous treated as adverse;
- gross policy mean / median bps;
- gross win rate;
- central-90% mean bps;
- break-even all-in round-trip cost hurdle (= gross mean bps/event);
- median minutes to target and stop;
- entry-alignment audit.

Also recompute the **same exact frozen policy** on `2020-07-23`–`2024-12-31` only as labeled development context. Do not refit or alter any parameter from that comparison.

## Interpretation rules

Primary confirmation is the 2025 **10m** result.

Evidence is directionally supportive only if all of the following hold:

1. at least 20 valid 2025 candidate events;
2. clean target-first share > 50%;
3. conservative target share (same-1m-bar ambiguity adverse) > 50%;
4. gross 10m policy mean > 0 bps.

If event count is <20, call the result inconclusive rather than pass/fail.

Even if supportive, do not call it fresh OOS, production-ready or net profitable. The next stage would require executable vehicle mapping and friction analysis.

If 2025 fails, do not reopen threshold/clock/gap filters on 2025. Return to the v0.1–v0.12 failure atlas.

## Prohibited post-confirmation edits

After 2025 is read, do not:

- optimize the robust-z threshold;
- choose a different gap magnitude cutoff;
- move the 09:30/10:00 boundaries;
- switch primary cap away from 10m because 5m or 30m looks better;
- promote a SHORT subgroup;
- select favorable 2025 months;
- introduce a trend strategy to mask losing events.
