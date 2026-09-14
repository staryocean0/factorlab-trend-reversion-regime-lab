# 趋势状态识别组件路线图

> 本路线图定义未来工作的执行顺序。它不是收益研究结论，也不把尚未验证的假设写成策略规则。
>
> 执行纪律：**一次会话只推进当前里程碑/冻结子步骤；未通过当前 Gate，不自动进入下一阶段。**

## 当前进度

- **M0 — PASS**：产品定位、白皮书与路线图。
- **M1 — PASS**：consumer 审计、API 合同与 Gap List。
- **M2 — PASS**：冻结 20-bar log-close OLS signed slope t-score 三桶基线，`T1=2.0`。
- **M3 — PASS**：冻结 `1m/5m/15m/60m` versioned profile registry、view/cadence/as-of 边界。
- **M4 — PASS**：在任何 M5 outcome 前冻结五桶实验协议：primary `T2=4.0`、sensitivity `3/5`、split、anchors、endpoints、sample floors、bootstrap/Holm 与 holdout unlock。
- **M5 — IN PROGRESS**：M5-1 source/profile admission **PASS（partial）**；M5-2 Development sample adequacy **PASS**。
- **唯一下一步：M5-3 — seal code/config/Development receipt；不得运行 Validation。**

---

## M0–M3 — 已完成基础工程

组件定位始终是 Layer 2 趋势状态识别，不是交易策略。M2 冻结三桶数学，M3 将其绑定到 DataHub Layer-1 V3 wall-clock views；多周期结果独立并存，不产生 `global_state`，不本地 resample，也不输出交易动作。

---

## M4 — 五桶实验协议冻结（PASS）

核心 H1：同 interval/同方向下，极端绝对斜率状态可能比中等趋势状态更难持续、更易衰减或反转。

冻结要点：

- `T1=2.0`；primary `T2=4.0`；sensitivity=`3.0/5.0`；
- primary carrier=`000852.SH`，replication=`000688.SH`，禁止池化 rescue；
- Development=`2020-07-23`–`2022-12-30`；Validation=`2023-01-03`–`2024-12-31`；locked historical holdout=`2025-01-02`–`2025-12-31`；
- anchors：1m official、5m offset0、15m offset5、60m offset30；
- source/profile 不满足 exact view + causal receipt 就 `NOT_ADMITTED`；
- episode-entry 为统计单位；horizons 1/3/5/10/20；primary endpoint=5-bar directional survival；
- validation primary 每组至少 100 episodes，10/20-bar secondary 每组至少 50；
- week-cluster bootstrap 5000、Holm FWER、`<=-5pp` practical guard 与 holdout unlock 规则冻结。

机器合同：`docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json`。

---

## M5 — 极端斜率持续性实证（IN PROGRESS）

### M5-1 — Source / Profile Admission（PASS，partial）

当前 active exact source 只准入两指数的：

- `trend_1m_official_v1`
- `trend_5m_offset0_v1`

15m/60m anchors 与 phase-sensitivity profiles 当前 `NOT_ADMITTED`；不能用 local resample、offset substitution 或 legacy 文件补齐。

机器 receipt：`docs/governance/TREND_M5_SOURCE_PROFILE_ADMISSION_V1.json`。

### M5-2 — Development Pipeline + Sample Adequacy（PASS）

只读取 `2020-07-23`–`2022-12-30`，只运行已 admitted 的 1m/5m anchors。真实数据 run `34812469153`。

主 5-bar 完整 episode-entry 数：

| carrier/profile | UP moderate | UP strong | DOWN moderate | DOWN strong |
|---|---:|---:|---:|---:|
| `000852.SH / 1m` | 6012 | 3003 | 5912 | 2891 |
| `000852.SH / 5m` | 1157 | 549 | 1202 | 587 |
| `000688.SH / 1m` | 5805 | 2746 | 6319 | 3084 |
| `000688.SH / 5m` | 1105 | 546 | 1267 | 631 |

全部超过 primary floor=100；10/20-bar secondary 可用量全部超过 50。

该 Gate 只说明 **Development 样本量不构成明显阻塞**。没有读取 Validation/Holdout，没有计算 survival、reversal、returns、transition probability、MFE/MAE、bootstrap、p-value，也没有 adjudicate H1。

机器 receipt：`docs/governance/TREND_M5_DEVELOPMENT_ADEQUACY_V1.json`。

### M5-3 — Code / Config / Development Seal（唯一下一步）

目标：在任何 Validation outcome 出现之前，把后续正式检验所依赖的代码和身份完全封死。

必须封存：

1. M5 Development/Validation 共用计算代码的 Git blob/hash；
2. M4 protocol identity；
3. M5-1 source admission identity；
4. M5-2 Development artifact/run/dataset identity；
5. exact admitted carrier/profile/source identities；
6. `T1/T2/split/horizon/sample floor/bootstrap/Holm` 等配置 identity；
7. Validation 与 Holdout 仍为 locked 的状态。

**M5-3 不运行 Validation。** Seal PASS 后，后续会话才允许 primary `T2=4` Validation 一次。

### M5 后续冻结顺序

- M5-4：primary `T2=4` Validation 一次；
- M5-5：预注册 `T2=3/5` sensitivity，不得改 primary；
- 只有 Validation 满足 M4 support rule 才可解锁 holdout；
- replication / phase sensitivity 不得 rescue CSI1000 primary。

### M5 最终 Gate

只有极端桶相对普通趋势桶出现稳定、可复现且有实际量级的差异，五桶才进入候选产品语义；否则保留三桶或连续强度。

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
