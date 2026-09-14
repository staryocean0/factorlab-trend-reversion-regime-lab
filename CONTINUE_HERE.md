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

当前里程碑：M0–M4 PASS；M5 **IN PROGRESS**。M5-1 source/profile admission 与 M5-2 Development sample adequacy 已完成；H1 尚未进入 Validation。

先读：[路线图](docs/ROADMAP.md)、[M4 冻结协议](docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.md)、[M5-1 receipt](docs/governance/TREND_M5_SOURCE_PROFILE_ADMISSION_V1.json)、[M5-2 receipt](docs/governance/TREND_M5_DEVELOPMENT_ADEQUACY_V1.json)。

## M5-1 已完成：Source / Profile Admission

M4 的 8 个 anchor carrier/profile pair 中：

| carrier | 1m official | 5m offset0 | 15m offset5 | 60m offset30 |
|---|---|---|---|---|
| `000852.SH` | ADMITTED | ADMITTED | NOT_ADMITTED | NOT_ADMITTED |
| `000688.SH` | ADMITTED | ADMITTED | NOT_ADMITTED | NOT_ADMITTED |

15m/60m 继续 fail closed；禁止本地 resample、换 offset 或 legacy 近似替代。

## M5-2 已完成：Development Sample Adequacy

真实数据运行只读取 M4 Development：`2020-07-23`–`2022-12-30`，且只使用已 admitted 的 1m/5m anchors。

主 5-bar 完整 episode-entry 数：

| carrier/profile | UP moderate | UP strong | DOWN moderate | DOWN strong |
|---|---:|---:|---:|---:|
| 000852.SH / 1m | 6012 | 3003 | 5912 | 2891 |
| 000852.SH / 5m | 1157 | 549 | 1202 | 587 |
| 000688.SH / 1m | 5805 | 2746 | 6319 | 3084 |
| 000688.SH / 5m | 1105 | 546 | 1267 | 631 |

全部超过 M4 primary 门槛 100；10/20-bar secondary 可用量也全部超过 50。

这只说明 **Development 样本量无明显阻塞**。它不说明 extreme bucket 更容易耗竭，也不代表 Validation 一定有足够样本。

本轮没有读取 2023–2025，也没有计算 survival、reversal、return、transition probability、MFE/MAE、bootstrap、p-value 或 H1 adjudication。

真实运行：Actions `34812469153`；head `7069d2afc1c2137c14a16003dcfd5ebf9c21376f`；artifact digest `sha256:95eb49298359959cd4ebf82fc21eca8d79e61e932f0d550fbb3c09efd56b3147`。

## 唯一下一步：M5-3 封存 Gate

下一次会话只允许：

1. 封存 M5 Development pipeline code identity；
2. 封存 M4 config / M5 source-admission / Development result identity；
3. 固化 exact source/dataset/profile/run hashes；
4. 形成不可被后续 Validation 结果覆盖的 Development seal receipt；
5. 保持 Validation 与 Holdout 仍锁定。

**M5-3 不运行 Validation。** 只有封存 Gate PASS 后，下一次会话才可能执行一次性的 primary `T2=4` Validation。

M5 完成前不得进入 M6。
