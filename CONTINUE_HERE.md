# 从这里接管

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 当前产品口径

本仓是**供策略调用的趋势状态识别组件**，不是独立交易策略，不直接输出买卖、仓位、订单或 Layer 4 指令。

当前里程碑：M0–M4 PASS；M5 **IN PROGRESS**。M5-1 source/profile admission、M5-2 Development sample adequacy、M5-3 Development seal、**M5-4 primary `T2=4` Validation 均已完成**。

接管必读：[路线图](docs/ROADMAP.md)、[M4 协议](docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json)、[M5-3 seal](docs/governance/TREND_M5_DEVELOPMENT_SEAL_V1.json)、[M5-4 result](docs/governance/TREND_M5_PRIMARY_VALIDATION_V1.json)。

## M5-1 / M5-2 / M5-3

当前 active exact source 只准入两指数的 `1m_official` 与 `5m_offset_0`；15m/60m anchors 与 phase-sensitivity profiles 仍 `NOT_ADMITTED`，禁止本地 resample、换 offset 或 legacy 近似替代。

Development `2020-07-23`–`2022-12-30` 的样本量 Gate 已 PASS，随后 code/config/source/data/run identities 已在 M5-3 seal 中封存。

## M5-4 已完成：Primary T2=4 Validation

真实运行：Actions `34814912150`；head `4aecd9b88a171eb51a63462bfe10eaa8168f34dc`；artifact `10335368583`；digest `sha256:acf170aab180478c73fb2dcc09ec5610c06e7276e566ee2fc7a134082e2dc045`。

只读取 CSI1000 `000852.SH` Validation `2023-01-03`–`2024-12-31`；2025 Holdout、STAR50 replication、`T2=3/5` sensitivity 均未运行。

Primary 5-bar directional survival：

| interval | direction | moderate | strong | Strong-Moderate | 95% CI | 裁决 |
|---|---|---:|---:|---:|---|---|
| 1m | UP | 0.5014 | 0.8867 | +0.3853 | [+0.3734,+0.3969] | H1_CONTRADICTED |
| 1m | DOWN | 0.5137 | 0.8932 | +0.3795 | [+0.3681,+0.3908] | H1_CONTRADICTED |
| 5m | UP | 0.5079 | 0.8901 | +0.3822 | [+0.3531,+0.4119] | H1_CONTRADICTED |
| 5m | DOWN | 0.5082 | 0.8755 | +0.3673 | [+0.3388,+0.3948] | H1_CONTRADICTED |

M4 预注册 H1 预测 Strong-Moderate 为负，即极端斜率更易耗竭。实际四个可执行 primary contrast 全部约 **+37–39pp**，CI 全部严格大于 0，因此结论是：

**`H1_CONTRADICTED_ON_ALL_EXECUTABLE_PRIMARY_CONTRASTS`。**

10-bar reversal 也一致反驳 H1：Strong-Moderate 约 `-0.236` 至 `-0.251`，各 CI 严格小于 0。当前定义下，极端斜率状态表现为**更高的短期趋势持续性、更低的反转率**，而不是更易耗竭。

这仍然不是交易语义，也不能直接推出 BUY/SELL、仓位或最终五桶产品架构。

15m/60m 保持 `NOT_ADMITTED`，raw p=`1.0`，仍保留在完整 8 项 Holm family 中。Primary Validation 没有任何 `VALIDATION_SUPPORT` contrast，因此 **Holdout 不得解锁**；one-time Validation execution contract 已标记 consumed，CI job 已禁用二次运行。

## 唯一下一步：M5-5 预注册 T2=3/5 Validation Sensitivity

下一次会话只允许执行 M4 已预注册的 `T2=3.0 / 5.0` Validation sensitivity：

1. 仍只用同一 Validation split 与 admitted 1m/5m；
2. 不能修改 T2=4 headline 裁决；
3. 不能把某个 sensitivity 结果升级成 primary；
4. 不能用 sensitivity、STAR50 或 pooling rescue H1；
5. Holdout **继续永久锁定于本次 H1 support 流程**，不得因 sensitivity 看起来更好而打开。

M5-5 完成后再按冻结顺序处理 replication/剩余报告；M5 完成前不得进入 M6。
