# 趋势状态识别组件路线图

> 本仓的 trend-regime 是 Layer 2 市场状态基础设施，不是交易策略。
>
> 原 M0–M9 已完成并冻结；2026-09-14 用户显式授权独立的 Post-V1 Cross-Profile Invariance & Calibration Study。后续研究不得静默改写 V1。

## 当前进度

- **M0–M9 — COMPLETE / PASS**：`factorlab.layer2.trend_regime@1.0.0` 稳定组件合同已冻结。
- **X1–X3 — COMPLETE**：source/profile inventory、distributional / state-dynamics invariance。
- **X4 — `INSUFFICIENT_EVIDENCE`**：不修改 V1。
- **X5 / X5B — COMPLETE**：五指数 5m replication + source robustness。
- **X5C — COMPLETE**：五指数 15m/60m + 60m 长窗口；60m heterogeneity 持续。
- **X5D — COMPLETE / NO ADOPTION**：静态 interval-specific T1 / static normalization 无外部语义支配。
- **X5E — COMPLETE / NO ADOPTION**：causal rolling normalization 改善 cross-carrier scale，但未建立 temporal stability。
- **X5F — COMPLETE / DIAGNOSTIC ONLY**：carrier + common-time 解释约 59.9% log-scale variation，约 40.2% interaction 未解决。
- **X5G — COMPLETE / DIAGNOSTIC ONLY**：dynamic common + slow carrier 显著改善 cross-carrier alignment，但 fixed-window temporal stability 未建立。
- **X5H — COMPLETE / PRIMARY RESEARCH CANDIDATE QUALIFIED, NO ADOPTION**：dual fast/slow blend 通过预注册主 gate，但机制识别与 scale-turnover 仍未解决。
- **X6 — HOLD / NOT READY**：不做 representation / SemVer 变更。

V1 release pointer `release/trend-regime-v1.0.0` 必须继续指向原 M9 gated commit `5a563d87d1628379e0d9a04aa7c5500bc30c4bc2`；Post-V1 研究提交不得移动它。

## V1 冻结表示

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

Runtime admission 仍只有 `000852.SH` / `000688.SH` 的 1m official 与 5m offset0。Post-V1 public/native-clock research source 不产生 runtime admission。

## 到 X5F/X5G 已知的 60m scale 结构

X5F 的五指数 × 2026-01..09 monthly scale decomposition：

```text
log(scale) = grand + carrier_effect + common_time_effect + residual
carrier ≈ 27.4%
common-time ≈ 32.4%
residual / carrier×time ≈ 40.2%
```

Jan–Apr → May–Sep leave-one-carrier-out 可将 carrier median-strength range 从约 **1.470** 压到 **0.270**（约 -81.6%），但 residual cell factor max/min 仍约 **2.408×**。

X5G 再测试 strictly-causal dynamic common scale + slow carrier component。四个预注册 fixed-window 候选均把 cross-carrier range 压低约 **80.2%–85.9%**，但没有一个同时通过 temporal / breadth / interaction gates。最接近的 `COMMON20_CARRIER120` 在完整 6–9 月里 temporal ratio 基本与 raw 持平，说明更慢 fixed-window smoothing 存在 regime-shift lag。

## X5H — Adaptive Regime-Shift Strength Scale — COMPLETE

Protocol：`docs/governance/TREND_X5H_ADAPTIVE_REGIME_SHIFT_STRENGTH_SCALE_PROTOCOL_V1.json`  
Result：`docs/governance/TREND_X5H_ADAPTIVE_REGIME_SHIFT_STRENGTH_SCALE_RESULT_V1.json`  
Decision update：`docs/governance/TREND_X4_POST_X5H_UPDATE_V1.json`

X5H 仍只研究 `normalized_strength`，不计算收益、不使用策略、不改 state boundary、不改变 V1 `strength=abs(slope_t)`。

### 预注册设计

为避免 X5G 的 partial-May 影响，主评价固定为三个完整月份：**2026-06 / 07 / 08**，每 carrier **260 measurements**；2026-09-01..14 仅作前推 extension，不参与候选选择。

严格因果候选均只使用 `t-1` 及更早信息。common fast/slow = **5 / 20**，carrier fast/slow = **20 / 120**，blend threshold 固定为 **1.5×**。预注册候选包括 X5G baseline、carrier blend、common blend、dual blend、carrier reset。

### X5H-1：dual blend 通过全部预注册主 gate

主样本 raw：

```text
cross-carrier median-strength range     = 2.1942
median monthly max/min                  = 1.5066×
monthly-cell max/min                    = 2.7612×
```

`ADAPT_DUAL_BLEND_1P5`：

```text
cross-carrier range                     = 0.1370
range reduction vs raw                  = 93.75%
median monthly max/min                  = 1.1604×
temporal reduction vs raw               = 22.98%
carriers improved                       = 5/5
monthly-cell max/min                    = 1.3560×
interaction reduction vs X5G baseline   = 36.26%
```

因此它是 **X5H 预注册 gate-qualified research candidate**。其他四个预注册候选均未通过全部 gate。

### X5H-2：但“regime-shift mechanism”本身未被识别

Dual blend 的 fast 权重非常活跃：common mean weight ≈ **0.761**，carrier mean weight ≈ **0.708**；约 70%–75% 观测的权重 ≥0.5。也就是说它大部分时间都明显偏向 fast scale，并非稀疏 change-point switch。

明确标记为 post-hoc、且不参与主判定的 mechanism diagnostic 中，纯 fast `common=5 / carrier=20` 甚至略优：

```text
cross-carrier range reduction           ≈ 93.83%
temporal reduction                      ≈ 23.87%
carriers improved                       = 5/5
monthly-cell max/min                    ≈ 1.3200×
interaction reduction vs X5G baseline   ≈ 37.95%
```

因此 X5H 支持“更短记忆 scale 有价值”，但**不能证明 adaptive blend 的特定 regime-shift 机制优于单纯 fast scaling**。

### X5H-3：前推 extension 有支持，但不足以升级语义

2026-09-01..14：raw cross-carrier range ≈ **1.5041**；dual blend ≈ **0.4418**，仍改善约 **70.6%**。该 extension 未用于选择，而且若机械套用主样本 75% gate，它并未达到该阈值。

### X5H-4：scale turnover 明显上升

Post-hoc turnover diagnostic 显示：

```text
X5G baseline median |Δ log(scale)|       ≈ 0.0346
dual blend                               ≈ 0.1112   (~3.21× baseline)
pure fast 5/20                           ≈ 0.1175   (~3.39× baseline)

X5G baseline q95 |Δ log(scale)|          ≈ 0.2400
dual blend                               ≈ 0.5310   (~2.21× baseline)
pure fast                                ≈ 0.5061   (~2.11× baseline)
```

这说明更好的月度 scale alignment 是以明显更高的逐步 scale turnover 换来的。Turnover 并非 X5H 预注册 gate，因此不能事后否决 primary pass，但它阻止我们把该 candidate 直接宣称为稳定产品表示。

## X5H 决策

```text
GATE_QUALIFIED_RESEARCH_CANDIDATE        = ADAPT_DUAL_BLEND_1P5
SPECIFIC_REGIME_SHIFT_MECHANISM          = NOT IDENTIFIED
SHORT_MEMORY_SCALE_VALUE                 = SUPPORTED FOR FURTHER RESEARCH
STABLE_TEMPORAL_PRODUCT_STRENGTH         = NOT ESTABLISHED
V1_STATE                                 = NO CHANGE
V1_STRENGTH                              = NO CHANGE
X6                                       = HOLD / NOT READY
```

下一步如继续，应在**新的预注册阶段**中直接比较 dual blend、pure-fast 5/20 与 slow baseline，并新增明确的 scale-turnover / jitter non-inferiority gate，同时使用 fresh 或结构独立的 validation window/source/carrier set。不得用交易收益或 state outcome 选择 strength estimator。

## 当前总体判断

```text
UNIVERSAL_FIXED_T1                        = CURRENT V1 BASELINE, NOT UNIVERSAL LAW
CAUSAL_STATE_BOUNDARY_NORMALIZATION       = NOT SUPPORTED FOR ADOPTION
CROSS_CARRIER_STRENGTH_NORMALIZATION      = SUPPORTED RESEARCH DIAGNOSTIC
ADAPTIVE_DUAL_BLEND                       = PROSPECTIVE REPLICATION CANDIDATE ONLY
PURE_FAST_5_20                            = POST-HOC COMPARATOR, REQUIRES PREREGISTRATION
STABLE_TEMPORAL_PRODUCT_STRENGTH          = NOT ESTABLISHED
CURRENT_DECISION                          = INSUFFICIENT_EVIDENCE
```

## X6 — Representation / Version Decision — HOLD

当前 action：**NO V1 CHANGE / NO ADMISSION EXPANSION / NO X6 VERSION BUMP**。

## 全程冻结边界

- 不重跑 M5 primary / T2 sensitivity / STAR50 replication；
- 不打开旧 M4/M5 2025 Holdout；
- 不把 research-only public/legacy source 写成 runtime admitted source；
- 不产生 `global_state`、BUY/SELL、position/order、strategy selection/routing；
- `production_authority=false`、`fresh_oos=false`；
- 任何改变 T1、lookback、estimator、strength semantics 或 snapshot lifecycle 的决定必须版本化；
- 历史 V1 snapshots 不得原地改写。
