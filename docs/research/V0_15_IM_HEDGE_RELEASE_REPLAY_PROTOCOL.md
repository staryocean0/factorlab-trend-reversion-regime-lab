# v0.15 Protocol — Executable IM Hedge-Release Replay

Date: 2026-09-07  
Status: **frozen before any point-in-time IM quote/basis history is opened in this repository**

## Purpose

v0.13 produced a directionally supportive but statistically imprecise cash-index historical confirmation. v0.14.1 then rejected a standalone same-day IM long/flat implementation on exchange-fee grounds and left only one plausible execution architecture:

> a portfolio that already carries a prior-day CSI1000 IM short hedge temporarily buys that old short closed on the first frozen LONG reversal event of the day, then sells the short open again at the frozen cash-index exit trigger.

This protocol defines the executable replay before IM historical quotes are supplied.

This is **not** a new alpha search and it does not change the reversal signal.

## Frozen cash-index event

- carrier: CSI1000 `000852.SH`;
- negative overnight gap;
- signal time `09:30 <= t < 10:00` Asia/Shanghai;
- LONG robust residual re-entry threshold `2.0` on a completed 5m bar;
- cash-index diagnostic entry level remains next-1m-open;
- target `+10 bps`, stop `-10 bps`;
- primary cap `10 trading minutes`;
- first qualifying event per trading day only;
- cash-index 1m policy remains the outcome authority;
- supplied 3s index observations may narrow the trigger timestamp but may not redefine the signal or invent unobserved extrema.

## Account architecture

Before the continuous auction opens on every eligible event day, the account must already hold at least one **prior-day short IM position** in the causally selected contract.

If that inventory condition is not satisfied, the event is **not executable under this architecture** and must fail closed. Do not silently substitute a same-day new short because that changes close-today fee accounting.

The comparison baseline is:

> keep the prior-day IM short hedge unchanged through the event window.

The overlay is:

1. at the frozen entry trigger, buy-close one unit of the historical short;
2. remain one unit less hedged until the frozen cash-index exit trigger;
3. at the exit trigger, sell-open one unit of the same IM contract to restore the hedge.

The reported economic quantity is the **incremental PnL of the overlay relative to keeping the hedge unchanged**, not standalone futures PnL.

## Causal contract-selection rule

The trade contract for event day `D` must be selected using only information available by the end of prior trading day `D-1`.

Eligible set:

- all IM contracts listed and active on event day `D`;
- exclude a contract if `D` is its last trading day, because reopening that contract would not restore an overnight hedge beyond the session.

Ranking:

1. highest prior-day open interest;
2. if tied, highest prior-day volume;
3. if still tied, nearest expiry.

No retrospectively stitched continuous contract, future-day liquidity, realized intraday spread, or hindsight best basis may influence selection.

The account-state assumption must be explicit: by the prior close the baseline hedge program is assumed to hold the selected contract. Any ordinary hedge-program roll/rebalance cost common to both baseline and overlay is outside the incremental event PnL; any cost caused specifically by the overlay must be included.

## Required historical data

### Prior-day contract state

For all active IM contracts on each event's prior trading day:

- contract code;
- expiry / last trading day;
- daily volume;
- daily open interest;
- settlement price.

### Event-window executable quotes

For the selected contract, point-in-time Level-1 BBO or stronger data around the v0.14.2 manifest windows:

- authoritative exchange timestamp;
- best bid price/size;
- best ask price/size;
- last price;
- trade size or cumulative volume where available;
- contract code.

Official CFFEX historical data service explicitly offers Level-1, Level-2 and 1m/5m historical databases. Preferred evidence source is official CFFEX history or an equivalently authoritative licensed feed.

## Execution rule

### Entry

At the frozen cash-index entry time:

- action: `BUY_CLOSE` one prior-day short IM;
- fill: first executable **ask** at or after the trigger time;
- if no valid ask is available inside the requested quote window, mark the event unfilled / data-insufficient; do not backfill from a later bar open without a declared sensitivity run.

### Exit

At the frozen cash-index exit trigger:

- action: `SELL_OPEN` one IM short in the same contract;
- fill: first executable **bid** at or after the trigger time;
- timeout events use the frozen 10-minute timeout clock;
- if no valid bid is available inside the requested window, fail closed.

Base replay does not assume midpoint fills, passive fills, queue priority or price improvement.

## Costs

Charge separately and report separately:

- effective-dated CFFEX ordinary transaction fee on buy-close historical position;
- effective-dated CFFEX ordinary transaction fee on sell-open;
- CFFEX order/申报 fees where applicable;
- broker commission / markup;
- any additional account-specific exchange or clearing cost supplied by the owner;
- spread is embedded by ask-entry / bid-exit execution;
- additional slippage, if modeled, must be shown as a separate sensitivity rather than hidden in the fill price.

The architecture assumes no close-today fee on the first event/day because it closes a historical short and later opens a new short. If actual account/order records show otherwise, the event must be repriced with the realized fee.

## Basis and PnL

Cash-index/IM basis must be recorded at both entry and exit. Do not assume futures move one-for-one with the cash index over the 10-minute window.

For one contract with multiplier `M=RMB 200/point`, the overlay's market PnL relative to maintaining the short hedge is economically equivalent to a temporary long exposure:

`market_pnl = (exit_sell_open_price - entry_buy_close_price) * M`

Then subtract all overlay-specific fees/costs.

Report both RMB and basis points of contract notional at entry.

## Primary outputs

For every frozen event:

- event and prior trading day;
- selected contract and causal selection inputs;
- proof of prior-day short inventory eligibility (or explicit assumed baseline inventory flag for research simulation);
- cash-index signal/entry/exit clocks;
- IM ask entry and bid exit with timestamps;
- entry and exit cash/IM basis;
- spread paid at entry and exit;
- exchange fee, order fee, broker fee, slippage separately;
- gross incremental overlay PnL;
- net incremental overlay PnL;
- failure/data-coverage reason where applicable.

Aggregate:

- eligible events and quote coverage;
- net mean/median bps per event;
- total net RMB per one-contract overlay;
- net win rate;
- gross-to-net edge retention;
- tail losses;
- results by year only for descriptive transport, not winner selection.

## Interpretation

- If net mean is non-positive after rules-compliant executable fills and all known friction, the candidate is **not economically viable as this hedge-release overlay**. Preserve the cash-index phenomenon as a measurement/risk-management finding.
- If net mean remains positive but very small, label it **cost-fragile** rather than stable alpha; do not add filters just to rescue it.
- Only materially positive executable results with adequate quote coverage justify a later capacity/account-level study.

No 2026 market data may be opened in this stage. No trend strategy or Trend-vs-Reversion gate is part of the replay.
