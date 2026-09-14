# FactorLab 趋势反转与均值回归研究

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 产品定位

本仓收敛为**可被策略调用的 Layer 2 趋势状态识别组件**，不是独立交易策略，也不直接输出买卖、仓位、订单或 Layer 4 指令。

**M0–M5 已完成。** M5 closeout authority：`docs/governance/TREND_M5_CLOSEOUT_V1.json`。下一里程碑是 M6 表示层裁决，本轮没有进入 M6。

## M5 最终研究结论

M4 预注册的 exhaustion H1 认为 extreme absolute slope state 可能比 moderate trend state 更难持续、更易反转。M5 的结果稳定地指向相反方向：

- CSI1000 primary `T2=4`：admitted 1m/5m、UP/DOWN 四个 survival Strong-Moderate 均约 **+36.7pp～+38.5pp**，95% CI 全部严格大于 0；正式 headline 为 `H1_CONTRADICTED_ON_ALL_EXECUTABLE_PRIMARY_CONTRASTS`。
- CSI1000 predeclared `T2=3/5` sensitivity：**8/8** 可执行 contrasts 继续反驳 H1，0 个朝 H1 方向。
- STAR50 independent `T2=4` replication：四个 survival contrasts 分别约 **+37.35pp / +37.27pp / +37.30pp / +33.94pp**，CI 全部严格大于 0；四个 reversal10 contrasts 均明显为负。Replication 状态为 `CLEAR_QUALITATIVE_REPLICATION_OF_PRIMARY_CONTRADICTION`。

因此，在当前**已准入的 1m/5m exact views** 上，extreme absolute slope 更适合作为**趋势 persistence/strength descriptor 的候选语义**，而不是“更可能耗竭”的标签。

这仍然没有交易动作语义，也没有证明正式五桶一定优于“三桶+连续 strength”。5-bar direction-adjusted return 没有呈现与 persistence/reversal 同等级的稳定证据，所以不能把上述状态差异直接解释为收益规则。

## 证据边界

- 15m/60m anchors 与 phase profiles：`NOT_ADMITTED_NOT_EXECUTED`；
- 禁止 local resampling、profile substitution、legacy promotion；
- STAR50 与 CSI1000 未 pooling；
- 2025 protocol Holdout 从未打开，且因 primary support rule 未通过继续关闭；
- M5-4 / M5-5 / M5-6 one-shot jobs 均 consumed，禁止 rerun；
- `production_authority=false`、`fresh_oos=false`。

## 唯一下一步

**M6 — Representation Decision**：只在“三桶+连续 strength / 正式五桶 / 三桶主状态+五桶诊断扩展”之间做产品表示选择。M6 不允许重跑 M5、重调 `T2`、打开 Holdout 或映射 BUY/SELL/position。

## 入口

[当前状态与下一步边界](CONTINUE_HERE.md) · [执行路线图](docs/ROADMAP.md) · [M5 closeout](docs/governance/TREND_M5_CLOSEOUT_V1.json) · [M5 primary](docs/governance/TREND_M5_PRIMARY_VALIDATION_V1.json) · [M5 sensitivity](docs/governance/TREND_M5_T2_SENSITIVITY_V1.json) · [M5 STAR50 replication](docs/governance/TREND_M5_STAR50_REPLICATION_V1.json) · [当前组件白皮书](docs/WHITEPAPER.md) · [Gap 审计](docs/API_GAP_ANALYSIS.md)

## 本地环境

```bash
bash .codex/cloud_setup.sh
```

默认只安装依赖并检查组件一致性，不自动运行研究 outcome。
