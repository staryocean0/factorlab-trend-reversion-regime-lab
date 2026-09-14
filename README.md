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

M0–M4 已完成；M5 正在进行。M5-1 source/profile admission、M5-2 Development adequacy、M5-3 seal、M5-4 primary `T2=4` Validation、**M5-5 `T2=3/5` Validation sensitivity** 已完成。

M5-4 的正式 headline 是 **`H1_CONTRADICTED_ON_ALL_EXECUTABLE_PRIMARY_CONTRASTS`**：在 CSI1000 已准入 1m/5m、UP/DOWN 四个 primary contrast 上，5-bar directional survival 的 Strong-Moderate 约 `+0.367` 至 `+0.385`，95% CI 全部严格大于 0；10-bar reversal Strong-Moderate 约 `-0.236` 至 `-0.251`，CI 全部严格小于 0。冻结定义下 extreme slope state 更持久、反转更少，而不是更易耗竭。

M5-5 进一步检查预注册 `T2=3.0 / 5.0`。8 个可执行 sensitivity contrast **8/8 都继续 `SENSITIVITY_H1_CONTRADICTED`，0 个朝 H1 方向**：`T2=3` 的 survival Strong-Moderate 约 `+0.405` 至 `+0.415`，`T2=5` 约 `+0.338` 至 `+0.357`，所有 95% CI 仍严格大于 0；10-bar reversal 仍全部为负。这说明 M5-4 的反证不是 `T2=4` 单点阈值现象。

这些结果仍然**没有交易动作语义**，也不等于已经决定最终采用五桶产品表示。Primary support rule 未通过，所以 2025 protocol Holdout 保持关闭；M5-4 与 M5-5 one-shot jobs 都已 consumed，CI 已禁止二次运行。

15m/60m 与 phase-offset profiles 继续 `NOT_ADMITTED`，禁止本地 resample、换 offset 或 legacy 近似补齐。

## 当前唯一下一步

**M5-6 — cross-carrier replication / remaining robustness reporting。** 只允许对 STAR50 `000688.SH` 使用已 admitted 的 1m official / 5m offset0 exact views 做独立 replication，不能池化 CSI1000，不能改写 CSI1000 headline，不能 rescue 原 H1，也不能打开 Holdout。Phase-sensitivity profiles 在没有 current active exact-view receipt 时继续 fail closed。

## 入口

[当前状态与下一步边界](CONTINUE_HERE.md) · [执行路线图](docs/ROADMAP.md) · [M4 冻结协议](docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.md) · [M5-4 Validation result](docs/governance/TREND_M5_PRIMARY_VALIDATION_V1.json) · [M5-5 sensitivity result](docs/governance/TREND_M5_T2_SENSITIVITY_V1.json) · [当前组件白皮书](docs/WHITEPAPER.md) · [Gap 审计](docs/API_GAP_ANALYSIS.md)

`production_authority=false`、`fresh_oos=false` 与既有 scientific status 不因这些研究步骤自动改变。

## 本地环境

```bash
bash .codex/cloud_setup.sh
```

默认只安装依赖并检查组件一致性，不自动运行研究 outcome。
