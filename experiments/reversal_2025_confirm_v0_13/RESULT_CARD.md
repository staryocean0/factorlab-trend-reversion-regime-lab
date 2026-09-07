# RESULT CARD — Preregistered 2025 Historical Confirmation v0.13

Date: 2026-09-07  
Status: **predeclared directional confirmation passed; statistical precision still weak**  
Run: `34103454999`  
Artifact: `reversal-2025-confirm-v0-13`  
Artifact ID: `10011422019`  
Artifact digest: `sha256:46dadadaf6643fa3d0228cd379d9a33b4ab52160fbd318081ef3195a296caf18`

## Evidence identity

The frozen contract was committed in `docs/research/V0_13_2025_CONFIRMATION_PROTOCOL.md` before this workflow opened the project-local 2025 confirmation segment.

GitHub Actions explicitly checked that the preregistration file was present before empirical execution. `2025` is still consumed historical material, **not fresh OOS**.

No 2026 data was opened.

## Frozen candidate

Primary candidate frozen from v0.12:

- CSI1000 `000852.SH`;
- negative overnight gap;
- `09:30 <= signal time < 10:00` Asia/Shanghai;
- LONG robust residual re-entry, threshold `2.0`;
- signal computed on completed 5m bars;
- entry at next supplied 1m open;
- symmetric target `+10 bps` / stop `-10 bps`;
- **10 trading minutes primary cap**;
- if target and stop touch in the same 1m bar, score the stop;
- if neither is touched by the cap, exit at cap-bar close;
- 5m and 30m are frozen robustness caps, not alternative winners.

No clock, gap-magnitude, threshold, side or horizon was changed after reading 2025.

## Execution audit

- sealed seed validation: passed, 111 files;
- original main seed validation: passed;
- pytest: **48 passed**;
- development candidate signals: 162;
- 2025 candidate signals: **37**;
- 2025 candidate trading days: **35**;
- next-1m-open vs next-5m-open entry exact-match rate: **100%**;
- maximum entry-price difference: **0 points**.

## Primary 2025 result — 10 minute cap

| Metric | 2020H2–2024 development context | 2025 frozen confirmation |
|---|---:|---:|
| Events | 162 | **37** |
| Target first | 92 | **20** |
| Stop first | 64 | **15** |
| Same-1m-bar ambiguous | 0 | **0** |
| Time-out | 6 | **2** |
| Clean target share | 58.97% | **57.14%** |
| Conservative target share | 58.97% | **57.14%** |
| Gross policy mean | +1.918 bps | **+1.515 bps** |
| Gross policy median | +10.0 bps | **+10.0 bps** |
| Gross win rate | 59.88% | **59.46%** |
| Break-even all-in round-trip cost hurdle | 1.918 bps | **1.515 bps** |
| Median minutes to target | 2 | **2** |
| Median minutes to stop | 2 | **2** |

The 2025 mean is about 21% smaller than the development-context mean but remains positive and the sign does not flip.

## Frozen robustness caps

### 5 minute cap — 2025

- 37 events;
- target first 19, stop first 13, time-out 5;
- clean target share 59.38%;
- gross policy mean **+0.995 bps/event**.

### 30 minute cap — 2025

- 37 events;
- target first 21, stop first 16, no time-outs;
- clean target share 56.76%;
- gross policy mean **+1.351 bps/event**.

The primary 10m result is retained regardless of the robustness values.

## Predeclared decision

The preregistration required, for the 2025 primary 10m result:

1. at least 20 events;
2. clean target share > 50%;
3. conservative target share > 50%;
4. gross policy mean > 0 bps.

All four are true.

**Protocol verdict:** `DIRECTIONALLY_SUPPORTIVE_HISTORICAL_CONFIRMATION`.

## Supplemental uncertainty — not a new pass criterion

The confirmation sample remains small.

For the 35 clean target/stop resolutions, `20/35 = 57.14%`. An exact two-sided 95% binomial interval is approximately **39.35%–73.68%**; the one-sided exact test against 50% gives `p ≈ 0.25`.

Across all 37 policy events, gross mean is `+1.515 bps` with sample standard deviation about `9.78 bps`; a simple one-sample t-test against zero gives `p ≈ 0.35`.

These supplemental calculations were performed after the preregistered verdict and are used only to describe precision. They do not alter the frozen pass/fail rule.

Therefore the correct interpretation is:

> The frozen candidate transported directionally into the project-local 2025 confirmation segment, but the confirmation is not statistically precise enough to establish a stable alpha.

## Economic interpretation

The observed 2025 gross mean of `+1.515 bps/event` is also the maximum all-in round-trip friction that the sample mean can absorb before reaching zero **under this idealized index diagnostic**.

That hurdle is thin. The repository has index bars rather than an executable CSI1000 vehicle. No futures/ETF basis, bid-ask spread, commission, slippage, impact, capacity or fill uncertainty has been charged.

Because the candidate is a same-day intraday LONG reversal, direct A-share cash implementation also cannot be assumed from an index signal. Executable-vehicle mapping is now more important than adding another signal filter.

## Decision after v0.13

Do **not** tune the confirmed signal further on 2025.

The next stage should move from signal discovery to **economic realizability**:

1. freeze the candidate unchanged;
2. identify a legally/execution-compatible CSI1000 vehicle and its point-in-time history;
3. reproduce signal timestamps against that vehicle rather than the cash index;
4. model basis, bid-ask, fees/slippage and time-stop fills;
5. compare the resulting all-in round-trip cost with the observed `1.515 bps/event` confirmation hurdle;
6. keep the cash-index result as a measurement-plane finding, not a production backtest.

No trend strategy or Trend-vs-Reversion gate is required for this stage.
