# 给接手外部研究AI的提示词

你接手的是 FactorLab 的**真实反转 / 均值回归策略桶**，不是通用 K 线状态识别桶，也不是 STAR50 风险态桶。

## 当前职责

本仓当前应研究并推进真实的 reversal / mean-reversion 策略及其执行与失效边界，重点包括已经迁回本仓的 R1/R2 研究包：

- **R1**：父级趋势仍完整，出现较低尺度逆向回撤后，研究恢复/反转交易机制；
- **R2**：父级区间仍完整，发生边界越界后重新进入区间，研究 failed acceptance / re-entry 机制。

此前 MR0/MR1/REV0、robust re-entry、first-passage、1m path resolution、clock/stability/execution 等研究都是该策略桶的历史证据。

先读：

1. `CONTINUE_HERE.md`
2. `docs/research/R1_R2_MIGRATION_NOTE_20260909.md`
3. `docs/archive/rmr_migrated_from_star50_20260909/`
4. `scripts/rmr_parent_state_legacy/`

## 明确禁止混桶

- **不要**把“横盘震荡 / 上行趋势 / 下行趋势”的通用因果状态识别当成本仓主产品；那属于 `factorlab-two-wave-strategy-lab`。
- **不要**把 Unsafe/Recovering、HighVol、波动聚集、冲击风险态切换当成本仓主产品；那属于 `factorlab-star50-filter-lab`。
- 本仓 research branches 上曾经误做的 `kline-recognizer` v1-v13 只保留为历史 Git 证据；它不再拥有本仓主权威。其关键权威/结果包应在 Two-Wave 桶中作为 supporting evidence 保存。
- 不要为了修 scope 删除历史证据、旧分支或旧结果；修的是当前 authority 和后续研究方向。

## 研究纪律

- 一次只改变一个可解释机制；保留失败与贡献，不以回测收益反向定义机制。
- 使用因果可得信息，信号形成与可执行时间严格分开。
- 当前历史数据已被消费，不得包装成 fresh OOS。
- 指数诊断不是可直接成交的账户收益；真实载体、成本、执行需单独合同。
- 新策略只有在预先冻结的开发/验证规则通过后才能成为当前最佳；失败版本不得覆盖既有最佳策略，但其局部贡献应保留。

`production_authority=false`。
