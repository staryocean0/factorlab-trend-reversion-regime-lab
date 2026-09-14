# Trend Regime V1 API Examples

> 这些示例展示 **Layer 2 状态读取**，不是交易策略示例。示例不会把 `UP/DOWN/strength` 映射为买卖、仓位、订单或策略路由。

## 1. 基本查询

```python
from factor_lab.market_state.trend_regime_consumer import TrendRegimeConsumer

consumer = TrendRegimeConsumer()

result = consumer.query_regime(
    symbol="000852.SH",
    as_of="2026-09-14T10:00:30+08:00",
    bar_interval="1m",
)
```

调用者只提供 `symbol / as_of / bar_interval`，以及 interval 存在多 phase 时所需的 `profile_id`。Caller 不提供 lookback、estimator、T1/T2、provider admission、validity policy 或交易动作。

## 2. 5m exact admitted profile

```python
result = consumer.query_regime(
    symbol="000852.SH",
    as_of="2026-09-14T10:05:30+08:00",
    bar_interval="5m",
    profile_id="trend_5m_offset0_v1",
)
```

当前 V1 runtime admission 只有：

- `trend_1m_official_v1`
- `trend_5m_offset0_v1`

这不是“默认选择任意 5m phase”。调用者必须使用已准入 profile；组件不会静默替换 phase。

## 3. AVAILABLE 结果

AVAILABLE query 的 `snapshot` 含正式产品表示：

```python
payload = result.to_dict()

state = payload["snapshot"]["state"]
directional_score = payload["snapshot"]["directional_score"]
strength = payload["snapshot"]["strength"]
```

稳定关系：

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

即使 `directional_score` 的绝对值很大，V1 也不会返回 `STRONG_UP/STRONG_DOWN` 或 T2-based state。

## 4. UNAVAILABLE 必须显式处理

```python
payload = result.to_dict()

if payload["status"] == "UNAVAILABLE":
    reason = payload["reason"]
    # state is unavailable; do not replace it with SIDEWAYS.
```

重要语义：

- latest expired => `LATEST_SNAPSHOT_EXPIRED`
- unadmitted profile => `STATE_NOT_ADMITTED`
- 没有已发布 snapshot => `NO_PUBLISHED_SNAPSHOT`
- unavailable query 的 `snapshot` 为 `None`
- latest expired / latest unavailable 不回退旧 snapshot

## 5. 15m/60m 当前 fail closed

```python
result = consumer.query_regime(
    symbol="000852.SH",
    as_of="2026-09-14T10:15:30+08:00",
    bar_interval="15m",
    profile_id="trend_15m_offset5_v1",
)

assert result.reason == "STATE_NOT_ADMITTED"
```

M3 中存在 15m/60m engineering profile，不等于这些 profile 已进入 V1 runtime admission。未来若扩张，必须先有新的 exact source admission receipt 与版本化治理。

## 6. 多周期保持独立

```python
one_minute = consumer.query_regime(
    "000852.SH",
    "2026-09-14T10:05:30+08:00",
    "1m",
)

five_minute = consumer.query_regime(
    "000852.SH",
    "2026-09-14T10:05:30+08:00",
    "5m",
    "trend_5m_offset0_v1",
)
```

`1m` 和 `5m` 可以同时给出不同方向。Layer 2 不投票、不加权、不生成 `global_state`。多周期组合属于 Layer3/更上层。

## 7. 与 risk state 并行上送

推荐上层保持 namespace 分离：

```python
strategy_inputs = {
    "trend_by_interval": {
        "1m": one_minute.to_dict(),
        "5m": five_minute.to_dict(),
    },
    "risk": risk_state_payload,
}
```

这里仍然没有：

```text
fused_state
selected_strategy
action
position
order
route
```

Trend 与 risk 如何组合，属于上层所有权，不属于本组件。

## 8. 稳定调用者应依赖什么

V1 caller 可以依赖：

- `query_regime(symbol, as_of, bar_interval, profile_id=None)`
- `status / reason / snapshot`
- `state / directional_score / strength`
- snapshot identity、publication/receipt causality 与 expiry/no-fallback
- source/provider/admission identities

V1 caller 不应依赖：

- M4/M5 five-bucket research artifacts
- 内部 estimator/window 实现细节作为 caller knob
- 15m/60m 当前一定可用
- Layer2 自动产生交易动作或全局趋势
- `production_authority=true`

完整发布/兼容规则见 `TREND_V1_RELEASE.md` 与 `TREND_M9_RELEASE_GOVERNANCE_V1.json`。
