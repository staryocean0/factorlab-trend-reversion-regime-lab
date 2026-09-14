# 趋势状态识别组件路线图

> 本路线图定义未来工作的**执行顺序**。它不是收益研究结论，也不把任何尚未验证的假设写成策略规则。
>
> 执行纪律：**一次会话只推进当前里程碑/当前冻结子步骤；未通过当前 Gate，不自动进入下一阶段。** 历史研究证据保持原样，不用新定位重写旧结果。

## 当前进度

- **M0 — PASS**：产品定位、白皮书与路线图已落库。
- **M1 — PASS**：完成参考 consumer 审计，冻结 [API 合同](API_CONTRACT.md) 并形成 [Gap List](API_GAP_ANALYSIS.md)。
- **M2 — PASS**：冻结 [三桶趋势状态基线](THREE_BUCKET_BASELINE.md)：20-bar log-close OLS signed slope t-score，`T1=2.0`，completed-bar/as-of 与 fail-closed。
- **M3 — PASS**：完成多 K 线级别参数化，首批 profile registry 为 `1m/5m/15m/60m` 共 10 个 Layer-1 V3 profiles。
- **M4 — PASS**：五桶实验协议已在任何 M5 outcome 计算之前冻结，详见 [M4 协议](governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.md) 与 [机器合同](governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json)。
- **M5 — IN PROGRESS**：**M5-1 source/profile admission 已 PASS（partial admission）**。两指数的 1m official 与 5m offset0 已准入；15m/60m anchors 及 phase-sensitivity profiles 因缺少 current active exact-view receipt 而 fail closed。详见 [M5-1 receipt](governance/TREND_M5_SOURCE_PROFILE_ADMISSION_V1.md)。
- **唯一下一步：M5-2**。只允许 Development pipeline + sample-adequacy checks；Validation 与 Holdout 仍锁定。

---

## M0 — 定位与路线图（PASS）

### 目标
把仓库从“可能被误解为一套趋势/反转交易策略”校正为：**供上层策略调用的趋势状态识别组件**。

### Gate
- 组件不是策略，不直接输出买卖、仓位、订单。
- 同一时刻在不同 K 线级别可有不同状态。
- 五桶只是待验证研究假设。

---

## M1 — 参考组件审计与接口合同（PASS）

### 已完成
- `docs/API_CONTRACT.md`：冻结 `regime_state_consumer_v1` 的调用 envelope、as-of/expiry/no-fallback、snapshot/provenance、authority 与参数所有权。
- `docs/API_GAP_ANALYSIS.md`：measurement plane 到稳定 trend consumer 的 gap list。
- 确认 `timing_layer2_measurement_plane.py` 是 measurement authority 根，不另建平行 Layer 2。
- capability registry 的历史 asset/source ref 不自动等于当前可执行 provider，必须 admission/fail-closed。

### Gate
**PASS。** 接口在不知道任何具体策略逻辑时也能独立成立，且不含交易动作语义。

---

## M2 — 三桶基线冻结与可复现性（PASS）

`trend_regime_three_bucket_baseline@1.0` 冻结：`log(close)`、最近 20 根 completed/available bar、log-close OLS signed slope t-score、`T1=2.0`，并对缺失/坏值/future data fail closed。BDCI/DII 等只作诊断。

### Gate
**PASS。** 同输入、同版本、同 `as_of` 结果唯一可重复；无未来数据泄漏；参数不可在 `@1.0` 内静默漂移。

---

## M3 — 多 K 线级别参数化（PASS）

M3 把 M2 measurement 绑定到 DataHub Layer-1 V3 wall-clock views，调用坐标为 `bar_interval + profile_id + as_of`。Registry 包含：1m×1、5m×5、15m×2、60m×2。所有 profile 继续复用 `lookback=20 / T1=2.0 / log_close_ols_slope_t@1.0`；不本地 resample；cadence/view 错误 fail closed；多周期结果独立并存，无 `global_state`。

### Gate
**PASS。** profile/view/cadence/as-of 边界已冻结且不含交易语义。

---

## M4 — 五桶假设与实验协议冻结（PASS）

H1：同 interval/同方向下，极端绝对斜率状态可能比中等趋势状态更难持续、更易衰减或反转。

机器合同 `trend_five_bucket_protocol_m4@1.0` 冻结：

- `T1=2.0`；primary `T2=4.0`；sensitivity=`3.0/5.0`；
- primary carrier=`000852.SH`；replication=`000688.SH`；禁止池化 rescue；
- Development=`2020-07-23`–`2022-12-30`；Validation=`2023-01-03`–`2024-12-31`；locked historical holdout=`2025-01-02`–`2025-12-31`；
- anchors：1m official、5m offset0、15m offset5、60m offset30；
- source/profile 不满足 exact view + causal receipt 就 `NOT_ADMITTED`；禁止 resample/substitution；
- episode-entry 统计单位；horizons 1/3/5/10/20；primary endpoint=5-bar directional survival；
- week-cluster bootstrap 5000、Holm FWER、样本门槛与 holdout unlock 规则均冻结。

M4 未计算任何 forward outcome。

### Gate
**PASS。** 评价口径已在 M5 outcome 之前锁定。

---

## M5 — 极端斜率持续性实证（IN PROGRESS）

### M5-1 — Source / Profile Admission（PASS，partial admission）

机器 receipt：`docs/governance/TREND_M5_SOURCE_PROFILE_ADMISSION_V1.json`。

已确认当前 active cross-index source 为 DataHub `factorlab_unified_index_kline_v3_20260824` 的受限历史 archive，并冻结历史 `available_at` 语义：raw historical retrieval time 只作 provenance；M5 causal replay 的 completed-bar runtime visibility 使用 `runtime_available_at = bar_end`，该映射依据已冻结的数据所有者澄清，不声称测得真实 feed latency。

Anchor 裁决：

| carrier | 1m official | 5m offset0 | 15m offset5 | 60m offset30 |
|---|---|---|---|---|
| `000852.SH` | ADMITTED | ADMITTED | NOT_ADMITTED | NOT_ADMITTED |
| `000688.SH` | ADMITTED | ADMITTED | NOT_ADMITTED | NOT_ADMITTED |

原因：当前 active cross-index catalog 对两指数存在完整的 exact `1m_official` / `5m_offset_0` lineage 与 2020-07-23–2025-12-31 覆盖；15m/60m 只有 legacy/旧研究 exact files，没有 current active exact-view receipt。所有 phase-sensitivity profiles 当前也保持 `NOT_ADMITTED`。

本裁决没有删除 M4 planned hypotheses，也没有修改 T2/horizon/split。Legacy 文件没有因为“存在”而自动获得新研究准入。

M5-1 明确未计算：五桶 episode counts、survival、forward returns、transition/reversal、MFE/MAE、Validation/Holdout outcomes。

### M5-2 — Development Pipeline + Sample Adequacy（唯一下一步）

只允许对已 admitted 的 `1m/5m` anchors：

1. 建立冻结 M4 五桶 development pipeline；
2. 检查 source/profile/cadence 与 split 边界；
3. 计算 Development 样本充足性；
4. 封存 code/config/development receipt。

**M5-2 仍不得读取 Validation outcome。** 15m/60m 不得通过本地 resample、换 offset、池化 carrier 来补齐。

### 后续仍被冻结的顺序

只有 M5-2 封存后，才可能进入 primary `T2=4` Validation；Validation 后才运行预注册 sensitivity；只有 Validation 满足 M4 support rule 才允许解锁 Holdout。

### M5 最终 Gate
只有极端桶相对普通趋势桶出现稳定、可复现且有实际量级的差异，五桶才进入候选产品语义；否则保留三桶或连续强度。

---

## M6 — 三桶 / 五桶 / 连续强度架构裁决

允许的正式裁决：1) 三桶 + 连续强度；2) 正式五桶；3) 三桶主状态 + 五桶研究/诊断扩展。M5 完成前不得进入 M6。

---

## M7 — 稳定 Consumer API 与测试

目标：把已裁决状态模型封装成 `symbol + as_of + bar_interval/profile` 的稳定只读 consumer；缺失/过期不回退，schema/version 固定，并有 prefix-causality/兼容测试。

---

## M8 — 策略匹配与集成验证

趋势组件只回答状态/强度；风险组件回答风险属性；具体策略组合两者并决定交易动作。

---

## M9 — 发布、版本与治理

形成稳定 schema、API 示例、profile 清单、证据追踪、changelog/migration 与 CI/文档一致性治理。

---

## 全程不变的四条原则

1. **组件不是策略。** 不直接给买卖、仓位或订单。
2. **参数决定语境。** 状态必须绑定 K 线级别/配置版本。
3. **强度先连续、分桶后验证。** 五桶不能因为直觉合理就提前获得产品语义。
4. **策略匹配在接口层解决。** 不为每个策略复制状态识别代码；策略选择 profile，组件返回有版本的状态描述。
