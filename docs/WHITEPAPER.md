# 趋势状态识别组件：当前研究与工程白皮书

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](REPOSITORY_STATE.json) · [最新研究解释](research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

> 本白皮书定义产品定位与当前研究证据；上方状态块仍是历史 evidence authority。M5 完成不自动授予 production authority，也不产生 fresh OOS 结论。

## 1. 产品定位

本仓核心交付是供多个上层调用者使用的 **Layer 2 趋势状态识别组件**。它描述指定 `symbol + as_of + bar_interval/profile` 下的趋势状态与连续强度，不输出买卖、仓位、订单、策略选择或 Layer 4 动作。

## 2. 当前里程碑状态

- M0–M4：PASS；
- **M5：PASS / COMPLETE**；
- **唯一下一步：M6 Representation Decision**；
- M7 才实现正式 consumer；M8 才进行上层策略集成；M9 做发布治理。

M5 总 closeout：`docs/governance/TREND_M5_CLOSEOUT_V1.json`。

## 3. 已冻结工程与研究协议

- M2：20-bar `log(close)` OLS signed slope t-score，`T1=2.0`；
- M3：1m×1、5m×5、15m×2、60m×2 versioned profiles，无 `global_state`；
- M4：五桶 protocol 在 outcome 前冻结，primary `T2=4`、sensitivity `T2=3/5`、Development/Validation/Holdout、episode/horizon/sample floor、ISO-week bootstrap、Holm family 与 negative-result rule 均预注册；
- M5-1：两 carrier 当前只准入 `1m_official / 5m_offset_0`；15m/60m 与 phase profiles fail closed；
- M5-2：Development sample adequacy PASS；
- M5-3：code/config/source/data/run identities 在 Validation 前 seal；
- M5-4/M5-5/M5-6：三个 outcome 步骤均 one-shot consumed，禁止 rerun。

## 4. M4 原始 H1

H1：在相同 interval/profile 与相同方向内，extreme absolute slope state 可能比 moderate trend state **更难持续、更容易衰减或反转**。

五桶候选为 `STRONG_DOWN / DOWN / SIDEWAYS / UP / STRONG_UP`，`T1=2.0`，primary `T2=4.0`。Primary endpoint 是 5-bar directional survival 的 `Strong-Moderate`，H1 预期为负；10-bar reversal H1 预期为正；5-bar direction-adjusted return H1 预期为负。

## 5. M5-4：CSI1000 Primary T2=4 反驳 H1

CSI1000 `000852.SH` Validation=`2023-01-03`–`2024-12-31`，仅 admitted 1m/5m：

| interval | direction | moderate survival5 | strong survival5 | Strong−Moderate | 95% CI | reversal10 diff |
|---|---|---:|---:|---:|---|---:|
| 1m | UP | 0.5014 | 0.8867 | +0.3853 | [+0.3734,+0.3969] | -0.2476 |
| 1m | DOWN | 0.5137 | 0.8932 | +0.3795 | [+0.3681,+0.3908] | -0.2507 |
| 5m | UP | 0.5079 | 0.8901 | +0.3822 | [+0.3531,+0.4119] | -0.2371 |
| 5m | DOWN | 0.5082 | 0.8755 | +0.3673 | [+0.3388,+0.3948] | -0.2360 |

正式 headline：**`H1_CONTRADICTED_ON_ALL_EXECUTABLE_PRIMARY_CONTRASTS`**。Extreme slope state 的短期 persistence 显著更高，10-bar reversal 显著更低。

## 6. M5-5：T2=3/5 Sensitivity 强化反证

完全相同的 CSI1000 Validation、source/profile、episode/endpoint/bootstrap 定义，仅使用 M4 预注册 sensitivity thresholds：

- `T2=3` survival Strong−Moderate：`+0.4045 / +0.4110 / +0.4095 / +0.4147`；所有 CI > 0；
- `T2=5`：`+0.3572 / +0.3459 / +0.3477 / +0.3382`；所有 CI > 0；
- **8/8 executable sensitivity contrasts = H1_CONTRADICTED，0/8 朝 H1 方向**；
- reversal10 同样全部为负。

因此 primary 反证对 `T2=3/4/5` 均稳健，不是单一阈值现象。

## 7. M5-6：STAR50 独立复制

STAR50 `000688.SH`，相同 Validation、primary `T2=4`，仅 admitted 1m/5m：

| interval | direction | moderate survival5 | strong survival5 | Strong−Moderate | 95% CI | reversal10 diff |
|---|---|---:|---:|---:|---|---:|
| 1m | UP | 0.4953 | 0.8687 | +0.3735 | [+0.3621,+0.3850] | -0.2504 |
| 1m | DOWN | 0.5135 | 0.8862 | +0.3727 | [+0.3608,+0.3845] | -0.2090 |
| 5m | UP | 0.4926 | 0.8657 | +0.3730 | [+0.3416,+0.4042] | -0.2620 |
| 5m | DOWN | 0.5330 | 0.8725 | +0.3394 | [+0.3141,+0.3640] | -0.1923 |

4/4 replication contrasts 的 survival CI 均严格大于 0，reversal CI 均严格小于 0。正式状态：**`CLEAR_QUALITATIVE_REPLICATION_OF_PRIMARY_CONTRADICTION`**。STAR50 独立报告，没有与 CSI1000 pooling，也没有建立新的 primary significance family。

## 8. M5 最终科学解释

M5 的完整证据链在三个层次上一致：

1. CSI1000 primary `T2=4`；
2. CSI1000 predeclared `T2=3/5` sensitivity；
3. STAR50 independent `T2=4` replication。

因此，原“极端斜率更容易耗竭”的 H1 被稳健反驳。对**已准入 1m/5m exact views**，absolute slope extremeness 是一个有实证支持的 **persistence/strength descriptor 候选**：极端状态更容易保持同方向、较少进入相反方向状态。

这并不等于：

- 正式五桶一定优于三桶+连续 strength；
- `STRONG_UP`/`STRONG_DOWN` 是交易信号；
- 已证明某种收益/仓位规则；
- 已获得 production authority。

尤其 5-bar direction-adjusted return 并没有像 persistence/reversal 那样形成稳定一致的证据，因此**不得把 persistence 差异直接翻译成 alpha 或交易动作**。

## 9. Scope Limits

- admitted intervals：1m、5m；
- 15m/60m anchors：`NOT_ADMITTED_NOT_EXECUTED`；
- phase profiles：`NOT_ADMITTED_NOT_EXECUTED`；
- 禁止 local resampling、profile substitution、legacy promotion；
- 无 carrier pooling；
- 2025 protocol Holdout 从未打开，primary support rule 失败后继续关闭；
- `fresh_oos=false`；
- `production_authority=false`；
- `m5_outcome_work_reopen_allowed=false`。

## 10. M6：唯一下一步

M6 只做产品表示层裁决：

1. 三桶 + 连续 strength；
2. 正式五桶；
3. 三桶主状态 + 五桶诊断/研究扩展。

M6 应使用 M5 已封存的 persistence/strength 证据，但不得重开 M5、重调 T2、打开 Holdout 或增加交易动作语义。M6 完成后才进入 M7 consumer implementation。

## 11. Consumer 与上层边界

M7 实现正式 `regime_state_consumer_v1` facade、snapshot store、expiry/no-fallback 与 conformance tests；M8 做上层调用集成；M9 负责 schema/version/migration/release governance。

全程不变：**组件不是策略，状态到交易动作的映射属于上层。**
