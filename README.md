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

M0–M4 已完成；**M5 正在进行中，M5-1 source/profile admission 已完成。** 当前 exact current source 只准入两指数的 `1m_official` 与 `5m_offset_0`；M4 anchor 中的 15m/60m 因缺少 current active exact-view receipt 而 `NOT_ADMITTED`，不得本地重采样或用 legacy 文件近似替代。

M5-1 没有计算五桶 episode 数、survival、forward return、transition/reversal、MFE/MAE，也没有读取 Validation/Holdout outcome，因此尚无新的五桶市场结论。

历史归档 `available_at` 按已冻结的数据所有者澄清只表示 historical retrieval availability；M5 causal replay 将 completed bar 的 runtime visibility 映射为 `runtime_available_at = bar_end`，同时保留 raw historical `available_at` 作为 provenance，不声称测得 feed latency。

## 当前唯一下一步

**M5-2 — Development pipeline + sample-adequacy checks，仅限已 admitted 的 1m/5m anchors。** Validation 与 Holdout 继续锁定；Development code/config/receipt 封存前不得读取 Validation outcome。

## 入口

[当前状态与下一步边界](CONTINUE_HERE.md) · [当前组件白皮书](docs/WHITEPAPER.md) · [执行路线图](docs/ROADMAP.md) · [M1 API 合同](docs/API_CONTRACT.md) · [Gap 审计](docs/API_GAP_ANALYSIS.md) · [M2 三桶基线](docs/THREE_BUCKET_BASELINE.md) · [M4 冻结协议](docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.md) · [M5-1 admission receipt](docs/governance/TREND_M5_SOURCE_PROFILE_ADMISSION_V1.md) · [M5-1 machine receipt](docs/governance/TREND_M5_SOURCE_PROFILE_ADMISSION_V1.json) · [测试与工作流](docs/TESTING.md) · [数据用途说明](docs/DATA.md)

当前没有已确认交易策略。M5 研究必须继续遵循冻结协议，不能根据后续结果修改 primary T2、split、profile、horizon 或样本门槛。工程/准入通过不自动改变 `production_authority=false`、`fresh_oos=false` 或既有 scientific status。

## 本地环境

```bash
bash .codex/cloud_setup.sh
```

默认只安装依赖并检查组件一致性，不自动回放历史拟合。完整回归需要已检出测试依赖数据，见测试说明。源码包版本0.1.0是包装版本，不是策略成熟度。
