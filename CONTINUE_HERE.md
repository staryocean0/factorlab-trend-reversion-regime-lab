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

当前里程碑：M0–M4 PASS；M5 **IN PROGRESS**。M5-1 source/profile admission、M5-2 Development sample adequacy、M5-3 Development seal、M5-4 primary `T2=4` Validation、**M5-5 `T2=3/5` Validation sensitivity 均已完成**。

接管必读：[路线图](docs/ROADMAP.md)、[M4 协议](docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json)、[M5-4 result](docs/governance/TREND_M5_PRIMARY_VALIDATION_V1.json)、[M5-5 result](docs/governance/TREND_M5_T2_SENSITIVITY_V1.json)。

## M5-4 Primary T2=4：headline 已冻结

CSI1000 `000852.SH` Validation=`2023-01-03`–`2024-12-31`，admitted 1m/5m 的四个 primary 5-bar directional-survival contrast 全部为正约 `+0.367` 至 `+0.385`，95% CI 全部严格大于 0；10-bar reversal Strong-Moderate 约 `-0.236` 至 `-0.251`，CI 全部严格小于 0。

正式 headline：**`H1_CONTRADICTED_ON_ALL_EXECUTABLE_PRIMARY_CONTRASTS`**。这意味着冻结定义下 extreme slope state 更持久、更少反转，而不是更易耗竭。它没有交易动作语义。

Primary support rule 未通过，所以 2025 Holdout **永久保持关闭于本次 H1 support 路径**；M5-4 one-shot job 已 consumed 并禁止 rerun。

## M5-5 已完成：T2=3/5 Validation Sensitivity

真实运行：Actions `34816576915`；head `9e622c653a5510e73444a00f76881050946ffd1a`；artifact `10336711547`；digest `sha256:4c654375daa971c9aa028dc29fea1f1facab889cb29104a1b740f7e34efc575c`。

仍只读取同一 CSI1000 Validation、同一 admitted 1m/5m；没有读取 Holdout，没有运行 STAR50 replication，也没有重跑 M5-4。

### T2=3

| interval | direction | survival Strong-Moderate | 95% CI | reversal10 Strong-Moderate | sensitivity label |
|---|---|---:|---|---:|---|
| 1m | UP | +0.4045 | [+0.3903,+0.4179] | -0.2627 | H1_CONTRADICTED |
| 1m | DOWN | +0.4110 | [+0.4005,+0.4220] | -0.2684 | H1_CONTRADICTED |
| 5m | UP | +0.4095 | [+0.3805,+0.4400] | -0.2512 | H1_CONTRADICTED |
| 5m | DOWN | +0.4147 | [+0.3864,+0.4432] | -0.2854 | H1_CONTRADICTED |

### T2=5

| interval | direction | survival Strong-Moderate | 95% CI | reversal10 Strong-Moderate | sensitivity label |
|---|---|---:|---|---:|---|
| 1m | UP | +0.3572 | [+0.3436,+0.3711] | -0.2190 | H1_CONTRADICTED |
| 1m | DOWN | +0.3459 | [+0.3329,+0.3587] | -0.2247 | H1_CONTRADICTED |
| 5m | UP | +0.3477 | [+0.3179,+0.3781] | -0.1996 | H1_CONTRADICTED |
| 5m | DOWN | +0.3382 | [+0.3098,+0.3673] | -0.2206 | H1_CONTRADICTED |

因此 8 个预注册 T2 sensitivity contrasts **8/8 都继续反驳 exhaustion H1，0 个朝 H1 方向**。这说明 M5-4 的反证并不是只由 `T2=4` 这个阈值造成。

M5-5 只是 robustness evidence：没有建立新的 primary family，不能改写或升级 headline，也不能打开 Holdout。M5-5 one-shot execution 已 consumed，CI 已禁止 rerun。

15m/60m 与 phase-offset profiles 继续 `NOT_ADMITTED`；禁止本地 resample、换 offset 或 legacy 近似补齐。

## 唯一下一步：M5-6 Cross-carrier Replication / Remaining Robustness

下一次会话只允许按 M4 step 7 做剩余 replication/reporting：

1. 以 STAR50 `000688.SH` 为独立 replication carrier；
2. 只使用 M5-1 已 admitted 的 1m official / 5m offset0 exact views；
3. primary representation 仍以冻结 `T2=4` 为 replication headline，不得改变 CSI1000 headline；
4. 不池化 STAR50 与 CSI1000，不用 replication rescue 原 H1；
5. phase-sensitivity profiles 仍 `NOT_ADMITTED`，没有 exact current receipt 就继续 fail closed；
6. 2025 Holdout 继续不读取。

M5-6 完成并收口 M5 后，才允许进入 M6 表示层裁决。M6 仍只讨论三桶/五桶/连续强度表示，不产生交易动作。
