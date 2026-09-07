# v0.14 Execution Reality Check — Before Any Further Signal Search

Date: 2026-09-07  
Status: execution feasibility screen, not a new signal experiment

## Why this stage exists

v0.13 produced the first preregistered directional historical confirmation in this research line:

- CSI1000;
- negative overnight gap;
- 09:30–10:00;
- LONG robust residual re-entry;
- next-1m-open entry;
- +10 / -10 bps symmetric barriers;
- 10m primary cap;
- 2025 gross mean `+1.515 bps/event` over 37 events.

The confirmation is small-sample and not fresh OOS. More importantly, the `+1.515 bps/event` gross mean is an **economic cost ceiling**: any all-in round-trip friction above that level makes the sample mean non-positive before considering model uncertainty.

Therefore the next research question is not another entry filter. It is whether the candidate has an executable vehicle whose point-in-time frictions can fit inside this narrow hurdle.

---

## 1. Natural derivative vehicle: CSI1000 index futures (IM)

Official CFFEX product / rule pages state that CSI1000 index futures:

- trade under code `IM`;
- use the CSI1000 index as underlying;
- contract multiplier is RMB 200 per index point;
- minimum tick is 0.2 index point;
- continuous trading is 09:30–11:30 and 13:00–15:00;
- are cash-settled;
- rules took effect from 2022-07-22.

Official sources:

- https://www.cffex.com.cn/zz1000/
- https://www.cffex.com.cn/cn/ssxz/20220718/43093.html

Thus IM is timing-compatible with the frozen 09:30–10:00 / 10-minute candidate and is the most direct same-day long/flat mapping to investigate for the 2025 confirmation period.

### Fee red flag

The CFFEX public fee table dated 2024-07 states for equity-index futures (including CSI1000):

- normal transaction fee: transaction value × `0.23 / 10,000`;
- close-today fee: transaction value × `2.3 / 10,000`.

Official source:

- https://www.cffex.com.cn/cn/zjssf/20240701/39212.html

Expressed in notional basis points, a simple standalone trade that **opens today and closes the same position today** would therefore have an exchange-level nominal fee of approximately:

`0.23 bps opening + 2.30 bps close-today = 2.53 bps round trip`.

That already exceeds the v0.13 2025 gross mean hurdle of `1.515 bps/event` by about `1.015 bps/event`, **before**:

- broker commission / markup;
- bid-ask spread;
- slippage;
- futures-vs-cash-index basis;
- contract selection / roll effects;
- signal timestamp and quote latency;
- market impact.

This is an immediate economic warning, not yet a final historical cost backtest. Before applying the fee numerically to 2025, the effective-dated 2025 exchange + broker fee contract should be verified. The public 2024-07 table is sufficient to show that a naive standalone same-day IM round trip is not automatically viable.

---

## 2. Natural cash vehicle: domestic CSI1000 stock ETF

A long-only candidate might appear easier to implement with an ETF. An established example is Southern CSI1000 ETF `512100`, whose SSE product materials show a 2016-11-04 listing date.

However, the Shanghai Stock Exchange explicitly states that domestic **stock ETFs use T+1 trading**, while only selected bond/gold/cross-border/money ETFs support T+0.

Official sources:

- https://www.sse.com.cn/assortment/fund/etf/question/c/c_20240118_5734755.shtml
- https://www.sse.com.cn/disclosure/fund/announcement/c/new/2023-12-15/512100_20231215_0U36.pdf

Therefore a naive implementation:

`09:xx buy stock ETF -> 10 minutes later sell those newly bought shares`

cannot be assumed executable.

A **pre-existing inventory overlay** may be a different implementation problem: if an account already holds sufficient sellable ETF inventory, one could investigate whether a temporary intraday increase in exposure can be offset later using pre-existing sellable shares. That must be treated as a separate account/inventory contract, not silently assumed from index returns.

---

## 3. What v0.14 concludes now

The candidate has passed a useful scientific transition:

1. broad reversal / MR failed;
2. a narrow opening-gap re-entry mechanism survived a frozen 2025 historical confirmation;
3. the first execution screen immediately reveals that the most direct flat-to-long-to-flat IM implementation may have a fee floor larger than the observed gross mean;
4. the obvious cash ETF alternative has T+1 constraints for a standalone same-day round trip.

This is exactly the kind of problem that should be exposed before adding more predictive features.

**Do not tune the signal further until executable-vehicle economics are resolved.**

---

## 4. Minimum next data contract

### Preferred path A — IM futures executable replay

Request point-in-time CSI1000 futures data for at least the 2025 frozen confirmation dates:

- all active IM contracts, not only a retrospectively stitched continuous price;
- 1m OHLC at minimum; bid/ask or tick/quote data strongly preferred;
- volume and open interest;
- contract code and expiry;
- authoritative trading calendar;
- point-in-time fee schedule / broker cost assumptions;
- explicit rule for choosing the trade contract using only information available before the signal (e.g. frozen prior-day liquidity rule, not hindsight best contract).

Required outputs:

- cash-index signal timestamp -> selected IM contract timestamp mapping;
- cash/futures basis at signal and exit;
- executable next quote / next bar open;
- +10/-10 bps equivalent barrier behavior on the futures vehicle;
- time-out fill;
- exchange fees, broker fees, spread and slippage separately;
- net event PnL;
- fraction of cash-index candidate events that remain economically positive.

### Alternative path B — stock ETF inventory overlay

If futures close-today economics are prohibitive, request 2025 point-in-time intraday data for a preregistered CSI1000 stock ETF plus an explicit starting-inventory/sellable-quantity policy.

Do not describe this as a standalone intraday ETF round trip. The account must have sufficient prior-day sellable inventory for the overlay construction.

---

## 5. Stop condition

If an executable, rules-compliant vehicle cannot reduce total realized round-trip friction below the v0.13 gross hurdle with adequate margin, stop treating the confirmed cash-index phenomenon as a standalone trading strategy.

It may still be useful later as:

- an execution-timing signal for an existing CSI1000 exposure;
- an inventory-rebalancing overlay;
- a risk-management / entry-timing input;
- a future contrast point against the independently researched trend strategy.

But those are different economic policies and must be tested as such.
