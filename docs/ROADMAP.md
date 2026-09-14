# 趋势状态识别组件路线图

> 本路线图定义未来工作的**执行顺序**。它不是收益研究结论，也不把任何尚未验证的假设写成策略规则。
>
> 执行纪律：**一次会话只推进当前里程碑；未通过当前 Gate，不自动进入下一阶段。** 历史研究证据保持原样，不用新定位重写旧结果。

## 当前进度

- **M0 — PASS**：产品定位、白皮书与路线图已落库。
- **M1 — PASS**：完成参考 consumer 审计，冻结 [API 合同](API_CONTRACT.md) 并形成 [Gap List](API_GAP_ANALYSIS.md)。
- **M2 — PASS**：冻结 [三桶趋势状态基线](THREE_BUCKET_BASELINE.md)：20-bar log-close OLS signed slope t-score，`T1=2.0`，completed-bar/as-of 与 fail-closed。
- **M3 — PASS**：完成多 K 线级别参数化，首批 admission 为 `1m/5m/15m/60m`，绑定 10 个 DataHub Layer-1 V3 profiles；完成 cadence/view/as-of 与多周期并存回归。
- **M4 — PASS**：五桶实验协议已在任何 M5 outcome 计算之前冻结，详见 [M4 协议](governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.md) 与 [机器合同](governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json)。
- **唯一下一步：M5**。M5 只能按 M4 冻结协议执行，不允许先看结果再改阈值、切分、profile、horizon 或样本门槛。

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

### 已冻结基线

详细规格见 `docs/THREE_BUCKET_BASELINE.md`。`trend_regime_three_bucket_baseline@1.0`：

- `log(close)`；
- 最近 20 根已结束且已可用 bar；
- log-close OLS signed slope t-score 为唯一三桶 authority；
- `T1=2.0`；
- `DOWN: s<-2`；`SIDEWAYS: -2<=s<=2`；`UP: s>2`；
- 缺失/坏 close、少于 20 根均 fail closed；
- future/unpublished bar 不影响较早 `as_of`；
- BDCI/DII 等只作诊断，不参与主状态投票。

### Gate
**PASS。** 同输入、同版本、同 `as_of` 结果唯一可重复；无未来数据泄漏；参数不可在 `@1.0` 内静默漂移。

---

## M3 — 多 K 线级别参数化（PASS）

### 核心决定

M3 不重新调 M2 数学，而是把 M2 measurement 绑定到 DataHub 已登记的 Layer-1 V3 wall-clock views。稳定查询坐标变为：

```text
bar_interval + profile_id + as_of
```

其中 `profile_id` 代表同一 K 线周期下的具体 wall-clock 相位/view。FactorLab 不在本层自己 resample K 线。

### 首批 admitted intervals / profiles

- `1m`：`trend_1m_official_v1` → `1m_official`
- `5m`：`trend_5m_offset0_v1` … `trend_5m_offset4_v1` → `5m_offset_0` … `5m_offset_4`
- `15m`：`trend_15m_offset5_v1` / `trend_15m_offset10_v1`
- `60m`：`trend_60m_offset30_v1` / `trend_60m_offset45_v1`

合计 10 个 versioned profiles。

### Profile 选择规则

- 只有一个 admitted view 的 interval 可省略 `profile_id`；当前只有 `1m` 满足。
- `5m/15m/60m` 存在多个合法 view，必须显式指定 `profile_id`。
- 组件禁止自行选择“默认相位”。
- profile 与 interval 不匹配直接拒绝。

### 数学与阈值

所有首批 profile 继续复用 `lookback_bars=20`、`T1=2.0`、`log_close_ols_slope_t@1.0`。这不是声称该阈值对所有周期最优，而是避免未经实证 Gate 就按周期调参。

### Cadence / as-of admission

- `bar_end <= as_of` 且 `available_at <= as_of` 才 visible；
- visible row 的 `view_id` 必须匹配 profile；
- selected 20-bar window 必须落在 profile immutable `close_times`；
- 缺口 `CADENCE_GAP`，错误时钟 `OFF_PROFILE_GRID`；
- 不插值、不 forward-fill、不本地 resample；
- 多周期结果独立并存，顶层无 `global_state`。

### Gate
**PASS。** 每个 admitted profile 绑定真实 Layer-1 V3 view；不存在隐式 resample/default phase；cadence 缺口 fail closed；M2 数学没有静默漂移。

---

## M4 — 五桶假设与实验协议冻结（PASS）

### 核心假设 H1
极端绝对斜率可能比中等趋势斜率更难持续，更容易衰减、横盘或反转。该假设不包含任何交易动作语义。

### 已冻结协议

机器合同：`trend_five_bucket_protocol_m4@1.0`。

- `T1=2.0` 保持不变；主 `T2=4.0`；敏感性仅 `T2=3.0/5.0`；
- primary carrier=`000852.SH`，replication=`000688.SH`，禁止池化 rescue；
- 公共历史窗口 `2020-07-23`–`2025-12-31`；
- Development=`2020-07-23`–`2022-12-30`；
- Validation=`2023-01-03`–`2024-12-31`；
- locked historical holdout=`2025-01-02`–`2025-12-31`，明确不是 fresh OOS；
- 每个 interval 的研究 anchor 用最小 session offset 机械选择：1m official、5m offset0、15m offset5、60m offset30；其余 M3 profiles 只做 phase sensitivity；
- source/profile 不满足 M3 identity/receipt admission 时记 `NOT_ADMITTED`，禁止本地 resample 或替代；
- 统计单位为五桶 state episode entry，不把每根 bar 当独立样本；
- horizons=`1/3/5/10/20 bars`，primary horizon=5，primary reversal horizon=10；
- primary endpoint=`5-bar directional survival`，比较 `Strong-Moderate`，H1 预测负值；
- secondary confirmatory=`10-bar reversal probability` 与 `5-bar direction-adjusted return`；
- 预注册 duration、transition、time-to-first-reversal、MFE/MAE 等描述指标；
- validation 主指标每组至少 100 episodes，holdout 每组至少 50；不足即 `UNDERPOWERED`，不得降 T2 或池化制造 power；
- week-cluster bootstrap 5000 次，seed=`20260914`，95% CI；
- primary family 固定为 `4 anchor intervals × 2 directions = 8`，Holm FWER `alpha=0.05`；
- practical guard：primary survival contrast 必须 `<=-5pp`；
- validation 未通过不得解锁 holdout；T2=3/5 不能替代 T2=4 headline；
- 负结果允许为 `H1_NOT_SUPPORTED / INCONCLUSIVE_UNDERPOWERED / H1_CONTRADICTED / NOT_ADMITTED`。

### M4 本轮明确没有做

没有计算 forward return、transition/reversal probability、五桶 episode 数量、MFE/MAE，也没有读取 holdout outcome。因此 M4 没有产生任何新的五桶市场证据。

### Gate
**PASS。** 协议已在 M5 outcome 之前冻结，并有机器可读合同与 CI invariant tests；M5 不能通过事后换参数、样本、profile、horizon 或门槛来救结论。

---

## M5 — 极端斜率持续性实证

### 目标
严格按 M4 冻结协议正式检验 H1。

### 固定执行纪律
1. 先做 source/profile admission，不计算 outcome；
2. 仅在 development 做管线与样本充足性检查；
3. 封存代码/config/development receipt；
4. 主 `T2=4` validation 只运行一次；
5. 再运行预注册 `T2=3/5` sensitivity，不改 primary；
6. 只有 validation 通过预注册支持规则才解锁 holdout；
7. replication 与 phase sensitivity 不得改写 primary。

### Gate
只有极端桶相对普通趋势桶出现稳定、可复现且有实际量级的差异，五桶才进入候选产品语义；否则保留三桶或连续强度。

---

## M6 — 三桶 / 五桶 / 连续强度架构裁决

允许的正式裁决：
1. 三桶 + 连续强度；
2. 正式五桶；
3. 三桶主状态 + 五桶研究/诊断扩展。

裁决必须跨周期/样本具有解释力，不能只因为样本内更好看。

---

## M7 — 稳定 Consumer API 与测试

目标：把已裁决状态模型封装成 `symbol + as_of + bar_interval/profile` 的稳定只读 consumer；缺失/过期不回退，schema/version 固定，并有 prefix-causality/兼容测试。

---

## M8 — 策略匹配与集成验证

趋势组件只回答状态/强度；风险组件回答风险属性；具体策略组合两者并决定交易动作。至少两个不同持仓周期的调用者应能复用同一组件而无需复制代码。

---

## M9 — 发布、版本与治理

形成稳定 schema、API 示例、profile 清单、证据追踪、changelog/migration 与 CI/文档一致性治理。

---

## 全程不变的四条原则

1. **组件不是策略。** 不直接给买卖、仓位或订单。
2. **参数决定语境。** 状态必须绑定 K 线级别/配置版本。
3. **强度先连续、分桶后验证。** 五桶不能因为直觉合理就提前获得产品语义。
4. **策略匹配在接口层解决。** 不为每个策略复制状态识别代码；策略选择 profile，组件返回有版本的状态描述。
