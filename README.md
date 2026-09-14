# FactorLab 趋势反转与均值回归研究

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 新产品定位

本仓工程收敛为**可被策略调用的趋势状态识别组件**，不是独立交易策略，也不直接输出买卖、仓位或 Layer 4 指令。

M0–M4 已完成；M5 正在进行。M5-1 source/profile admission、M5-2 Development adequacy、M5-3 seal、**M5-4 primary `T2=4` Validation** 已完成。

M5-4 的预注册 H1 是“极端绝对斜率比中等趋势更易耗竭/反转”。真实 CSI1000 Validation 却在已准入 1m/5m、UP/DOWN 四个 primary contrast 上全部得到相反结果：5-bar directional survival 的 Strong-Moderate 约 **+0.367 至 +0.385**，95% CI 全部严格大于 0；10-bar reversal Strong-Moderate 约 **-0.236 至 -0.251**，CI 全部严格小于 0。因此正式 headline 是：

**`H1_CONTRADICTED_ON_ALL_EXECUTABLE_PRIMARY_CONTRASTS`。**

这说明冻结定义下的 extreme slope state 在短周期上更持久、反转更少，而不是更易耗竭。它仍然**没有任何交易动作语义**，也不等于已经决定最终采用五桶产品表示。

15m/60m 继续 `NOT_ADMITTED` 并按预注册规则留在 8 项 Holm family 中。Primary Validation 没有 support contrast，所以 2025 protocol Holdout 保持关闭；one-time Validation 已 consumed，CI 已禁止二次运行。

## 当前唯一下一步

**M5-5 — 预注册 `T2=3.0 / 5.0` Validation sensitivity。** 它只能解释阈值敏感性，不能替代或 rescue `T2=4` headline，也不能据此打开 Holdout。STAR50 replication 仍是后续独立步骤。

## 入口

[当前状态与下一步边界](CONTINUE_HERE.md) · [执行路线图](docs/ROADMAP.md) · [M4 冻结协议](docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.md) · [M5-3 Development seal](docs/governance/TREND_M5_DEVELOPMENT_SEAL_V1.md) · [M5-4 Validation result](docs/governance/TREND_M5_PRIMARY_VALIDATION_V1.md) · [M5-4 machine receipt](docs/governance/TREND_M5_PRIMARY_VALIDATION_V1.json) · [当前组件白皮书](docs/WHITEPAPER.md) · [Gap 审计](docs/API_GAP_ANALYSIS.md)

`production_authority=false`、`fresh_oos=false` 与既有 scientific status 不因本轮 Validation 自动改变。

## 本地环境

```bash
bash .codex/cloud_setup.sh
```

默认只安装依赖并检查组件一致性，不自动运行研究 outcome。
