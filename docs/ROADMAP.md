# 趋势状态识别组件路线图

> 本路线图定义未来工作的执行顺序。它不是收益研究结论，也不把尚未验证的假设写成策略规则。
>
> 执行纪律：**一次会话只推进当前里程碑/冻结子步骤；未通过当前 Gate，不自动进入下一阶段。**

## 当前进度

- **M0 — PASS**：产品定位、白皮书与路线图。
- **M1 — PASS**：consumer 审计、API 合同与 Gap List。
- **M2 — PASS**：冻结 20-bar log-close OLS signed slope t-score 三桶基线，`T1=2.0`。
- **M3 — PASS**：冻结 `1m/5m/15m/60m` versioned profile registry、view/cadence/as-of 边界。
- **M4 — PASS**：结果前冻结五桶实验协议。
- **M5 — IN PROGRESS**：M5-1 admission PASS（partial）；M5-2 Development adequacy PASS；M5-3 seal PASS；M5-4 primary `T2=4` Validation 得到全部可执行 contrasts `H1_CONTRADICTED`；**M5-5 `T2=3/5` sensitivity 也在 8/8 可执行 sensitivity contrasts 上继续反驳 H1**。
- **唯一下一步：M5-6 — cross-carrier replication / remaining robustness reporting。** 不得池化 rescue，不得读取 Holdout，不得补造未准入 phase profiles。

---

## M0–M3 — 已完成基础工程

组件定位始终是 Layer 2 趋势状态识别，不是交易策略。M2 冻结三桶数学，M3 将其绑定到 DataHub Layer-1 V3 wall-clock views；多周期结果独立并存，不产生 `global_state`，不本地 resample，也不输出交易动作。

---

## M4 — 五桶实验协议冻结（PASS）

H1：同 interval/同方向下，极端绝对斜率状态可能比中等趋势状态更难持续、更易衰减或反转。

冻结：`T1=2.0`、primary `T2=4.0`、sensitivity `3/5`、Development/Validation/Holdout split、4 个 anchor intervals、episode-entry 单位、1/3/5/10/20 bar horizons、primary directional-survival endpoint、样本门槛、week-cluster bootstrap 5000、Holm FWER、`<=-5pp` practical guard 与 holdout unlock。

机器合同：`docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json`。

---

## M5 — 极端斜率持续性实证（IN PROGRESS）

### M5-1 — Source / Profile Admission（PASS，partial）

当前 active exact source 只准入两指数的 `trend_1m_official_v1` 与 `trend_5m_offset0_v1`。15m/60m anchors 与 phase-sensitivity profiles 当前 `NOT_ADMITTED`；禁止 local resample、offset substitution 或 legacy 文件补齐。

### M5-2 — Development Pipeline + Sample Adequacy（PASS）

只读取 `2020-07-23`–`2022-12-30`；已准入 1m/5m 的 strong/moderate episode 样本量均高于预注册门槛。该 Gate 只证明样本量无明显阻塞。

### M5-3 — Code / Config / Development Seal（PASS）

`docs/governance/TREND_M5_DEVELOPMENT_SEAL_V1.json` 在 Validation 前冻结计算、source、profile、数据与 Development artifact identities，并以 Git blob guard 防止静默漂移。

### M5-4 — Primary T2=4 Validation（PASS：执行完成，H1 被反驳）

机器结果：`docs/governance/TREND_M5_PRIMARY_VALIDATION_V1.json`。

CSI1000 `000852.SH` Validation=`2023-01-03`–`2024-12-31`，admitted 1m/5m 四个 primary 5-bar directional-survival Strong-Moderate contrast 为 `+0.3673` 至 `+0.3853`，95% CI 全部严格大于 0；10-bar reversal contrast 为 `-0.2360` 至 `-0.2507`，CI 全部严格小于 0。

正式 headline：**`H1_CONTRADICTED_ON_ALL_EXECUTABLE_PRIMARY_CONTRASTS`**。Primary support rule 未通过，因此 2025 Holdout 不得解锁；one-shot primary job 已 consumed 并禁止 rerun。

### M5-5 — T2=3/5 Validation Sensitivity（PASS：反证对阈值稳健）

机器结果：`docs/governance/TREND_M5_T2_SENSITIVITY_V1.json`。真实 run=`34816576915`。

Sensitivity 仍只使用同一 CSI1000 Validation 与 admitted 1m/5m，不建立新 primary family，也不允许 headline replacement。

`T2=3` 的 4 个 survival Strong-Moderate contrasts 为：

- 1m UP `+0.4045`，95% CI `[+0.3903,+0.4179]`；
- 1m DOWN `+0.4110`，95% CI `[+0.4005,+0.4220]`；
- 5m UP `+0.4095`，95% CI `[+0.3805,+0.4400]`；
- 5m DOWN `+0.4147`，95% CI `[+0.3864,+0.4432]`。

`T2=5` 的 4 个 contrasts 为：

- 1m UP `+0.3572`，95% CI `[+0.3436,+0.3711]`；
- 1m DOWN `+0.3459`，95% CI `[+0.3329,+0.3587]`；
- 5m UP `+0.3477`，95% CI `[+0.3179,+0.3781]`；
- 5m DOWN `+0.3382`，95% CI `[+0.3098,+0.3673]`。

因此 **8/8 sensitivity contrasts = `SENSITIVITY_H1_CONTRADICTED`，0/8 朝 H1 方向**。10-bar reversal 也全部保持 Strong-Moderate 为负约 `-0.200` 至 `-0.285`。说明原 exhaustion H1 的反证并非 `T2=4` 单点阈值现象。

M5-5 不能替代 primary headline，也不能打开 Holdout；one-shot sensitivity job 已 consumed，rerun 将被 CI 禁止。

### M5-6 — Cross-carrier Replication / Remaining Robustness（唯一下一步）

按 M4 step 7，只允许做剩余独立 replication/reporting：

- STAR50 `000688.SH` 独立报告，不能与 CSI1000 池化；
- 只使用 M5-1 admitted 的 1m official / 5m offset0 exact views；
- replication headline 仍围绕 frozen primary `T2=4`，不能改变 CSI1000 headline；
- phase-sensitivity profiles 继续 `NOT_ADMITTED`，除非存在 current active exact-view receipt；
- 不读取 2025 Holdout；
- replication 即使方向不同，也只能作为外部一致性信息，不能 rescue 原 H1。

M5-6 完成后收口 M5，再进入 M6 表示层裁决。

---

## M6 — 三桶 / 五桶 / 连续强度架构裁决

允许：1) 三桶 + 连续强度；2) 正式五桶；3) 三桶主状态 + 五桶研究/诊断扩展。M5 完成前不得进入 M6。

## M7 — 稳定 Consumer API 与测试

实现 `symbol + as_of + bar_interval/profile` 的只读 consumer、snapshot store、expiry/no-fallback 与 conformance tests。

## M8 — 策略匹配与集成验证

趋势组件只描述趋势状态/强度；策略层决定如何与风险状态组合并映射交易动作。

## M9 — 发布、版本与治理

形成稳定 schema、API 示例、profile 清单、证据追踪、changelog/migration 与 CI 治理。

---

## 全程不变原则

1. **组件不是策略。**
2. **状态必须绑定时间尺度/profile/version。**
3. **强度先连续、分桶后验证。**
4. **负结果允许；禁止调参救结论。**
