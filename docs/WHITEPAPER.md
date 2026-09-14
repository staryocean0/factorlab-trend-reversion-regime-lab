# 趋势状态识别组件：当前研究与工程白皮书

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](REPOSITORY_STATE.json) · [最新研究解释](research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

> 本白皮书定义产品定位与当前研究证据；上方状态块仍是历史 evidence authority。完成 M5 研究步骤不自动授予 production authority。

## 1. 产品定位

本仓核心交付是供多个上层调用者使用的 **Layer 2 趋势状态识别组件**。它描述指定 `symbol + as_of + bar_interval/profile` 下的趋势状态与连续强度，不输出买卖、仓位、订单、策略选择或 Layer 4 动作。

## 2. 已冻结工程与研究流程

- M2：20-bar `log(close)` OLS signed slope t-score，`T1=2.0`，completed/available、fail closed；
- M3：1m×1、5m×5、15m×2、60m×2 共 10 个 versioned Layer-1 view profiles；不同周期独立并存，无 `global_state`；
- M4：五桶研究协议在 outcome 前冻结，primary `T2=4.0`、sensitivity `3/5`、Development/Validation/Holdout split、episode unit、horizons、sample floors、week-cluster bootstrap、Holm family 与 negative-result rule 全部预注册；
- M5-1：当前 active exact source 只准入两指数 `1m_official` 与 `5m_offset_0`；15m/60m 与 phase sensitivity source fail closed；
- M5-2：Development 样本量 Gate PASS；
- M5-3：code/config/source/data/run identities 在 Validation 前 seal；
- M5-4：primary `T2=4` one-shot Validation 已消费并封存；
- M5-5：预注册 `T2=3/5` Validation sensitivity 已消费并封存。

## 3. M4 原始 H1

H1：在相同 interval/profile 与相同方向内，极端绝对斜率状态可能比中等趋势状态**更难持续、更容易衰减或反转**。

五桶候选：`STRONG_DOWN / DOWN / SIDEWAYS / UP / STRONG_UP`，其中 `T1=2.0`、primary `T2=4.0`。Primary endpoint 是 5-bar directional survival 的 `Strong-Moderate`，H1 预期为负；secondary confirmatory 包括 10-bar reversal probability（预期正）与 5-bar direction-adjusted return（预期负）。

Primary family 预注册为 `4 intervals × 2 directions = 8`，Holm FWER alpha=.05。未准入 planned contrast raw p 固定为 1.0，family 不得缩小。Primary contrast 还必须 `<= -0.05` 才算有实际量级的 H1 support。

## 4. M5-4 Primary T2=4 Validation：H1 被反驳

真实运行只读取 CSI1000 `000852.SH` Validation `2023-01-03`–`2024-12-31`，仅执行 admitted 1m/5m；2025 Holdout、STAR50 replication、T2=3/5 sensitivity 当时均未运行。

| interval | direction | moderate survival5 | strong survival5 | Strong-Moderate | 95% CI |
|---|---|---:|---:|---:|---|
| 1m | UP | 0.5014 | 0.8867 | +0.3853 | [+0.3734,+0.3969] |
| 1m | DOWN | 0.5137 | 0.8932 | +0.3795 | [+0.3681,+0.3908] |
| 5m | UP | 0.5079 | 0.8901 | +0.3822 | [+0.3531,+0.4119] |
| 5m | DOWN | 0.5082 | 0.8755 | +0.3673 | [+0.3388,+0.3948] |

所有可执行 primary contrasts 的方向都与 H1 相反，而且 CI 全部严格高于 0。因此正式 headline 是：

**`H1_CONTRADICTED_ON_ALL_EXECUTABLE_PRIMARY_CONTRASTS`。**

10-bar reversal Strong-Moderate 约为 `-0.236` 至 `-0.251`，95% CI 全部严格小于 0。冻结定义下 extreme slope state 表现为**更强的短期趋势持续性与更低的反转概率**，而不是耗竭。

Primary support rule 未通过，所以 2025 protocol Holdout 保持关闭；M5-4 one-shot execution 已 consumed，rerun 被 CI 禁止。

## 5. M5-5 T2=3/5 Sensitivity：反证对阈值稳健

M5-5 使用完全相同的 CSI1000 Validation split、相同 admitted 1m/5m views、相同 episode/endpoint/bootstrap 定义，只替换为 M4 预注册的 sensitivity `T2=3.0` 与 `T2=5.0`。它不建立新 primary family，也不能改写 T2=4 headline。

`T2=3`：

| interval | direction | Strong-Moderate survival5 | 95% CI | reversal10 Strong-Moderate |
|---|---|---:|---|---:|
| 1m | UP | +0.4045 | [+0.3903,+0.4179] | -0.2627 |
| 1m | DOWN | +0.4110 | [+0.4005,+0.4220] | -0.2684 |
| 5m | UP | +0.4095 | [+0.3805,+0.4400] | -0.2512 |
| 5m | DOWN | +0.4147 | [+0.3864,+0.4432] | -0.2854 |

`T2=5`：

| interval | direction | Strong-Moderate survival5 | 95% CI | reversal10 Strong-Moderate |
|---|---|---:|---|---:|
| 1m | UP | +0.3572 | [+0.3436,+0.3711] | -0.2190 |
| 1m | DOWN | +0.3459 | [+0.3329,+0.3587] | -0.2247 |
| 5m | UP | +0.3477 | [+0.3179,+0.3781] | -0.1996 |
| 5m | DOWN | +0.3382 | [+0.3098,+0.3673] | -0.2206 |

结果是 **8/8 sensitivity contrasts = `SENSITIVITY_H1_CONTRADICTED`，0/8 朝 H1 方向**。因此当前 CSI1000 证据表明：extreme slope 的更高短期持续性/更低反转率对 `T2=3/4/5` 均稳健，原 exhaustion H1 的失败不是 T2=4 单点阈值造成。

5-bar direction-adjusted return 并不呈现同等稳定的方向，因此不能把上述状态持续性差异直接翻译成收益规则。

M5-5 one-shot execution 同样已 consumed，rerun 被 CI 禁止；Holdout 仍保持关闭。

## 6. 这个结果不意味着什么

M5-4/M5-5 的反证不自动意味着：

- 正式五桶一定优于三桶+连续强度；
- `STRONG_UP` 应买入或卖出；
- `STRONG_DOWN` 应采取某个交易动作；
- 任何收益或仓位规则已被验证；
- 组件已获得 production authority。

它只改变研究认识：原“极端斜率=更可能耗竭”的假设不成立；极端斜率反而是一个**持续性强度**语义候选。是否值得成为正式产品状态，要等 M5 完成后由 M6 裁决。

## 7. Source / Holdout 边界继续不变

15m/60m 与 phase-offset profiles 仍为 `NOT_ADMITTED`；没有 current active exact-view receipt 时不得本地 resample、换 offset 或用 legacy 近似补齐。

Primary Validation 没有 `VALIDATION_SUPPORT` contrast，因此 M4 的 Holdout unlock 条件未满足。2025 protocol Holdout 对本次 H1 support 路径保持关闭，不能为了寻找支持而读取。Sensitivity 结果也不能改变这一点。

## 8. 唯一下一步：M5-6 Cross-carrier Replication / Remaining Robustness

只允许按 M4 step 7 做剩余独立 replication/reporting：STAR50 `000688.SH` 只能使用 M5-1 已 admitted 的 1m official / 5m offset0 exact views；不能与 CSI1000 pooling，不能改写 CSI1000 T2=4 headline，不能 rescue 原 exhaustion H1，也不能打开 Holdout。Phase-sensitivity profiles 没有 exact current receipt 时继续 fail closed。

M5-6 完成并收口 M5 后，M6 才裁决最终表示：三桶+连续强度、正式五桶、或三桶主状态+五桶诊断扩展。

## 9. Consumer 与产品边界

M7 才实现正式 `regime_state_consumer_v1` facade、snapshot store、expiry/no-fallback 和 conformance tests；M8 才做上层调用集成；M9 负责版本、migration 与发布治理。

全程不变：`production_authority=false`、`fresh_oos=false`，组件不是交易策略，状态到交易动作的映射属于上层。
