# 趋势状态识别组件：当前研究与工程白皮书

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](REPOSITORY_STATE.json) · [最新研究解释](research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

> 本白皮书定义产品定位与当前研究证据。完成 M5/M6 不自动授予 production authority，也不产生 fresh OOS 结论。

## 1. 产品定位

本仓核心交付是 **Layer 2 趋势状态识别组件**。它描述指定 `symbol + as_of + bar_interval/profile` 下的趋势方向和强度，不承担上层策略语义。

## 2. 里程碑状态

- M0–M4：PASS；
- M5：PASS，empirical evidence closed；
- **M6：PASS，representation frozen**；
- **M7：唯一下一步，stable consumer implementation**。

## 3. M5 最终证据

M4 原始 H1 认为 extreme absolute slope 可能更易耗竭。M5 在 admitted 1m/5m exact views 上稳定得到相反结果：

- CSI1000 primary `T2=4`：4/4 executable primary contrasts H1_CONTRADICTED；
- CSI1000 predeclared `T2=3/5` sensitivity：8/8 executable contrasts H1_CONTRADICTED；
- STAR50 independent `T2=4` replication：4/4 contrasts clear qualitative replication。

因此 absolute slope extremeness 对当前 evidence scope 是有支持的 **persistence/strength descriptor 候选**。但 5-bar direction-adjusted return 没有与 persistence/reversal 同等级的稳定证据，所以不能把 strength 直接解释为收益规则。

M5 scope：empirical certification 当前只覆盖 1m/5m、CSI1000/STAR50；15m/60m 与 phase profiles `NOT_ADMITTED_NOT_EXECUTED`；2025 Holdout 从未打开；`fresh_oos=false`。

## 4. M6 Representation Decision

Machine authority：`docs/governance/TREND_M6_REPRESENTATION_DECISION_V1.json`。

M6 选择：**THREE_BUCKET_PLUS_CONTINUOUS_STRENGTH**。

正式 V1 representation：

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

schema：`trend_regime_three_bucket_plus_continuous_strength@1.0`。

### 4.1 state

`state` 继续完全继承 M2：

- DOWN: `slope_t < -2`
- SIDEWAYS: `-2 <= slope_t <= 2`
- UP: `slope_t > 2`

M6 不改变 20-bar lookback、log-close OLS estimator 或 `T1=2.0`。

### 4.2 directional score / strength

`directional_score` 精确等于 M2 `slope_t`，保留符号；`strength` 等于其绝对值。M6 不做 quantile normalization、unit-interval scaling 或新的拟合。

`strength` 表达趋势几何强度，不是收益概率、置信概率或独立误差假设下的统计显著性。

## 5. 为什么 V1 不采用正式五桶

M5 的关键事实是 `T2=3/4/5` 全部得到同一 qualitative persistence 关系。这说明 evidence 支持连续 slope extremeness，而没有识别一个具有独特产品意义的 cutoff。

同时：

- 15m/60m 和 phase profiles 尚无同等级 evidence；
- return evidence 没有 persistence/reversal 那么稳定；
- 固定五桶会损失连续信息并把 research threshold 升级为 product semantics。

因此 V1 formal state enum **不包含 `STRONG_UP / STRONG_DOWN`**。M4/M5 five-bucket assets 继续保留用于 research audit，但 M7 stable consumer 不返回 five-bucket/strong-state 字段，也不接受 caller T2。

以后如要正式引入五桶，必须创建新的 representation schema/version，并重新进行结果前 evidence 流程；不能静默修改 M6 V1。

## 6. M6 evidence certification 边界

M6 representation 的数学定义可以包装冻结 M2/M3 measurement，但 persistence/strength 的 empirical certification 当前只覆盖 admitted 1m/5m 与两个 carrier。15m/60m 和 phase profiles 不得被描述为已经获得相同实证认证。

`production_authority=false`、`fresh_oos=false` 保持不变。

## 7. M7 唯一下一步

M7 实现：

- `query_regime(symbol, as_of, bar_interval, profile_id)`；
- immutable snapshot + stable identity；
- publication/expiry + latest-expired no fallback；
- provider/profile fail-closed admission；
- M6 fields：`state / directional_score / strength / representation_schema_id / state_scheme_id / strength_definition_id`；
- stable API 禁止 T2、STRONG_*、five-bucket state；
- multi-interval 无 `global_state`。

M7 不重开 M5 outcome，不改变 M6 representation。M8 才做上层集成，M9 做 release/version governance。
