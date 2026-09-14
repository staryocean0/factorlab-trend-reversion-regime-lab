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

M0 产品定位、M1 consumer 合同与 **M2 三桶基线冻结**均已完成。当前唯一下一阶段是 **M3 多 K 线级别参数化**；M3 完成前不进入五桶协议或极端斜率实证。

M2 已冻结 `trend_regime_three_bucket_baseline@1.0`：20 根 completed/available K 线、log-close OLS signed slope t-score、`T1=2.0`，并用因果/缺失回归测试保证 future/unpublished bar 不泄漏。详见 [M2 三桶基线](docs/THREE_BUCKET_BASELINE.md)。

## 入口

[当前状态与下一步边界](CONTINUE_HERE.md) · [当前组件白皮书](docs/WHITEPAPER.md) · [执行路线图](docs/ROADMAP.md) · [M1 API 合同](docs/API_CONTRACT.md) · [Gap 审计](docs/API_GAP_ANALYSIS.md) · [M2 三桶基线](docs/THREE_BUCKET_BASELINE.md) · [组件索引](docs/COMPONENTS.md) · [测试与工作流](docs/TESTING.md) · [数据用途说明](docs/DATA.md)

当前没有已确认交易策略或自动续开的收益实验。工程基线、数据修正和审计可复现，但复现通过不增加市场证据，也不改变 `production_authority=false`。请勿将归档快照或旧 manifest 中的 `complete=true` 作为新的研究准入。

## 本地环境

```bash
bash .codex/cloud_setup.sh
```

默认只安装依赖并检查组件一致性，不自动回放历史拟合。完整回归需要已检出测试依赖数据，见测试说明。源码包版本0.1.0是包装版本，不是策略成熟度。
