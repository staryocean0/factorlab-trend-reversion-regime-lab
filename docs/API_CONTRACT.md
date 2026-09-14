# 趋势状态识别组件 API 合同（M1–M6 冻结，M7 待实现）

> 状态：**consumer 边界、M2 三桶数学、M3 interval/profile 语义、M6 正式表示均已冻结；M7 只负责 consumer/snapshot lifecycle 实现，不再讨论 state representation。**
>
> 本文不授予 production authority。`production_authority=false`、`fresh_oos=false`。

## 1. 组件职责

本组件是 Layer 2 趋势状态识别组件。它回答：

> 对指定 `symbol + as_of + bar_interval/profile`，当前是否存在已知且仍有效的趋势状态；若存在，方向状态、连续方向分数与强度是什么，来自哪个测量与时间坐标？

它不回答买卖、仓位、订单、策略路由或应该选择哪个交易工具。

## 2. 与 measurement plane 的关系

`src/factor_lab/market_state/timing_layer2_measurement_plane.py` 仍是 Layer 2 measurement authority root；trend consumer 只能安全读取并包装 measurement，不建立平行 Layer 2。

权责固定：

- measurement = true
- strategy selection = false
- parameter selection = false
- routing = false
- trading action = false
- production = false

稳定输出不得带 `position`、`action`、`selected_*`、`tool_owner`、`responsible_tool` 等策略字段。

## 3. V1 逻辑调用面

M7 consumer 的调用面冻结为：

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
- 当该 interval 有多个可执行 Layer-1 views 时显式选择 `profile_id`

### 3.2 Component-owned semantics

调用者不得通过 stable API 自由传入：

- lookback/window
- estimator / price transform
- `T1`
- **任何 `T2` / strong-state threshold**
- normalization / quantile gate
- bar-completion/session/cadence 规则
- source/provider priority
- state scheme
- publication / validity 规则

这些由 versioned component/profile 持有。M6 已明确：V1 stable API **没有正式 T2**。

## 4. M2 三桶 measurement

`trend_regime_three_bucket_baseline@1.0`：

- 最近 20 根 completed + available bars
- `log(close)`
- `log_close_ols_slope_t@1.0`
- `T1=2.0`
- `DOWN: slope_t < -2`
- `SIDEWAYS: -2 <= slope_t <= 2`
- `UP: slope_t > 2`

坏值/少历史均 fail closed；future/unpublished bar 不可影响更早 `as_of`。

## 5. M6 正式产品表示

机器 authority：`docs/governance/TREND_M6_REPRESENTATION_DECISION_V1.json`。

正式 representation schema：

`trend_regime_three_bucket_plus_continuous_strength@1.0`

正式输出由三个核心量组成：

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

语义：

- `state` 表示方向类别；
- `directional_score` 保留 signed trend geometry；
- `strength` 表示 non-negative absolute trend geometry magnitude；
- `directional_score` 不是 iid t-test 显著性；
- `strength` 不是收益预测概率，也不是交易 conviction。

### 5.1 V1 禁止的正式状态

以下**不是 V1 product state**：

- `STRONG_UP`
- `STRONG_DOWN`
- 任意 five-bucket state enum

M4/M5 的五桶/T2=3/4/5 只保留为 research artifacts。M7 stable consumer 不得返回 `strong_state`、`five_bucket_state`、`T2` 等字段。

### 5.2 为什么选择连续 strength

M5 在 CSI1000 primary、T2=3/5 sensitivity、STAR50 replication 上都表明：absolute slope extremeness 与更高 persistence / 更低 reversal 稳定相关；但 `T2=3/4/5` 都给出同一方向证据，因此没有识别出一个有独特产品意义的 cutoff。M6 因此保留连续信息，而不把研究阈值升级成正式五桶。

## 6. M3 interval/profile 语义

M3 engineering registry 仍包含：

- `1m`：1 个 profile
- `5m`：5 个 offset profiles
- `15m`：2 个 offset profiles
- `60m`：2 个 offset profiles

规则不变：

- 当前 `1m` 唯一 view 可省略 `profile_id`；
- 多 view interval 不得暗选相位；
- profile/interval 不匹配直接拒绝；
- FactorLab 不在本层 local-resample；
- M3 profiles 保持 `20 bars + T1=2.0`。

注意：**engineering profile registry 不等于当前 provider/source admission。** M5 当前 active exact source 只对两 carrier 的 1m official / 5m offset0 完成实证准入；15m/60m 与 phase profiles 仍未获得 M5 persistence certification。M7 provider acceptance 必须继续 fail closed。

## 7. `regime_state_consumer_v1` 最小 envelope

```json
{
  "schema": "regime_state_consumer_v1",
  "symbol": "000852.SH",
  "as_of": "2026-09-14T10:15:00+08:00",
  "bar_interval": "5m",
  "profile": "trend_5m_offset0_v1",
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
- `representation_schema_id = trend_regime_three_bucket_plus_continuous_strength@1.0`
- `state_scheme_id = trend_regime_three_bucket@1.0`
- `strength_definition_id = absolute_log_close_ols_slope_t@1.0`
- `state = DOWN | SIDEWAYS | UP`
- `directional_score = slope_t`
- `strength = abs(directional_score)`
- source/provider identity
- measurement-only authority

M7 才实现 snapshot store/index 与正式 `valid_until`/expiry 行为；M2/M3/M6 primitives 不能被误称为 consumer 已完成。

## 8. Availability / fail-closed

`status` 只允许：

- `AVAILABLE`
- `UNAVAILABLE`

不可用不能伪装成 `SIDEWAYS` 或其他状态。

V1 至少保留以下 reason families：

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

state 与 `directional_score` 若不满足 frozen M2 T1 boundary，也属于 invalid measurement，必须 fail closed，不能静默重分类。

## 9. As-of / causality

正式 snapshot 只有在：

```text
published_at <= as_of < valid_until
```

且全部输入在 `decision_time` 已经可知时，才能返回 `AVAILABLE`。

M2/M3 前缀规则：

```text
bar_end <= as_of
available_at <= as_of
```

未来/尚未发布 row 不可见；visible wrong-view row 属于 provider/profile mismatch。

## 10. Latest-expired no fallback

若 `as_of` 前最新 snapshot 已过期：

```text
status = UNAVAILABLE
reason = LATEST_SNAPSHOT_EXPIRED
snapshot = null
```

禁止回退更老 snapshot。

## 11. Snapshot immutability / versioning

- 已发布 snapshot 必须有稳定 identity；
- 同 identity 内容不得改写；
- estimator、T1、representation schema、profile/view 改变都必须新版本；
- query 返回只读/副本语义；
- M7 应采用 append-only 或等价不可变存储。

M6 V1 不允许通过修改 `T2` 来“升级”成五桶。未来如正式引入五桶，必须新建 representation schema/version 并重新做结果前证据流程。

## 12. 多周期语义

同一 `as_of` 可以同时存在不同 interval 的不同 `state / directional_score / strength`。

M3/M6 都不定义顶层 `global_state`。多周期投票、权重、综合趋势与交易解释属于策略层。

## 13. Provider admission

capability registry 中出现 asset/source ref 不等于当前可执行。正式 provider 至少满足：

1. implementation/artifact 可解析；
2. source identity / receipt 可验证；
3. clocks 可映射到因果 measurement coordinate；
4. profile/view 明确接纳；
5. provider acceptance 通过。

不满足必须 fail closed。

## 14. 后续边界

- **M6 已 PASS**：正式表示冻结为“三桶 + 连续 strength”；
- **M7 唯一下一步**：实现本文 consumer、snapshot lifecycle、provider acceptance 与 conformance tests；
- M7 不得重新打开 M5 outcome、重新调 T2、读取 Holdout或改变 M6 representation；
- M8 才做上层调用集成；M9 做版本/发布治理。
