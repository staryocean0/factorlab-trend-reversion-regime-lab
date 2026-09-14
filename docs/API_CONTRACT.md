# 趋势状态识别组件 API 合同（M1–M7 已冻结）

> 状态：**M7 stable consumer 已实现并通过 conformance tests。** 本文定义当前 V1 调用面、snapshot lifecycle 与 fail-closed provider admission。
>
> `production_authority=false`、`fresh_oos=false`。组件不输出买卖、仓位、订单、策略路由或多周期总趋势。

## 1. 正式调用面

```text
query_regime(
    symbol,
    as_of,
    bar_interval,
    profile_id = optional_when_unambiguous,
) -> RegimeQueryResult
```

Caller 只拥有：`symbol`、timezone-aware `as_of`、`bar_interval`，以及需要时的 `profile_id`。

Caller 不得传入：lookback、estimator、T1/T2、normalization、provider admission、publication/validity policy、strategy action。

## 2. 正式产品表示

Machine authority：`docs/governance/TREND_M6_REPRESENTATION_DECISION_V1.json`。

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

representation schema：`trend_regime_three_bucket_plus_continuous_strength@1.0`。

稳定 API 禁止 `STRONG_UP/STRONG_DOWN`、five-bucket state、T2 与 `global_state`。M4/M5 五桶只属于历史研究证据。

## 3. Consumer / Snapshot schema

Consumer schema：`regime_state_consumer_v1`。
Snapshot schema：`trend_regime_snapshot@1.0`。

AVAILABLE snapshot 至少包含：

- `snapshot_id`
- `symbol / bar_interval / profile_id / layer1_view_id`
- `decision_time / observation_time / measurement_available_at`
- `published_at / valid_until`
- `state / directional_score / strength`
- `representation_schema_id / state_scheme_id / strength_definition_id`
- `provider_id / source_dataset_id / admission_receipt_id / source_receipt_id`
- measurement schema/estimator identity
- `production_authority=false`

Unavailable 查询返回 `snapshot=null`，不得把不可用伪装成 SIDEWAYS 或泄露旧 state/score/strength。

## 4. Snapshot lifecycle

M7 runtime 已实现：

- snapshot immutable；
- ingest append-only；
- identical duplicate 幂等；conflicting duplicate 拒绝；
- `received_at < published_at` 拒绝；
- receipt 全局倒序拒绝；同 symbol/profile source decision-time 倒序拒绝；
- as-of 只看 `consumer_received_at <= as_of` 的记录；
- `as_of >= valid_until` 时最新 snapshot 过期；
- **latest-expired no fallback**；
- 最新 explicit unavailable 同样 no fallback。

`valid_until` 是 component/provider publication layer 拥有的因果坐标，不是 query caller 参数。Consumer 强制 validity window，但不自行猜测 Layer-1 交易日完整性。

## 5. 当前 provider admission

当前 V1 registry 冻结为：

- provider: `datahub`
- source dataset: `factorlab_unified_index_kline_v3_20260824`
- symbols: `000688.SH`, `000852.SH`
- profiles: `trend_1m_official_v1`, `trend_5m_offset0_v1`
- admission receipt: `trend_m5_source_profile_admission_v1_20260914`

M3 engineering registry 中其他 profiles 仍可作为工程定义存在，但在当前 runtime provider admission 下必须返回 `STATE_NOT_ADMITTED`。不得由 caller 或 constructor 自行扩张 V1 registry；以后扩张必须有新的 source admission / versioned governance。

## 6. Fail-closed reason families

包括但不限于：

- `NO_PUBLISHED_SNAPSHOT`
- `LATEST_SNAPSHOT_EXPIRED`
- `UNSUPPORTED_SYMBOL`
- `UNSUPPORTED_PROFILE`
- `STATE_NOT_ADMITTED`
- `INSUFFICIENT_HISTORY`
- `SOURCE_UNAVAILABLE`
- `OUTSIDE_SUPPORTED_TIME`
- `MEASUREMENT_INVALID`
- `CADENCE_GAP`
- `OFF_PROFILE_GRID`

## 7. Immutability / identity

`snapshot_id` 由 provider/source、symbol、interval/profile/view 与 decision time 的稳定坐标确定。同 identity 内容不能改写；修改 estimator、T1、representation、profile/view 或 provider/source admission 必须通过新的版本/身份表达，而不是覆盖历史 snapshot。

`source_receipt_id` 必须是非空字符串，不能被隐式字符串化为伪 receipt。

## 8. 多周期与策略边界

同一 as-of 可以存在不同 interval 的独立 snapshot。Layer 2 不产生 `global_state`。多周期投票、风险状态组合、策略选择和 BUY/SELL/仓位映射属于 M8 及更上层，不属于本组件。

## 9. Governance

M7 machine contract：`docs/governance/TREND_M7_CONSUMER_CONTRACT_V1.json`。

M7 不重开 M5 outcome，不读取 2025 Holdout，不改变 M6 representation。**唯一下一步是 M8 策略层调用集成验证。**
