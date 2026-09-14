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

M0 定位/路线图与 M1 接口合同审计均已完成。当前唯一下一阶段是 **M2 三桶基线冻结与可复现性**；M2 完成前不进入多周期 profile 或五桶实证。详见 [当前白皮书](docs/WHITEPAPER.md)、[执行路线图](docs/ROADMAP.md)、[M1 API 合同](docs/API_CONTRACT.md) 与 [M1 Gap 审计](docs/API_GAP_ANALYSIS.md)。

## 入口

[当前状态与下一步边界](CONTINUE_HERE.md) · [当前组件白皮书](docs/WHITEPAPER.md) · [执行路线图](docs/ROADMAP.md) · [M1 API 合同](docs/API_CONTRACT.md) · [M1 Gap 审计](docs/API_GAP_ANALYSIS.md) · [组件索引](docs/COMPONENTS.md) · [测试与工作流](docs/TESTING.md) · [数据用途说明](docs/DATA.md)

当前没有已确认策略或自动续开的实验。已完成的研究、数据修正和审计可复现，但复现通过不增加市场证据。请勿将归档快照或旧manifest中的complete=true作为新的研究准入。

## 本地环境

```bash
bash .codex/cloud_setup.sh
```

默认只安装依赖并检查组件一致性，不自动回放历史拟合。完整回归需要已检出测试依赖数据，见测试说明。源码包版本0.1.0是包装版本，不是策略成熟度。
