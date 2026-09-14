# 从这里接管

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 当前产品口径

本仓是**供策略调用的 Layer 2 趋势状态识别组件**，不是独立交易策略，不直接输出买卖、仓位、订单、策略路由或 Layer 4 指令。

当前里程碑：**M0–M5 COMPLETE**。M5 outcome 证据链已经封存，机器 closeout 为 `docs/governance/TREND_M5_CLOSEOUT_V1.json`。本轮之后唯一允许进入的是 **M6 representation decision**；不得重新打开 M5 outcome 或 2025 Holdout。

接管必读：[路线图](docs/ROADMAP.md)、[M4 协议](docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json)、[M5 primary](docs/governance/TREND_M5_PRIMARY_VALIDATION_V1.json)、[M5 sensitivity](docs/governance/TREND_M5_T2_SENSITIVITY_V1.json)、[M5 STAR50 replication](docs/governance/TREND_M5_STAR50_REPLICATION_V1.json)、[M5 closeout](docs/governance/TREND_M5_CLOSEOUT_V1.json)。

## M5 最终科学结论

M4 预注册 H1 是：相同 interval/方向下，极端绝对斜率状态可能比 moderate trend 更难持续、更容易反转。

### CSI1000 primary `T2=4`

`000852.SH` Validation=`2023-01-03`–`2024-12-31`，仅 admitted 1m/5m：

| interval | direction | survival Strong-Moderate | 95% CI | reversal10 Strong-Moderate |
|---|---|---:|---|---:|
| 1m | UP | +0.3853 | [+0.3734,+0.3969] | -0.2476 |
| 1m | DOWN | +0.3795 | [+0.3681,+0.3908] | -0.2507 |
| 5m | UP | +0.3822 | [+0.3531,+0.4119] | -0.2371 |
| 5m | DOWN | +0.3673 | [+0.3388,+0.3948] | -0.2360 |

正式 headline：**`H1_CONTRADICTED_ON_ALL_EXECUTABLE_PRIMARY_CONTRASTS`**。

### T2 sensitivity

M4 预注册 `T2=3/5` 共 8 个可执行 sensitivity contrasts，**8/8 均 `SENSITIVITY_H1_CONTRADICTED`，0 个朝 H1 方向**。因此反证并非 `T2=4` 单点阈值现象。

### STAR50 independent replication

`000688.SH` 使用相同 Validation、primary `T2=4`、admitted 1m/5m：

| interval | direction | survival Strong-Moderate | 95% CI | reversal10 Strong-Moderate |
|---|---|---:|---|---:|
| 1m | UP | +0.3735 | [+0.3621,+0.3850] | -0.2504 |
| 1m | DOWN | +0.3727 | [+0.3608,+0.3845] | -0.2090 |
| 5m | UP | +0.3730 | [+0.3416,+0.4042] | -0.2620 |
| 5m | DOWN | +0.3394 | [+0.3141,+0.3640] | -0.1923 |

四个 replication contrasts 全部清楚同方向，正式结论：**`CLEAR_QUALITATIVE_REPLICATION_OF_PRIMARY_CONTRADICTION`**。

综合解释：在**已准入的 1m/5m exact views** 上，extreme absolute slope state 稳定表现为**更高的短期方向持续性、更低的反转概率**，而不是更易耗竭。因此 extreme absolute slope 可以作为 persistence/strength descriptor 的候选语义，但这仍不等于正式五桶已确定，更不产生交易动作语义。

## M5 的硬边界

- 15m/60m anchors：`NOT_ADMITTED_NOT_EXECUTED`；
- phase-offset profiles：`NOT_ADMITTED_NOT_EXECUTED`；
- 禁止 local resampling / profile substitution / legacy promotion；
- CSI1000 与 STAR50 **没有 pooling**；
- 2025 protocol Holdout **从未打开**，且因 primary support rule 未通过而继续关闭；
- M5-4、M5-5、M5-6 one-shot outcome jobs 均已 consumed，禁止 rerun；
- `production_authority=false`、`fresh_oos=false`；
- 5-bar direction-adjusted return 没有像 persistence/reversal 那样给出稳定的同方向证据，不能把状态差异直接翻译成收益规则。

## 唯一下一步：M6 Representation Decision

下一次会话只能做表示层裁决，在以下候选中选择并冻结产品语义：

1. **三桶 + 连续 strength**；
2. **正式五桶**；
3. **三桶作为主状态 + 五桶作为诊断/研究扩展**。

M6 必须基于 M5 已封存证据做产品表示决策，**不能重新调 T2、重跑 Validation/Holdout 或把状态映射成 BUY/SELL/position**。M6 完成后才进入 M7 Consumer API。
