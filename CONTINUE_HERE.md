# 从这里接管

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 当前状态

本仓是 Layer 2 趋势状态识别组件，不是交易策略。**M0–M6 PASS**；当前唯一下一步是 **M7 Stable Consumer API + Snapshot Lifecycle**。

接管必读：`docs/ROADMAP.md`、`docs/API_CONTRACT.md`、`docs/governance/TREND_M5_CLOSEOUT_V1.json`、`docs/governance/TREND_M6_REPRESENTATION_DECISION_V1.json`。

## M5 结论

在 admitted 1m/5m exact views 上：CSI1000 primary `T2=4`、CSI1000 `T2=3/5` sensitivity、STAR50 independent replication 均一致反驳原 extreme-slope exhaustion H1。Extreme absolute slope 表现为更高 persistence、更低 reversal，因此可作为 strength/persistence descriptor 候选。

限制不变：15m/60m 与 phase profiles `NOT_ADMITTED_NOT_EXECUTED`；2025 Holdout 从未打开；M5 outcome 不得重开；`fresh_oos=false`。

## M6 正式产品表示

机器 authority：`docs/governance/TREND_M6_REPRESENTATION_DECISION_V1.json`。

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

schema：`trend_regime_three_bucket_plus_continuous_strength@1.0`。

正式 state 只有三桶。`STRONG_UP / STRONG_DOWN`、five-bucket state 与 T2 都不进入 V1 stable API。M4/M5 的 T2=3/4/5 只保留为 research artifacts。

选择连续 strength 的核心理由：T2=3/4/5 都得到同一 qualitative persistence 关系，所以证据支持连续 extremeness，而没有识别 uniquely privileged cutoff；同时 15m/60m/phase profiles 尚未获得同等级实证认证。

## M7 唯一任务

实现并测试：

- `query_regime(symbol, as_of, bar_interval, profile_id)`；
- immutable snapshot / stable snapshot ID；
- publication + expiry / latest-expired no fallback；
- provider/profile fail-closed admission；
- snapshot fields：`state / directional_score / strength / representation_schema_id / state_scheme_id / strength_definition_id`；
- stable API 禁止 T2、STRONG_*、five-bucket state；
- multi-interval 无 `global_state`；
- `production_authority=false`。

M7 不得重跑 M5、读取 Holdout、调整 T2 或改变 M6 representation。M7 完成后才进入 M8。
