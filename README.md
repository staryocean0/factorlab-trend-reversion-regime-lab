# FactorLab 趋势反转与均值回归研究

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 新产品定位

未来工程收敛为**可被策略调用的趋势状态识别组件**，不是独立交易策略，也不直接输出买卖、仓位或 Layer 4 指令。

M0 产品定位、M1 consumer 合同、M2 三桶基线、M3 多 K 线级别参数化和 **M4 五桶实验协议冻结**均已完成。路线图唯一下一阶段是 **M5 极端斜率持续性实证**，若继续推进只能按 M4 冻结协议执行。

M2 冻结 `trend_regime_three_bucket_baseline@1.0`：20 根 completed/available K 线、log-close OLS signed slope t-score、`T1=2.0`。M3 把它绑定到 `1m/5m/15m/60m` 共 10 个 DataHub Layer-1 V3 profiles。M4 在任何五桶 outcome 被计算前冻结：primary `T2=4.0`、`T2=3/5` sensitivity、载体/日期切分、anchor profiles、horizons、episode 单位、primary/secondary endpoints、样本门槛、week-cluster bootstrap、Holm 多重检验、holdout unlock 与负结果规则。

M4 没有计算 forward return、transition/reversal probability、五桶 episode 数或 MFE/MAE，因此没有新增五桶市场证据。

## 入口

[当前状态与下一步边界](CONTINUE_HERE.md) · [当前组件白皮书](docs/WHITEPAPER.md) · [执行路线图](docs/ROADMAP.md) · [M1 API 合同](docs/API_CONTRACT.md) · [Gap 审计](docs/API_GAP_ANALYSIS.md) · [M2 三桶基线](docs/THREE_BUCKET_BASELINE.md) · [M4 冻结协议](docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.md) · [M4 机器合同](docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json) · [组件索引](docs/COMPONENTS.md) · [测试与工作流](docs/TESTING.md) · [数据用途说明](docs/DATA.md)

当前没有已确认交易策略，也没有由状态源登记的 active empirical candidate。M5 是路线图下一里程碑；若后续获得执行授权，必须遵循冻结协议，不能根据结果调整 primary 定义。工程基线、数据修正和审计可复现，但复现通过不增加市场证据，也不改变 `production_authority=false`。

## 本地环境

```bash
bash .codex/cloud_setup.sh
```

默认只安装依赖并检查组件一致性，不自动回放历史拟合。完整回归需要已检出测试依赖数据，见测试说明。源码包版本0.1.0是包装版本，不是策略成熟度。
