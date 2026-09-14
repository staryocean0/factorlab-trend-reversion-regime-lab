# 趋势状态识别组件路线图

> 本路线图定义未来工作的执行顺序。它不是收益研究结论，也不把尚未验证的状态直接写成策略规则。
>
> 执行纪律：**一次会话只推进当前里程碑；完成当前 Gate 后也不自动进入下一里程碑。**

## 当前进度

- **M0 — PASS**：产品定位、白皮书与路线图。
- **M1 — PASS**：consumer 审计、API 合同与 Gap List。
- **M2 — PASS**：冻结 20-bar log-close OLS signed slope t-score 三桶基线，`T1=2.0`。
- **M3 — PASS**：冻结 `1m/5m/15m/60m` versioned profile registry、view/cadence/as-of 边界。
- **M4 — PASS**：结果前冻结五桶实验协议。
- **M5 — PASS / COMPLETE**：source admission、Development adequacy、pre-Validation seal、CSI1000 primary、T2 sensitivity、STAR50 replication 全部按冻结顺序收口。预注册 exhaustion H1 在所有可执行 primary/sensitivity/replication contrasts 上被反驳。
- **唯一下一步：M6 — Representation Decision。** 本轮不执行 M6；M5 outcome 与 Holdout 不得重新打开。

---

## M0–M3 — 已完成基础工程

组件始终是 Layer 2 趋势状态识别组件，不是交易策略。M2 冻结三桶数学，M3 将其绑定到 DataHub Layer-1 V3 wall-clock views；不同周期独立并存，不产生 `global_state`，不本地 resample，也不输出交易动作。

## M4 — 五桶实验协议冻结（PASS）

预注册 H1：同 interval/同方向下，extreme absolute slope state 可能比 moderate trend state 更难持续、更容易衰减/反转。

冻结：`T1=2.0`、primary `T2=4.0`、sensitivity `T2=3/5`、Development/Validation/Holdout split、episode-entry unit、1/3/5/10/20 bar horizons、5-bar directional-survival primary、样本门槛、ISO-week bootstrap 5000、8 项 Holm family、`<=-5pp` practical guard 与 holdout unlock rule。

机器合同：`docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json`。

---

## M5 — 极端斜率持续性实证（PASS / COMPLETE）

机器 closeout：`docs/governance/TREND_M5_CLOSEOUT_V1.json`。

### M5-1 — Source / Profile Admission

当前 active exact source 只准入两指数的 `trend_1m_official_v1` 与 `trend_5m_offset0_v1`。15m/60m anchors 与 phase profiles 均 `NOT_ADMITTED`；禁止 local resampling、offset substitution 或 legacy promotion。

### M5-2 — Development Sample Adequacy

Development=`2020-07-23`–`2022-12-30`。两 carrier 的 admitted 1m/5m strong/moderate episode 样本量均超过预注册门槛。该步骤只验证可执行性，不产生 H1 结论。

### M5-3 — Pre-Validation Seal

M4/M5 contracts、M2/M3 核心计算、Layer-1 clock、market-data reader、data manifest、DataHub source identity 与 Development artifact 均在 Validation 前通过 Git blob/SHA 封存。

### M5-4 — CSI1000 Primary `T2=4`

`000852.SH` Validation=`2023-01-03`–`2024-12-31`，admitted 1m/5m：

| interval | direction | survival Strong−Moderate | 95% CI | reversal10 Strong−Moderate |
|---|---|---:|---|---:|
| 1m | UP | +0.3853 | [+0.3734,+0.3969] | -0.2476 |
| 1m | DOWN | +0.3795 | [+0.3681,+0.3908] | -0.2507 |
| 5m | UP | +0.3822 | [+0.3531,+0.4119] | -0.2371 |
| 5m | DOWN | +0.3673 | [+0.3388,+0.3948] | -0.2360 |

四个 primary contrasts 的 survival 方向均显著与 H1 相反，正式 headline：**`H1_CONTRADICTED_ON_ALL_EXECUTABLE_PRIMARY_CONTRASTS`**。

### M5-5 — Predeclared `T2=3/5` Sensitivity

同一 CSI1000 Validation、同一 admitted 1m/5m source/profile identities：

- `T2=3` 四个 survival contrasts：`+0.4045 / +0.4110 / +0.4095 / +0.4147`，CI 全部严格大于 0；
- `T2=5` 四个 contrasts：`+0.3572 / +0.3459 / +0.3477 / +0.3382`，CI 全部严格大于 0；
- 8/8 = `SENSITIVITY_H1_CONTRADICTED`，0/8 朝 H1 方向；
- reversal10 也全部为负。

所以 primary 反证不是 `T2=4` 单阈值偶然。

### M5-6 — STAR50 Cross-Carrier Replication

STAR50 `000688.SH`，相同 Validation、primary `T2=4`，仅 admitted 1m/5m：

| interval | direction | survival Strong−Moderate | 95% CI | reversal10 Strong−Moderate |
|---|---|---:|---|---:|
| 1m | UP | +0.3735 | [+0.3621,+0.3850] | -0.2504 |
| 1m | DOWN | +0.3727 | [+0.3608,+0.3845] | -0.2090 |
| 5m | UP | +0.3730 | [+0.3416,+0.4042] | -0.2620 |
| 5m | DOWN | +0.3394 | [+0.3141,+0.3640] | -0.1923 |

4/4 replication contrasts 均 `REPLICATION_H1_CONTRADICTED`，0 个相反；正式 replication 状态：**`CLEAR_QUALITATIVE_REPLICATION_OF_PRIMARY_CONTRADICTION`**。STAR50 与 CSI1000 没有 pooling。

### M5 最终 Gate

最终证据只覆盖**已准入 1m/5m exact views**，但在以下三层全部一致：

1. CSI1000 primary `T2=4`；
2. CSI1000 predeclared `T2=3/5` sensitivity；
3. STAR50 independent `T2=4` replication。

综合结论：原“extreme slope 更容易耗竭”的 H1 被稳健反驳；extreme absolute slope 反而是**persistence/strength descriptor** 的候选语义。5-bar direction-adjusted return 没有同等稳定证据，因此不得把 persistence 差异直接翻译成收益或交易规则。

未执行且保持 fail closed：15m/60m anchors、phase profiles。2025 Holdout 从未打开，因为 primary support rule 未通过。所有 one-shot outcome jobs 均 consumed，M5 outcome work 不得重开。

---

## M6 — 三桶 / 五桶 / 连续强度表示裁决（唯一下一步）

M6 只能基于 M5 已封存证据，在以下方案中做产品语义选择：

1. **三桶 + 连续 strength**；
2. **正式五桶**；
3. **三桶主状态 + 五桶诊断/研究扩展**。

M6 不得重新调 `T2`、重跑 M5、打开 Holdout，也不得把状态映射成 BUY/SELL/position。M6 完成后才进入 M7。

## M7 — 稳定 Consumer API 与测试

实现 `symbol + as_of + bar_interval/profile` 的只读 consumer、snapshot store、expiry/no-fallback 与 conformance tests。

## M8 — 策略匹配与集成验证

趋势组件只描述趋势状态/强度；上层策略决定如何与风险状态组合并映射交易动作。

## M9 — 发布、版本与治理

形成稳定 schema、API 示例、profile 清单、证据追踪、changelog/migration 与 CI 治理。

---

## 全程不变原则

1. **组件不是策略。**
2. **状态必须绑定时间尺度/profile/version。**
3. **强度先连续、分桶后验证。**
4. **负结果允许；禁止调参救结论。**
