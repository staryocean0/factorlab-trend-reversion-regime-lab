# 趋势状态识别组件路线图

> 本仓的 trend-regime 是 Layer 2 市场状态基础设施，不是交易策略。
>
> 原 M0–M9 已完成并冻结；2026-09-14 用户显式授权独立的 Post-V1 Cross-Profile Invariance & Calibration Study。后续研究不得静默改写 V1。

## 当前进度

- **M0–M9 — COMPLETE / PASS**：`factorlab.layer2.trend_regime@1.0.0` 稳定组件合同已冻结。
- **X1 — COMPLETE**：source/profile inventory。
- **X2 — COMPLETE**：两指数 × 10 exact views 的固定基线与预注册 sensitivity。
- **X3 — COMPLETE**：state-dynamics invariance；同 interval phase 较稳，60m carrier heterogeneity 明显。
- **X4 — `INSUFFICIENT_EVIDENCE`**：不修改 V1。
- **X5 — COMPLETE**：五指数 5m external replication。
- **X5B — COMPLETE**：5m Sina ↔ Eastmoney source robustness。
- **X5C — COMPLETE**：五指数 15m/60m 跨 carrier + 60m 长窗口；60m underpower 已解除，但 heterogeneity 持续。
- **X5D — COMPLETE / `INSUFFICIENT_EVIDENCE`**：静态 interval-specific T1 与静态 robust normalization 均未形成外部语义支配。
- **X5E — COMPLETE / NO ADOPTION**：60m temporal scale nonstationarity 得到支持；causal rolling normalization 强化 cross-carrier strength comparability，但没有同时建立 temporal stability 与 state-semantic non-inferiority。
- **X6 — HOLD / NOT READY**：不做 representation / SemVer 变更。

V1 release pointer `release/trend-regime-v1.0.0` 必须继续指向原 M9 gated commit `5a563d87d1628379e0d9a04aa7c5500bc30c4bc2`；Post-V1 研究提交不得移动它。

## V1 冻结表示

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

稳定入口：`query_regime(symbol, as_of, bar_interval, profile_id=None)`。

当前 runtime admission 仍只有两指数 `000852.SH` / `000688.SH` 的 `trend_1m_official_v1` 与 `trend_5m_offset0_v1`。其他 M3 profiles 继续 fail closed；Post-V1 public/legacy research source 不产生 runtime admission。

## 已建立的 Post-V1 结论

### Phase 与 5m

X2/X3 显示同一 interval 内 phase dispersion 总体较小，5m offset0–4 尤其稳定；跨 interval 差异明显大于 phase 差异。X5 五指数 5m 的 SIDEWAYS occupancy range ≈ **3.13pp**，one-step self-transition range ≈ **1.23–1.87pp**。X5B 中 Sina vs Eastmoney 的 slope_t Pearson ≈ **0.9999994**，三桶状态 **100% 一致**。目前没有证据支持 carrier-specific、phase-specific 或 provider-specific 5m T1。

## X5C — 15m / 60m Cross-Carrier — COMPLETE

Protocol：`docs/governance/TREND_X5C_15M_60M_CROSS_CARRIER_PROTOCOL_V1.json`  
Source receipt：`docs/governance/TREND_X5C_SINA_15M_60M_SOURCE_RECEIPT_V1.json`  
Result：`docs/governance/TREND_X5C_15M_60M_CROSS_CARRIER_RESULT_V1.json`

五指数 independent-source native-clock 研究：

- 15m：2026-06-17 至 2026-09-14，63 个完整交易日，每 carrier 989 measurements；
- 60m：2026-01-05 至 2026-09-14，170 个完整交易日，每 carrier 661 measurements；
- 旧 M4/M5 2025 Holdout 未读取；
- public native 15m/60m 不是 M3/DataHub exact profile identity，不改变 runtime admission。

固定 V1 `20-bar slope_t / T1=2`：

| 指标 | 15m 跨 carrier range | 60m 跨 carrier range |
|---|---:|---:|
| abs(slope_t) q90 | ≈ 1.26 | ≈ 3.37 |
| SIDEWAYS occupancy | ≈ 4.65pp | ≈ 12.41pp |
| DOWN survival5 | ≈ 7.80pp | ≈ 14.75pp |
| UP survival5 | ≈ 9.02pp | ≈ 10.44pp |

60m 所有预注册 directional metrics 的最小 origins = **181**，已超过 adequate threshold 100；早先的 60m UP underpower 不再是主要解释。

## X5D — Static Calibration Comparison — COMPLETE

Protocol：`docs/governance/TREND_X5D_INTERVAL_CALIBRATION_COMPARISON_PROTOCOL_V1.json`  
Calibration method：`docs/governance/TREND_X5D_DEVELOPMENT_CALIBRATION_METHOD_V1.json`  
Development receipt：`docs/governance/TREND_X5D_DEVELOPMENT_CALIBRATION_RECEIPT_V1.json`  
Result：`docs/governance/TREND_X5D_INTERVAL_CALIBRATION_COMPARISON_RESULT_V1.json`  
Decision update：`docs/governance/TREND_X4_POST_X5D_UPDATE_V1.json`

参数只使用 2020 Development exact-view 数据拟合；2026 五指数只用于外部 candidate evaluation，没有使用交易收益。Development 拟合得到 interval-specific `T1_60m≈1.2225`，primary median-abs normalization 等价 `T1_60m≈1.2701`。两种独立方法都说明 60m raw score scale 与短周期不同，但在 2026 外部样本上没有全面语义优势：interval-specific T1 为 **9 改善 / 7 恶化**，primary median-abs normalization 为 **10 改善 / 5 恶化 / 1 持平**；所有候选无严格 Pareto dominance，因此静态 calibration 不采纳。

## X5E — 60m Temporal Scale Stability & Causal Normalization — COMPLETE

Protocol：`docs/governance/TREND_X5E_60M_TEMPORAL_SCALE_CAUSAL_NORMALIZATION_PROTOCOL_V1.json`  
Result：`docs/governance/TREND_X5E_60M_TEMPORAL_SCALE_CAUSAL_NORMALIZATION_RESULT_V1.json`  
Decision update：`docs/governance/TREND_X4_POST_X5E_UPDATE_V1.json`

X5E 只研究表示层。没有计算收益、没有策略指标、没有扩大 runtime admission、没有修改 V1。研究只使用 X5C retained Sina native 60m 数据中的 **2026-01-05 至 2026-09-14** 行；旧 M4/M5 governed 2025 Holdout 未读取。候选严格 causal：在时点 `t` 的 scale 只能使用 `t-1` 及更早 slope_t，窗口预注册为 **40 / 80 / 120 measurements**。normalized semantic threshold 固定沿用 X5D 2020 Development 已封存值 `0.44780633341059867`，没有利用 2026 再拟合参数。

### X5E-1：60m temporal scale nonstationarity 得到支持

按月计算 `median(abs(slope_t))`，五指数 2026 月度最大/最小比：

- CSI1000：**2.50×**；
- STAR50：**2.76×**；
- CSI300：**3.32×**；
- CSI500：**1.61×**；
- SSE50：**1.63×**。

因此“一个静态 60m scale 在全年稳定”不受该窗口支持。

### X5E-2：causal normalization 很强地改善 cross-carrier strength scale

为公平比较，V1 与全部候选都限制在 120-score warmup 后的共同窗口 **2026-03-02 15:00 至 2026-09-14 15:00**，每 carrier **541 measurements**。

五指数 carrier-median strength 的横截面 range：

| 表示 | cross-carrier range | 相对 raw 降幅 |
|---|---:|---:|
| V1 raw `abs(slope_t)` | 1.4307 | — |
| causal median-abs 40 | 0.1052 | ≈ 92.7% |
| causal median-abs 80 | 0.0778 | ≈ 94.6% |
| causal median-abs 120 | 0.0573 | ≈ 96.0% |

所以 rolling causal scale 对 **cross-carrier strength-level alignment** 很有效。

### X5E-3：但 temporal stability 没有被解决

单 carrier 月度 median-strength 最大/最小比，在五指数之间取中位数：

```text
V1 raw              ≈ 1.694
causal medabs 40     ≈ 1.689
causal medabs 80     ≈ 2.056
causal medabs 120    ≈ 1.990
```

40-bar 几乎没有改善，80/120 反而更差。因此“cross-carrier scale 对齐”与“within-carrier temporal stability”是两个不同问题，不能混为一谈。

### X5E-4：动态 state-boundary normalization 仍有语义 trade-off

在事前定义的 8 个 60m cross-carrier state-semantic dispersion 指标上：

- causal median-abs 40：**5 改善 / 3 恶化**；
- causal median-abs 80：**3 改善 / 5 恶化**；
- causal median-abs 120：**5 改善 / 3 恶化**。

40/120 的恶化集中在 SIDEWAYS self-transition 与 DOWN/UP 的 opposite-entry10；没有任何候选严格 Pareto-dominates V1。候选相对 V1 改写约 **2.4%–12.8%** 的状态，但所有 carrier 的 DOWN↔UP opposite-direction disagreement 都为 **0**：变化只发生在 directional ↔ SIDEWAYS 边界，不改变 slope_t 的方向符号。

动态 raw-equivalent T1 也不是小幅微调。例如 40-bar 候选跨 carrier 的 q10/q90 极值约 **0.75–3.91**，进一步说明它是实质性的动态 representation change，而不是把固定 `T1=2` 略作修正。

### X5E 决策

```text
TEMPORAL_SCALE_NONSTATIONARITY       = SUPPORTED_ON_2026_FIVE_CARRIER_WINDOW
CAUSAL_STATE_BOUNDARY_NORMALIZATION  = NOT SUPPORTED FOR ADOPTION
CAUSAL_STRENGTH_SCALE_NORMALIZATION  = PROMISING CROSS-CARRIER DIAGNOSTIC
TEMPORAL_STABILITY_OF_NORMALIZATION  = NOT ESTABLISHED
V1_ACTION                            = NO CHANGE
X6                                  = HOLD / NOT READY
```

因此下一阶段如果继续，不应再让 rolling scale 直接接管 DOWN/SIDEWAYS/UP 边界。更合理的研究方向是：**strength-only temporal scale estimator**，或把 60m scale 分解为 carrier effect、time/regime effect 与 clock/source effect；只有未来预注册候选同时达到 state-semantic non-inferiority，才重新讨论 state-boundary representation。

## 当前 calibration 判断

```text
UNIVERSAL_FIXED_T1                  = CURRENT_V1_BASELINE, NOT UNIVERSAL LAW
STATIC_INTERVAL_SPECIFIC_T1         = NOT SUPPORTED FOR ADOPTION
PROFILE_SPECIFIC_T1                 = NOT SUPPORTED AS DEFAULT
STATIC_NORMALIZED_SCORE             = NOT SUPPORTED FOR ADOPTION
CAUSAL_STATE_BOUNDARY_NORMALIZATION = NOT SUPPORTED FOR ADOPTION
CAUSAL_STRENGTH_SCALE_NORMALIZATION = PROMISING DIAGNOSTIC, TEMPORAL STABILITY NOT ESTABLISHED
CURRENT_DECISION                    = INSUFFICIENT_EVIDENCE
```

## X6 — Representation / Version Decision — HOLD

当前 action：**NO V1 CHANGE / NO ADMISSION EXPANSION / NO X6 VERSION BUMP**。

## 全程冻结边界

- 不重跑 M5 primary / T2 sensitivity / STAR50 replication；
- 不打开旧 M4/M5 2025 Holdout；
- 不把 research-only public/legacy source 写成 runtime admitted source；
- 不因 clock alignment 宣称 exact source identity；
- 不产生 `global_state`、BUY/SELL、position/order、strategy selection/routing；
- `production_authority=false`、`fresh_oos=false`；
- 任何改变 T1、lookback、estimator、strength semantics 或 snapshot lifecycle 的决定必须版本化；
- 历史 V1 snapshots 不得原地改写。
