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
- **M5 — IN PROGRESS**：M5-1 source/profile admission PASS（partial）；M5-2 Development sample adequacy PASS；**M5-3 Code/Config/Development Seal PASS**。
- **唯一下一步：M5-4 — primary `T2=4` Validation 一次。** Holdout 仍锁定；不得改 seal、协议、source/profile 或多重检验 family。

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

机器 receipt：`docs/governance/TREND_M5_SOURCE_PROFILE_ADMISSION_V1.json`。

### M5-2 — Development Pipeline + Sample Adequacy（PASS）

只读取 `2020-07-23`–`2022-12-30`，真实 run `34812469153`。四个 admitted carrier/profile 的 strong/moderate 5-bar episode-entry 数均远高于 100，10/20-bar secondary 可用量均高于 50。

该 Gate 只说明 Development 样本量不构成明显阻塞；没有读取 Validation/Holdout，也没有计算 H1 outcome。

机器 receipt：`docs/governance/TREND_M5_DEVELOPMENT_ADEQUACY_V1.json`。

### M5-3 — Code / Config / Development Seal（PASS）

机器 seal：`docs/governance/TREND_M5_DEVELOPMENT_SEAL_V1.json`。

已在任何 Validation outcome 出现前固定：

1. M5-2 entrypoint/core 的 Git blob；
2. M2 slope baseline、M3 profile registry、Layer-1 clock contract、market-data reader 的 Git blob；
3. M4 protocol、M5-1 admission、M5-2 Development receipt 的 Git blob；
4. `data/manifest.json` Git blob；
5. DataHub export identity 与 `1m_official` / `5m_offset_0` source SHA256；
6. Development run/head/artifact digest；
7. historical replay clock contract；
8. Validation/Holdout 未读状态。

`tests/test_m5_development_seal.py` 使用 `git hash-object` 对 sealed paths 做 byte-identity guard；修改 sealed code/config 将直接使 CI 失败。

M5-3 **没有运行 Validation**，没有产生 survival/reversal/return/bootstrap/p-value 或 H1 adjudication。

### M5-4 — Primary Validation（唯一下一步）

只允许：

- primary `T2=4.0`；
- Validation=`2023-01-03`–`2024-12-31`；
- 只执行已 admitted 的 1m/5m anchors；
- 15m/60m 保持 `NOT_ADMITTED`，不得补造；
- M4 planned primary family 仍为 **8 contrasts = 4 intervals × 2 directions**；15m/60m 的 4 个不可执行 contrast 按预注册规则 `p=1.0`，Holm family size 仍为 8，禁止 admission 后缩小 family；
- Validation 只运行一次；
- Holdout 继续锁定。

### M5 后续冻结顺序

- M5-5：预注册 `T2=3/5` Validation sensitivity，不得替代 primary；
- 只有 primary Validation 满足 M4 support rule 才可解锁 primary `T2=4` holdout；
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
