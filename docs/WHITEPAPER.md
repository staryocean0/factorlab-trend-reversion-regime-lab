# 趋势状态识别组件：当前研究与工程白皮书

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](REPOSITORY_STATE.json) · [最新研究解释](research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

> 本白皮书定义产品定位与当前证据。工程里程碑完成不自动授予 production authority，也不产生 fresh OOS 结论。

## 1. 产品定位

本仓交付的是 **Layer 2 趋势状态识别组件**。它描述指定 `symbol + as_of + bar_interval/profile` 下的趋势方向和连续强度，不承担买卖、仓位、订单、策略路由或多周期总趋势语义。

## 2. M5/M6 证据与表示

M5 已完整收口：在 admitted 1m/5m exact views 上，CSI1000 primary、预注册 T2 sensitivity 与 STAR50 independent replication 都反驳原 extreme-slope exhaustion H1；extreme absolute slope 表现为更高 persistence、更低 reversal。

M6 因此选择**三桶 + 连续 strength**，而不是把任一研究 T2 固化成正式五桶：

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

V1 stable semantics 不包含 `STRONG_UP/STRONG_DOWN`、five-bucket state、T2 或 `global_state`。

## 3. M7 Stable Consumer（PASS）

Machine authority：`docs/governance/TREND_M7_CONSUMER_CONTRACT_V1.json`。

正式 consumer schema：`regime_state_consumer_v1`。
正式 snapshot schema：`trend_regime_snapshot@1.0`。

调用面：

```text
query_regime(symbol, as_of, bar_interval, profile_id=None)
```

M7 已实现：

- deterministic immutable snapshot identity；
- append-only ingest；
- identical duplicate 幂等、conflicting duplicate 拒绝；
- publication/receipt causality；
- as-of 只看当时 consumer 已收到的 snapshot；
- explicit `valid_until` expiry；
- latest expired / latest unavailable 均不回退旧 snapshot；
- unavailable 不泄露 state/score/strength；
- provider/source/admission/source-receipt identity；
- M6 state/score/strength schema identity；
- `production_authority=false`、`trading_action_authority=false`。

## 4. Provider admission 边界

当前 V1 provider registry 固定为 DataHub `factorlab_unified_index_kline_v3_20260824`，两指数只接纳：

- `trend_1m_official_v1`
- `trend_5m_offset0_v1`

M3 其余 engineering profiles 没有被删除，但在当前 runtime source admission 下必须 `STATE_NOT_ADMITTED`。V1 registry 不能由 query caller 或 constructor 自行扩张；未来扩张必须有新的 exact source receipt 和 versioned governance。

`source_receipt_id` 必须是非空字符串。`valid_until` 属于 component/provider publication layer，而不是 query caller 参数。

## 5. 证据范围仍然有限

M5 persistence/strength evidence certification 目前只覆盖 admitted 1m/5m 与 CSI1000/STAR50。15m/60m 和 phase profiles 不得被描述为已获得同等级实证认证。2025 protocol Holdout 从未打开；M5 outcome 不重开；`fresh_oos=false`。

## 6. 唯一下一步：M8

M8 只做上层 caller integration validation：验证不同策略层调用者如何安全读取 M7 snapshot，并由上层自行处理多周期组合、风险状态组合和动作映射。

M8 不改变 M6 representation、M7 lifecycle/provider admission，也不能把 `UP/DOWN/strength` 变成组件内部 BUY/SELL/仓位规则。M9 才处理 release/version/migration governance。
