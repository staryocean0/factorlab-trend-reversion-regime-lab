# 趋势状态识别组件 API 合同（M1，已吸收 M2/M3 决议）

> 状态：**M1 consumer 边界已冻结；M2/M3 已补全三桶数学与 interval/profile 语义；正式 consumer facade 仍属于 M7。**
>
> 本文不授予 production authority，也不提前冻结 M4–M6 的五桶研究结论。

## 1. 组件职责

本组件是 Layer 2 的趋势状态识别 consumer。它回答：

> 对指定 `symbol + as_of + bar_interval/profile`，当前是否存在已知且仍有效的趋势状态；若存在，状态/强度是什么，来自哪个测量与时间坐标？

它不回答买卖、仓位、订单、策略路由或应该选择哪个交易工具。

## 2. 与 measurement plane 的关系

`src/factor_lab/market_state/timing_layer2_measurement_plane.py` 负责 measurement authority、来源坐标和 capability；trend consumer 负责安全读取某个 `as_of` 时刻可见的状态。

权责固定：

- measurement = true
- strategy selection = false
- parameter selection = false
- routing = false
- production = false

稳定输出不得带 `position`、`action`、`selected_*`、`tool_owner`、`responsible_tool` 等策略字段。

## 3. V1 逻辑调用面

M7 最终 consumer 的逻辑调用面按 M1 + M3 冻结为：

```text
query_regime(
    symbol,
    as_of,
    bar_interval,
    profile_id = optional_when_unambiguous,
) -> RegimeQueryResult
```

### 3.1 Caller-owned selection

调用者拥有：

- `symbol`
- timezone-aware `as_of`
- `bar_interval`
- 当该 interval 有多个 admitted Layer-1 views 时，显式选择 `profile_id`

### 3.2 Component-owned semantics

调用者不得通过稳定 consumer API 自由传入：

- lookback/window
- slope/estimator 实现
- price transform / normalization
- `T1/T2`
- bar-completion / session / cadence 规则
- source/provider priority
- state scheme
- publication / validity 规则

这些都必须由 versioned component/profile 持有。

## 4. M2 已冻结的三桶 measurement

`trend_regime_three_bucket_baseline@1.0`：

- 最近 20 根 completed + available bars
- `log(close)`
- `log_close_ols_slope_t@1.0`
- `T1=2.0`
- `DOWN: s < -2`
- `SIDEWAYS: -2 <= s <= 2`
- `UP: s > 2`

坏值/少历史均 fail closed；future/unpublished bar 不可影响更早 `as_of`。

## 5. M3 已冻结的 interval/profile 语义

首批 engineering admission：

- `1m`：1 个 profile
- `5m`：5 个 offset profiles
- `15m`：2 个 offset profiles
- `60m`：2 个 offset profiles

合计 10 个 profiles，全部绑定 DataHub Layer-1 V3 immutable wall-clock views。

规则：

- 当前 `1m` 只有唯一 view，可省略 `profile_id`；
- `5m/15m/60m` 存在多个 admitted views，必须显式给 `profile_id`；
- 组件不得暗选相位；
- profile 与 interval 不匹配直接拒绝；
- FactorLab 不在本层 local-resample K 线；
- 所有首批 profiles 继续使用 M2 的 `20 bars + T1=2.0`，M3 不按周期调参。

## 6. `regime_state_consumer_v1` 最小 envelope

```json
{
  "schema": "regime_state_consumer_v1",
  "symbol": "000852.SH",
  "as_of": "2026-09-14T10:15:00+08:00",
  "bar_interval": "15m",
  "profile": "trend_15m_offset5_v1",
  "status": "AVAILABLE | UNAVAILABLE",
  "reason": "<reason-code>",
  "snapshot": null,
  "production_authority": false
}
```

`AVAILABLE` 时，snapshot 至少包含：

- `snapshot_id`
- `symbol`
- `bar_interval`
- `profile`
- `decision_time`
- `observation_time`
- `published_at`
- `valid_until`
- `state_scheme_version`
- `state`
- measurement raw/normalized/strength fields
- source/provider identity
- measurement-only authority

M7 才实现 snapshot store/index 与正式 `valid_until`/expiry 行为；M2/M3 measurement wrapper 不能被误称为 M7 consumer 已完成。

## 7. Availability / fail-closed

`status` 只允许：

- `AVAILABLE`
- `UNAVAILABLE`

不可用不能伪装成 `SIDEWAYS` 或其他市场状态。

V1 至少保留/吸收以下 reason families：

- `NO_PUBLISHED_SNAPSHOT`
- `LATEST_SNAPSHOT_EXPIRED`
- `INSUFFICIENT_HISTORY`
- `SOURCE_UNAVAILABLE`
- `UNSUPPORTED_SYMBOL`
- `UNSUPPORTED_PROFILE`
- `OUTSIDE_SUPPORTED_TIME`
- `MEASUREMENT_INVALID`
- `STATE_NOT_ADMITTED`
- `CADENCE_GAP`
- `OFF_PROFILE_GRID`

M3 additionally requires visible rows to match profile `view_id` and immutable close-time grid；cadence 缺口不插值、不回填、不 resample。

## 8. As-of / causality

正式 snapshot 只有在：

```text
published_at <= as_of < valid_until
```

且全部输入在 `decision_time` 已经可知时，才能返回 `AVAILABLE`。

M2/M3 measurement 前缀规则已经冻结：

```text
bar_end <= as_of
available_at <= as_of
```

未来或尚未发布的 row 对较早 `as_of` 不可见。未来 wrong-view row 也不能污染当前状态；当前 visible wrong-view row 则属于 provider/profile mismatch。

## 9. Latest-expired no fallback

若 `as_of` 前最新 snapshot 已经过期：

```text
status = UNAVAILABLE
reason = LATEST_SNAPSHOT_EXPIRED
snapshot = null
```

禁止为了“给一个值”而回退更老 snapshot。

## 10. Snapshot immutability / versioning

- 已发布 snapshot 必须有稳定 identity；
- 同 identity 内容不得改写；
- estimator、阈值、state scheme、profile/view 改变都必须产生新版本；
- query 返回只读/副本语义；
- M7 应采用 append-only 或等价不可变存储。

## 11. 多周期语义

同一 `as_of` 可以同时存在：

```text
1m = DOWN
5m = SIDEWAYS
15m = UP
60m = UP
```

M3 的 multi-interval measurement 顶层故意没有 `state/global_state`。多周期投票、权重和交易解释都属于策略层，不能污染 Layer 2。

## 12. Provider admission

capability registry 中出现某个 asset/source ref 不等于它当前可执行。正式 provider 至少应满足：

1. implementation/artifact 可解析；
2. source identity / receipt 可验证；
3. clocks 可映射到因果 measurement coordinate；
4. profile/view 明确接纳；
5. provider acceptance 通过。

不满足时必须 fail closed。

## 13. 后续边界

- **M4**：只冻结五桶实验协议；
- **M5**：按预注册协议做极端斜率实证；
- **M6**：裁决三桶/五桶/连续强度架构；
- **M7**：实现本文 consumer、snapshot lifecycle 与 conformance tests。

在 M6 之前，`STRONG_UP/STRONG_DOWN` 不具有正式产品状态语义；在 M7 之前，M2/M3 measurement wrapper 不具有正式 consumer/production authority。
