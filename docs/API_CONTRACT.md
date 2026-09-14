# 趋势状态识别组件 API 合同（M1–M8 已冻结）

> 状态：**M7 stable consumer 已实现；M8 已验证其上层集成所有权边界。** M8 不改变 M7 的调用面、snapshot lifecycle 或 provider admission。
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

Caller 只拥有 `symbol`、timezone-aware `as_of`、`bar_interval` 以及需要时的 `profile_id`。Caller 不得传入 lookback、estimator、T1/T2、normalization、provider admission、publication/validity policy 或 strategy action。

## 2. 正式产品表示

Machine authority：`docs/governance/TREND_M6_REPRESENTATION_DECISION_V1.json`。

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

representation schema：`trend_regime_three_bucket_plus_continuous_strength@1.0`。稳定 API 禁止 `STRONG_UP/STRONG_DOWN`、five-bucket state、T2 与 `global_state`。

## 3. Consumer / Snapshot schema

Consumer schema：`regime_state_consumer_v1`。Snapshot schema：`trend_regime_snapshot@1.0`。

AVAILABLE snapshot 至少包含 snapshot identity、symbol/interval/profile/view、decision/observation/publication/expiry clocks、`state/directional_score/strength`、representation identities、provider/source/receipt identities、measurement estimator identity，以及 `production_authority=false`。

Unavailable 查询返回 `snapshot=null`，不得把不可用伪装成 SIDEWAYS 或泄露旧 state/score/strength。

## 4. Snapshot lifecycle

M7 runtime 已实现：immutable snapshot、append-only ingest、duplicate identity guard、publication-before-receipt causality、receipt/source ordering、as-of receipt visibility、expiry，以及 **latest-expired / latest-explicit-unavailable no fallback**。

`valid_until` 属于 component/provider publication layer，不是 query caller 参数。Consumer 不自行猜测 Layer1 交易日完整性。

## 5. 当前 provider admission

当前 V1 registry 冻结为：

- provider `datahub`
- dataset `factorlab_unified_index_kline_v3_20260824`
- symbols `000688.SH`, `000852.SH`
- profiles `trend_1m_official_v1`, `trend_5m_offset0_v1`
- admission receipt `trend_m5_source_profile_admission_v1_20260914`

其他 M3 engineering profiles 在当前 runtime 下 fail closed 为 `STATE_NOT_ADMITTED`。不得由 caller/constructor 扩张 V1 registry。

## 6. Fail-closed reason families

包括 `NO_PUBLISHED_SNAPSHOT`、`LATEST_SNAPSHOT_EXPIRED`、`UNSUPPORTED_SYMBOL`、`UNSUPPORTED_PROFILE`、`STATE_NOT_ADMITTED`、`INSUFFICIENT_HISTORY`、`SOURCE_UNAVAILABLE`、`OUTSIDE_SUPPORTED_TIME`、`MEASUREMENT_INVALID`、`CADENCE_GAP`、`OFF_PROFILE_GRID`。

## 7. Immutability / identity

`snapshot_id` 绑定 provider/source、symbol、interval/profile/view 与 decision time。同 identity 内容不得改写。Estimator、T1、representation、profile/view 或 provider/source admission 改变必须新版本；`source_receipt_id` 必须是非空字符串。

## 8. M8 上层集成边界

Machine authority：`docs/governance/TREND_M8_STRATEGY_INTEGRATION_V1.json`。

M8 验证并冻结以下所有权规则：

1. Layer2 trend snapshot 是只读输入；caller 不在 Layer2 adapter 中修改 value/threshold/state semantics。
2. 同一 as-of 的 1m/5m snapshot 可以不同，必须分别上送；Layer2 不创建 `global_state`。
3. trend 与 risk 是并行 Layer2 namespaces；融合、冲突仲裁、选择属于 Layer3 或更高层。
4. `UNAVAILABLE` / expired 不能被 caller 转成 SIDEWAYS 来补值。
5. 任何 BUY/SELL、position/order、strategy/plugin selection、routing 都在 Layer2 之外。
6. M8 不创建 production wiring，也不授权 production。

CSI1000 私仓已有真实 read-only Layer2 adapter 和 Layer3 orchestration kernel，M8 验证与其所有权模型兼容。STAR50 仓已有真实 risk-state consumer，但其示例明确没有 external consumer connected，因此这里只认证为并行 risk-provider boundary，**不声称存在已部署的 STAR50 策略 caller**。

## 9. Governance

M7 machine contract：`docs/governance/TREND_M7_CONSUMER_CONTRACT_V1.json`。
M8 machine contract：`docs/governance/TREND_M8_STRATEGY_INTEGRATION_V1.json`。

M8 不重开 M5、读取 Holdout、改变 M6/M7、修改外部仓或扩大 provider admission。**唯一下一步是 M9 release/version/documentation/governance。**
