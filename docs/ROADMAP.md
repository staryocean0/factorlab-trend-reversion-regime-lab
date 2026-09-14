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
- **M5 — IN PROGRESS**：M5-1 source/profile admission PASS（partial）；M5-2 Development adequacy PASS；M5-3 seal PASS；**M5-4 primary `T2=4` Validation 已执行一次并在全部可执行 primary contrasts 上得到 `H1_CONTRADICTED`**。
- **唯一下一步：M5-5 — 预注册 `T2=3/5` Validation sensitivity。** 它不能替代/救援 T2=4 headline；Holdout 保持锁定。

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

只读取 CSI1000 `000852.SH` Validation=`2023-01-03`–`2024-12-31`，只执行 admitted 1m/5m；15m/60m 仍 `NOT_ADMITTED` 并以 raw p=`1.0` 留在完整 8 项 Holm family。真实 run=`34814912150`。

Primary 5-bar directional survival 的 Strong-Moderate：

| interval | direction | contrast | 95% CI | 结论 |
|---|---|---:|---|---|
| 1m | UP | +0.3853 | [+0.3734,+0.3969] | H1_CONTRADICTED |
| 1m | DOWN | +0.3795 | [+0.3681,+0.3908] | H1_CONTRADICTED |
| 5m | UP | +0.3822 | [+0.3531,+0.4119] | H1_CONTRADICTED |
| 5m | DOWN | +0.3673 | [+0.3388,+0.3948] | H1_CONTRADICTED |

M4 H1 预测 contrast 为负；实际所有可执行 contrast 均显著为正，意味着 extreme slope state 的短期 directional survival 明显高于 moderate trend state。10-bar reversal secondary 同样是 Strong-Moderate 约 `-0.236` 至 `-0.251`，CI 全部低于 0，即 strong state 更少反转。

因此正式 headline：**`H1_CONTRADICTED_ON_ALL_EXECUTABLE_PRIMARY_CONTRASTS`**。这不是交易动作结论，也不等于已经决定最终采用五桶。

Primary support rule 未通过，所以 2025 protocol Holdout **不得解锁**。One-time primary Validation execution 已 consumed，二次运行被 CI 禁用。

### M5-5 — T2=3/5 Validation Sensitivity（唯一下一步）

只允许执行 M4 已预注册的 `T2=3.0 / 5.0` sensitivity，使用相同 Validation split 与同一 admitted 1m/5m source/profile identities。

约束：

- sensitivity 不能替代 T2=4 headline；
- 不能用更好看的 sensitivity 结果 rescue H1；
- 不能因此打开 Holdout；
- 不能改 split、profile、horizon、endpoint 或 sample floor；
- STAR50 replication 仍是后续独立步骤，不能池化。

### M5 后续

完成 M5-5 后，按冻结顺序报告 replication/可执行 robustness；Holdout 对本次 H1 support 路径保持关闭。M5 收口后才进入 M6 表示层裁决。

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
