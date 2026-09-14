# 从这里接管

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 当前状态

本仓是 Layer 2 趋势状态识别组件，不是交易策略。**M0–M7 PASS**。当前唯一下一步：**M8 — 策略层调用集成验证**。

接管必读：`docs/ROADMAP.md`、`docs/API_CONTRACT.md`、`docs/governance/TREND_M6_REPRESENTATION_DECISION_V1.json`、`docs/governance/TREND_M7_CONSUMER_CONTRACT_V1.json`。

## 当前正式表示

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

V1 stable API 不包含 T2、`STRONG_UP/STRONG_DOWN`、five-bucket state 或 `global_state`。

## M7 已完成

正式入口：

```text
query_regime(symbol, as_of, bar_interval, profile_id=None)
```

已实现 `regime_state_consumer_v1` + `trend_regime_snapshot@1.0`：immutable identity、append-only ingest、publication/receipt causality、as-of visibility、expiry、latest-expired/unavailable no-fallback、source/provider receipt identity 与 fail-closed admission。

当前 V1 provider registry 固定为 DataHub exact source，两指数只接纳 `trend_1m_official_v1` / `trend_5m_offset0_v1`。15m/60m 与其他 phase profiles 在当前 runtime registry 下 `STATE_NOT_ADMITTED`。Registry 不能由 caller/constructor 自行扩权。

`source_receipt_id` 必须非空；`valid_until` 属于 component/provider publication layer，不是 query caller knob。

## 仍然禁止

- 重跑 M5 outcome 或读取 2025 Holdout；
- 修改 M6 representation；
- 修改 M7 snapshot identity / expiry-no-fallback / current provider admission；
- 在组件内输出 BUY/SELL/position/order/strategy routing；
- 声称 15m/60m 已获得与 1m/5m 相同的 empirical certification；
- 把工程完成解释成 `production_authority=true` 或 `fresh_oos=true`。

## M8 唯一任务

选择至少两个真实上层 caller 做集成/conformance 验证：它们只能读取 M7 snapshot，并在策略层自行决定多周期组合、风险状态组合和动作映射。M8 应证明调用边界稳定，而不是修改趋势组件语义。

M8 完成前不进入 M9。
