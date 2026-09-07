# RESULT CARD — Execution Architecture Cost Floor v0.14.1

Date: 2026-09-07  
Status: **standalone IM rejected; ETF marketable inventory overlay economically fragile; prior-day IM short hedge-release remains the only live execution architecture pending real IM quotes/basis**  
Run: `34106997455`  
Head: `6574be68bce61c6c7f498a20338e99bdec66b695`  
Artifact: `reversal-execution-overlay-v0-14-1`  
Artifact ID: `10012776244`  
Artifact digest: `sha256:02838a42282a006b7d9fac9ed0657cc7cd198da0764339988067118944d8ab7f`

## 1. Research role

This stage does **not** modify the v0.13 predictive signal.

Frozen phenomenon:

- CSI1000 `000852.SH`;
- negative overnight gap;
- 09:30–10:00 Asia/Shanghai;
- LONG robust residual re-entry threshold `2.0` observed on a completed 5m bar;
- next-1m-open diagnostic entry;
- symmetric `+10 / -10 bps` barriers;
- 10 trading-minute cap.

v0.13 found `+1.515 bps/event` on 37 project-local 2025 historical-confirmation events, but executable-vehicle economics were unresolved.

v0.14.1 asks a narrower question:

> **Which account architecture, if any, can avoid structurally consuming more friction than the thin cash-index effect before we even obtain real IM quotes?**

No trend strategy or Trend-vs-Reversion gate is introduced.

## 2. Why this stage uses at most one event per day

CFFEX close-today recognition is economically important here. Public explanations of the CFFEX rule describe closing volume as matched against **same-day newly opened positions before historical positions** when computing the close-today fee.

Therefore:

- `old long + buy more + later sell` does **not** cleanly avoid close-today cost; the sell can close the newly opened long first;
- `old short + buy-close historical short + later sell-open short` is different: the first leg closes a prior-day position and the second leg creates a new short, so there is no same-day newly opened position being closed on that first cycle;
- after that new short is created, a **second** buy-close later the same day would first close the same-day new short and can again incur close-today cost.

Hence the clean hedge-release architecture executes **only the first qualifying signal per trading day**.

This is an execution/accounting constraint discovered after v0.13 confirmation, not a new preregistered alpha filter. Its 2025 result is therefore an execution-feasibility diagnostic, not a second confirmation test.

Reference used for CFFEX close-today sequencing explanation:

- https://www.bocifco.com/newsinfo.aspx?cid=0&id=16408

## 3. First-signal-per-day cash-index diagnostic

| Role | Raw events | First/day events | Target | Stop | Timeout | Gross mean |
|---|---:|---:|---:|---:|---:|---:|
| 2020H2–2024 development context | 162 | 150 | 86 | 59 | 5 | **+1.985 bps** |
| 2025 historical confirmation context | 37 | 35 | 19 | 15 | 1 | **+1.290 bps** |

The execution constraint removes 12 development events and 2 confirmation events. The sign remains positive, but the 2025 economic hurdle falls from `1.515` to **`1.290 bps/event`**.

## 4. Architecture A — standalone IM long/flat

Implementation:

`flat -> buy-open IM -> same-day sell-close IM`

The CFFEX public fee table lists for CSI1000 index futures:

- ordinary transaction fee: notional × `0.23 / 10,000` = `0.23 bps`;
- close-today fee: notional × `2.3 / 10,000` = `2.30 bps`.

Exchange trade-fee floor for the standalone round trip:

`0.23 + 2.30 = 2.53 bps`.

Official source:

- https://www.cffex.com.cn/cn/zjssf/20240701/39212.html

Result before bid/ask, broker commission, slippage or basis:

| Role | Gross mean | CFFEX trade-fee floor | Residual |
|---|---:|---:|---:|
| Development context | +1.985 | -2.530 | **-0.545 bps** |
| 2025 confirmation context | +1.290 | -2.530 | **-1.240 bps** |

**Decision: reject the naïve standalone IM intraday implementation.**

It is negative before any market microstructure friction is charged.

## 5. Architecture B — prior-day IM short hedge release

Required account state before the day begins:

> sufficient **prior-day IM short hedge inventory** already exists in the selected contract.

Frozen event action:

1. first qualifying LONG reversal signal of the day -> **buy-close one historical short**;
2. frozen cash-index exit trigger -> **sell-open one short** to restore the hedge.

Both legs are ordinary transactions under this architecture, so the exchange trade-fee floor is approximately:

`0.23 + 0.23 = 0.46 bps`.

Before spread, basis, broker fee and slippage:

| Role | Gross mean | Ordinary CFFEX fees | Residual |
|---|---:|---:|---:|
| Development context | +1.985 | -0.460 | **+1.525 bps** |
| 2025 confirmation context | +1.290 | -0.460 | **+0.830 bps** |

The public CFFEX table also lists a stock-index-futures order/申报 fee. Using two `RMB 1` order fees and using the cash-index level only as an explicit proxy for IM notional gives a median order-fee proxy of about `0.016 bps` in 2025.

IM minimum tick is `0.2` index point and multiplier is `RMB 200/point`. Using the cash-index level only as a clearly labelled proxy, one minimum tick is about `0.313 bps` in the 2025 sample.

After ordinary exchange fees + **one tick** + two order-fee proxies:

- development residual: **+1.204 bps/event**;
- 2025 residual: **+0.501 bps/event**.

This is **not** a net backtest. It still excludes:

- real IM bid/ask at entry and exit;
- marketable-order slippage;
- cash-index/IM basis change during the holding interval;
- causal contract selection and roll state;
- broker markup/commission;
- queue/fill uncertainty.

**Decision: retain only as an executable-architecture candidate. Real IM quote/basis replay is mandatory before any economic claim.**

Official IM contract source:

- https://www.cffex.com.cn/zz1000/

## 6. Architecture C — stock-ETF inventory overlay

A stock ETF cannot be modeled as a zero-inventory T+0 round trip. The SSE states that domestic stock ETFs are T+1. Existing T-day-opening holdings may be sold on T day, while T-day newly purchased shares become sellable on T+1.

An inventory overlay could therefore be modeled only if prior-day sellable ETF inventory already exists:

`buy new ETF exposure -> later sell an equal amount from prior-day sellable inventory`.

This leaves the account with the newly bought shares replacing the shares sold from old inventory, so it is an inventory transformation rather than an independent flat-to-flat trade.

SSE competitive-trading handling fee is `0.004%` per side, or approximately `0.8 bps` round trip before broker commission.

After that exchange handling fee, the 2025 first-event/day residual is only **+0.490 bps/event**.

SSE ETF price tick is `RMB 0.001`. For a one-tick marketable spread alone to fit inside `0.490 bps`, the ETF unit price would need to exceed approximately **RMB 20.43** before broker commission. Typical CSI1000 stock-ETF prices are far below that scale, so one tick itself is generally several basis points.

SSE sources:

- ETF T+1 / trading FAQ: https://www.sse.com.cn/assortment/fund/etf/question/c/c_20240118_5734755.shtml
- fee schedule: https://www.sse.com.cn/lawandrules/sselawsrules2025/charge/c/c_20250610_10781461.shtml

**Decision: do not prioritize a marketable stock-ETF inventory implementation for this thin edge.** Passive execution would create a different fill-selection problem and must not be assumed free.

## 7. Current frontier

After v0.14.1 the research object is no longer a generic standalone reversal trade.

The only execution architecture still worth testing is:

> **A pre-existing CSI1000 IM short hedge is temporarily reduced on the first frozen opening-gap LONG re-entry event of the day, then restored at the frozen cash-index exit trigger.**

Economically, this is a **hedge-release / exposure-timing overlay**, not a new outright-long strategy.

This distinction matters because the counterfactual PnL is:

`PnL(temporarily less hedged) - PnL(keep hedge unchanged)`

rather than an isolated long-futures trade PnL.

## 8. Data blocker and next experiment

The repository and linked File Library currently contain no point-in-time 2025 IM minute/tick/BBO history. Therefore the true vehicle replay cannot yet be executed.

Before requesting a large external data package, the repository already contains CSI1000 `3s` observations through 2025. The next step is **v0.14.2**, an execution-clock bridge:

1. keep the v0.13 5m signal unchanged;
2. keep the first-event/day execution constraint unchanged;
3. keep entry at the frozen next-1m-open price/time;
4. use supplied CSI1000 3s observations only to resolve the first cash-index target/stop timestamp inside the 10-minute cap;
5. same-3s-bin target+stop ambiguity remains adverse;
6. compare 3s and 1m outcome classifications for grid sensitivity;
7. emit a narrow quote-request manifest containing only the actual IM entry/exit time windows needed for executable replay.

If 3s materially changes the frozen 1m outcomes, execution confidence falls. If it does not, the required external IM data can be reduced to prior-day contract-selection fields plus narrow BBO/tick windows around approximately 35 event entry/exit timestamps.

No new predictive threshold or trend filter is allowed in v0.14.2.
