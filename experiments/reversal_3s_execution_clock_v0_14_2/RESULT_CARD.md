# RESULT CARD — 3s Execution-Clock Bridge v0.14.2

Date: 2026-09-07  
Status: **cash-index trigger clocks successfully narrowed; no 1m/3s directional conflict; executable IM BBO/basis data still required**  
Run: `34108358649`  
Head: `8abfb6ee9f2030660e7564ccda2ce72baf07c546`  
Artifact: `reversal-3s-execution-clock-v0-14-2`  
Artifact ID: `10013338247`  
Artifact digest: `sha256:a38ef7d0dfd0b0abc63b801281fb2c94a2196220797cd46364a62d7eff7cc177`

## 1. Research role

v0.14.2 does **not** change the v0.13 reversal signal and does **not** replace the frozen 1m barrier/timeout policy.

Frozen event definition remains:

- CSI1000 `000852.SH`;
- negative overnight gap;
- `09:30 <= signal time < 10:00` Asia/Shanghai;
- LONG robust residual re-entry threshold `2.0` on a completed 5m bar;
- 10 bps symmetric target/stop;
- 10 trading-minute primary cap;
- v0.14.1 execution constraint: first qualifying event per trading day only.

The only purpose of this stage is to ask:

> Can the supplied CSI1000 `3s` point-price observations narrow the cash-index trigger clocks enough that an external IM executable replay needs only small BBO windows rather than full-year tick history?

The 3s source is a **point observation stream**, not OHLC. The implementation never invents unobserved intrainterval high/low values.

## 2. 3s source audit

The supplied 2025 CSI1000 3s source contains fields including:

- `observation_datetime` / `market_time_shanghai`;
- point `price`;
- `amount`;
- `session_phase`;
- `row_index`;
- `timestamp_mode = source_exact_3s`;
- source archive identity.

A January preflight found:

- 33,233 rows over 7 sampled trading days;
- no duplicate observation timestamps;
- median 20 observations per observed trading minute;
- typical sequence at exactly 3-second wall-clock intervals during continuous auction.

This is adequate for **observed point crossing timestamps**, but not for reconstructing an unobserved continuous path between samples.

## 3. 1m / 3s wall-clock audit

The full 2025 alignment test gives:

| Audit | Comparisons | Exact | Exact rate | Median abs diff | Max abs diff |
|---|---:|---:|---:|---:|---:|
| 1m `open` vs 3s point at `1m label - 1 minute` | 57,591 | 57,349 | **99.58%** | **0.00 pt** | 21.00 pt |
| 1m `close` vs 3s point exactly at `1m label` | 57,348 | 1,019 | **1.78%** | **0.16 pt** | 7.46 pt |

This reveals an important data-contract distinction:

- the 1m bars are effectively end-labelled for entry-clock purposes; their open usually maps exactly to the 3s point one minute earlier;
- the 1m close is **not** simply identical to the exact 3s snapshot at the bar label.

Therefore v0.14.2 does **not** promote the 3s stream to timeout/close authority. Frozen 1m OHLC remains the scientific outcome authority; 3s is used only when a supplied point explicitly observes a barrier crossing.

## 4. Frozen 2025 first-event/day results

v0.14.1 reduced the 37 raw 2025 candidate events to **35 first-event-per-day executable-architecture events**.

For those 35 events:

- exact frozen entry price available on the 3s stream: **35 / 35 = 100%**;
- same target/stop outcome observed on 3s points: **34**;
- frozen 1m timeout with no 3s barrier crossing: **1**;
- 1m barrier extreme not observed on supplied 3s points: **0**;
- directionally discordant 1m vs 3s outcome: **0**.

Grid relation:

| Relation | Events |
|---|---:|
| same 1m outcome observed by 3s point stream | **34** |
| timeout consistent / no 3s cross | **1** |
| 1m barrier touch absent from 3s observations | **0** |
| directionally discordant | **0** |

This is a strong execution-clock consistency result. It does **not** increase the v0.13 alpha estimate; it reduces timing uncertainty for the future IM quote replay.

## 5. IM quote-window reduction

The generated `im_quote_request_manifest.csv` now requests only:

### Entry

For each event, around the frozen physical entry time:

- from `entry time - 3 seconds`;
- through `entry time + 6 seconds`;
- action: `BUY_CLOSE_PRIOR_DAY_IM_SHORT`.

### Exit

For 34 observed barrier crossings:

- only `3s trigger time ± 6 seconds`;
- action: `SELL_OPEN_RESTORE_IM_SHORT`.

For the one timeout:

- `frozen 10-minute timeout clock ± 6 seconds`.

No event requires a fallback full 1m exit window because every 1m barrier outcome was actually observed by the supplied 3s stream.

Example request windows from the generated manifest:

- `2025-01-02`: entry around `09:40:00`, exit around `09:42:33`, stop-first;
- `2025-01-13`: entry around `09:50:00`, exit around `09:50:12`, target-first;
- `2025-03-11`: entry around `09:40:00`, exit around `09:40:30`, target-first.

The artifact contains the full 35-row manifest; do not reconstruct event timestamps manually from this prose.

## 6. What the 3s result does not prove

The supplied 3s series is still the **cash index**, not IM futures.

It contains no:

- IM bid/ask;
- executable queue depth;
- contract-specific last trades;
- futures/cash basis;
- open interest for causal contract selection;
- broker/exchange realized fee ledger.

Therefore the cash-index gross mean remains the previously frozen v0.14.1 first-event/day diagnostic, approximately **+1.290 bps/event** in 2025. v0.14.2 does not re-price that mean from 3s points.

## 7. External data requirement after v0.14.2

The external IM request can now be much smaller and more authoritative.

For every event day, request:

### Prior trading day

For all active IM contracts:

- contract code;
- expiry / last trading day;
- daily volume;
- daily open interest;
- settlement price.

These fields implement the already frozen causal contract-selection rule in `docs/research/V0_15_IM_HEDGE_RELEASE_REPLAY_PROTOCOL.md`.

### Event day

For the selected IM contract, retrieve Level-1 BBO or stronger data only around the generated 35 entry/exit windows:

- exchange timestamp;
- best bid / ask and sizes;
- last price;
- trade/cumulative volume if available;
- contract code.

Preferred source is official CFFEX historical data or an equivalently authoritative licensed feed. CFFEX's own historical-data service publishes Level-1, Level-2, 1-minute and 5-minute historical databases for listed contracts.

## 8. Decision

v0.14.2 **passes as an execution-clock bridge**:

- it preserves all 35 frozen first-event/day events;
- 34 barrier outcomes are directionally reproduced by actual 3s point crossings;
- the remaining event is a consistent timeout;
- no directional conflict appears;
- all exit quote requests can be narrowed to seconds rather than minutes.

The next empirical step is no longer another reversal-signal experiment.

It is the already preregistered **v0.15 executable IM hedge-release replay** using real contract selection, ask-entry, bid-exit, basis and effective-dated friction.

Until that data is supplied, the correct status remains:

> **confirmed cash-index phenomenon + plausible but cost-fragile hedge-release architecture; executable profitability unknown.**

No trend strategy or Trend-vs-Reversion gate is required at this stage.
