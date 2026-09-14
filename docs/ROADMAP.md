# 趋势状态识别组件路线图

> 本路线图定义未来工作的**执行顺序**。它不是收益研究结论，也不把任何尚未验证的假设写成策略规则。
>
> 执行纪律：**一次会话只推进当前里程碑；未通过当前 Gate，不自动进入下一阶段。** 历史研究证据保持原样，不用新定位重写旧结果。

## 当前进度

- **M0 — PASS**：产品定位、白皮书与路线图已落库。
- **M1 — PASS**：完成参考 consumer 审计，冻结 [API 合同](API_CONTRACT.md) 并形成 [Gap List](API_GAP_ANALYSIS.md)。
- **M2 — PASS**：冻结 [三桶趋势状态基线](THREE_BUCKET_BASELINE.md)：20-bar log-close OLS signed slope t-score，`T1=2.0`，completed-bar/as-of 与 fail-closed。
- **M3 — PASS**：完成多 K 线级别参数化，首批 admission 为 `1m/5m/15m/60m`，绑定 10 个 DataHub Layer-1 V3 profiles；完成 cadence/view/as-of 与多周期并存回归。
- **唯一下一步：M4**。M4 只冻结五桶实验协议，不读取/运行 M5 实证结果。

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
- 组件禁止自行选择“默认相位”，避免制造上游不存在的唯一默认。
- profile 与 interval 不匹配直接拒绝。

### 数学与阈值

所有首批 profile 继续复用：

- `lookback_bars=20`
- `T1=2.0`
- `log_close_ols_slope_t@1.0`

这不是声称 `T1=2.0` 已被证明对所有周期最优，而是避免在 M3 未经实证 Gate 就按周期调参。若未来需要不同阈值，必须升 profile/estimator 版本。

### Cadence / as-of admission

- `bar_end <= as_of` 且 `available_at <= as_of` 才 visible；
- visible row 的 `view_id` 必须匹配 profile；
- selected 20-bar window 的 Asia/Shanghai bar-end 必须落在 profile 的 immutable `close_times`；
- 同 session 内 cadence 必须连续；跨 session 时必须从当日最后 grid point 接到下一可见 session 的第一 grid point；
- 缺口返回 `UNAVAILABLE / CADENCE_GAP`；
- 错误时钟返回 `UNAVAILABLE / OFF_PROFILE_GRID`；
- 不插值、不 forward-fill、不本地 resample；
- 未来错误 view 不得污染更早 `as_of`。

完整交易日是否因节假日/整日数据缺失而缺席，不能仅靠 Layer-2 时间戳猜测；最终由 Layer-1 provider/receipt admission 负责跨交易日完整性。

### 多周期并存

`measure_multi_interval_trend_regimes_as_of(...)` 只返回独立 `measurements[]`，顶层故意没有 `state/global_state`。例如同一时刻 `1m=DOWN, 5m=SIDEWAYS, 15m=UP, 60m=UP` 完全合法；如何组合属于策略层。

### 实现与测试

- `src/factor_lab/market_state/trend_regime_profiles.py`
- `tests/test_trend_regime_profiles.py`
- schemas：`trend_regime_profile_registry@1.0`、`trend_regime_profile_measurement@1.0`、`trend_regime_multi_interval_measurement@1.0`

### Gate
**PASS。** 每个 admitted profile 绑定真实 Layer-1 V3 view；不存在隐式 resample/default phase；cadence 缺口 fail closed；多周期结果独立并存；M2 数学没有静默漂移；无交易/production authority。

---

## M4 — 五桶假设与实验协议冻结

### 目标
在不改变正式三桶基线的前提下，定义五桶候选并**先冻结检验协议，再看结果**。

设 `0 < T1 < T2`：

- `STRONG_DOWN`：`s < -T2`
- `DOWN`：`-T2 <= s < -T1`
- `SIDEWAYS`：`-T1 <= s <= T1`
- `UP`：`T1 < s <= T2`
- `STRONG_UP`：`s > T2`

### 核心假设 H1：极端斜率耗竭
非常高的绝对斜率可能比中等趋势斜率更难持续，更容易衰减、横盘或反转。`STRONG_UP/STRONG_DOWN` 可能是与普通趋势不同的末端/耗竭状态，而不是“更强的入场信号”。

即使 H1 成立，状态到买卖/仓位的映射仍属于策略层。

### M4 必须预注册

- `T2` 候选的选择方法与候选集合；
- 哪些 admitted M3 profiles 进入研究；
- development / validation / holdout 切分；
- forward horizons；
- 状态持续时间、下一状态转移概率、方向延续率；
- reversal probability / time-to-first-reversal；
- forward adverse / favorable excursion；
- `T2` 稳健性；
- 样本量/最小事件数与停止条件；
- 负结果处理规则。

### Gate
协议必须在读取 M5 结果之前冻结；不得看到结果后改 `T2`、改 horizon、改样本切分或挑 profile 来救结论。

---

## M5 — 极端斜率持续性实证

### 目标
按 M4 预注册协议正式检验 H1。

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
4. **策略匹配在接口层解决。** 不为每个策略复制状态识别代码。
