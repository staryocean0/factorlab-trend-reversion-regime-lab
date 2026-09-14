# FactorLab 趋势状态识别组件

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 当前产品状态

M0–M6 已完成。M6 正式表示冻结为：

```text
state = DOWN | SIDEWAYS | UP
directional_score = slope_t
strength = abs(directional_score)
```

schema：`trend_regime_three_bucket_plus_continuous_strength@1.0`。

M5 evidence 支持连续 extremeness/strength，但没有识别唯一 T2 cutoff。因此 V1 不采用正式 five-bucket state；M4/M5 的 T2=3/4/5 仅保留为 research artifacts。

当前 empirical support 范围仍是 admitted 1m/5m、CSI1000/STAR50；15m/60m 与 phase profiles 尚未获得同等级认证。`fresh_oos=false`、`production_authority=false`。

唯一下一步：**M7 stable consumer implementation**。

入口：[接管](CONTINUE_HERE.md) · [路线图](docs/ROADMAP.md) · [API 合同](docs/API_CONTRACT.md) · [M6 决策](docs/governance/TREND_M6_REPRESENTATION_DECISION_V1.md)
