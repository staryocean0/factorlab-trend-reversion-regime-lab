# 趋势状态识别组件路线图

> 本仓的 trend-regime 是 Layer 2 市场状态基础设施，不是交易策略。
>
> 原 M0–M9 已完成并冻结；2026-09-14 用户显式授权独立的 Post-V1 Cross-Profile Invariance & Calibration Study。后续研究不得静默改写 V1。

## 当前进度

- **M0–M9 — COMPLETE / PASS**：`factorlab.layer2.trend_regime@1.0.0` 稳定组件合同已冻结。
- **X1 — COMPLETE**：source/profile inventory。
- **X2 — COMPLETE**：两指数 × 10 exact views 的固定基线与 sensitivity。
- **X3 — COMPLETE**：state-dynamics invariance；60m carrier heterogeneity 明显。
- **X4 — `INSUFFICIENT_EVIDENCE`**：不修改 V1。
- **X5 — COMPLETE**：五指数 5m external replication。
- **X5B — COMPLETE**：5m Sina ↔ Eastmoney source robustness。
- **X5C — COMPLETE**：五指数 15m/60m + 60m 长窗口；60m heterogeneity 持续。
- **X5D — COMPLETE / NO ADOPTION**：静态 interval-specific T1 / static normalization 无外部语义支配。
- **X5E — COMPLETE / NO ADOPTION**：causal rolling normalization 改善 cross-carrier scale，但未建立 temporal stability。
- **X5F — COMPLETE / DIAGNOSTIC ONLY**：carrier + common-time 解释约 59.9% log-scale variation，约 40.2% interaction 未解决。
- **X5G — COMPLETE / DIAGNOSTIC ONLY**：strictly-causal dynamic common scale + slow carrier component 再次显著改善 cross-carrier alignment，但没有建立 stable temporal normalized_strength。
- **X6 — HOLD / NOT READY**：不做 representation / SemVer 变更。

V1 release pointer `release/trend-regime-v1.0.0` 必须继续指向原 M9 gated commit `5a563d87d1628379e0d9a04aa7c5500bc30c4bc2`；Post-V1 研究提交不得移动它。

## V1 冻结表示

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

稳定入口：`query_regime(symbol, as_of, bar_interval, profile_id=None)`。Runtime admission 仍只有 `000852.SH` / `000688.SH` 的 1m official 与 5m offset0。Post-V1 public/native-clock research source 不产生 runtime admission。

## X5F — 60m Strength Scale Decomposition

X5F 在五指数 × 2026-01..09 monthly scale cells 上得到：

```text
log(scale) = grand + carrier_effect + common_time_effect + residual
```

描述性 log-cell variance fractions：

- carrier ≈ **27.4%**
- common-time ≈ **32.4%**
- residual / carrier×time interaction ≈ **40.2%**

Jan–Apr → May–Sep leave-one-carrier-out 中，May–Sep raw carrier median-strength range ≈ **1.470**，normalization 后 ≈ **0.270**，约压缩 **81.6%**；说明 cross-carrier normalized_strength 有真实 transfer value。

但 train/eval carrier-factor rank correlation 只有约 **0.70**，最大 factor drift 约 **24%**；two-way residual cell factor max/min 仍约 **2.408×**。因此 X5F 只支持 research diagnostic，不支持稳定产品表示。

## X5G — Dynamic Common Scale & Carrier-Time Interaction Study — COMPLETE

Protocol：`docs/governance/TREND_X5G_DYNAMIC_COMMON_SCALE_CARRIER_INTERACTION_PROTOCOL_V1.json`  
Result：`docs/governance/TREND_X5G_DYNAMIC_COMMON_SCALE_CARRIER_INTERACTION_RESULT_V1.json`  
Decision update：`docs/governance/TREND_X4_POST_X5G_UPDATE_V1.json`

X5G 只研究 strength scale，不计算收益、不使用策略、不修改 state boundary，也不改变 V1 `strength=abs(slope_t)`。

### 严格因果定义

对每个 carrier `i` 和时点 `t`：

```text
q_minus_i[u] = median(log_strength[j,u]), j != i
common_i[t]  = median(q_minus_i[u]) over W measurements strictly before t
carrier_i[t] = median(log_strength[i,u] - common_i[u]) over K prior measurements
normalized_strength_i[t]
             = exp(log_strength[i,t] - common_i[t] - carrier_i[t])
```

当前 `t` 不进入自身 scale 估计；common factor 对 carrier `i` 只使用另外四个 carrier；未来信息禁止。

预注册候选：

```text
COMMON20_CARRIER120
COMMON40_CARRIER120
COMMON40_CARRIER240
COMMON80_CARRIER240
```

统一最大 warmup = **320 measurements**，共同评价窗口为 **2026-05-15 15:00 至 2026-09-14 15:00**，每 carrier **341 measurements**。

### X5G-1：cross-carrier alignment 再次稳定改善

同窗 raw carrier median-strength range = **1.4847**。四个候选的 range reduction：

| candidate | normalized range | reduction vs raw |
|---|---:|---:|
| COMMON20_CARRIER120 | 0.2947 | **80.15%** |
| COMMON40_CARRIER120 | 0.2118 | **85.74%** |
| COMMON40_CARRIER240 | 0.2087 | **85.94%** |
| COMMON80_CARRIER240 | 0.2886 | **80.56%** |

因此 dynamic common + carrier decomposition 对 cross-carrier strength alignment 的作用是可重复的，不只是 X5F static-month decomposition 的偶然现象。

### X5G-2：但 stable temporal representation 仍没有建立

预注册 stability gate 同时要求：

1. cross-carrier range reduction ≥ 50%；
2. median within-carrier monthly max/min 至少改善 10%；
3. 至少 4/5 carrier temporal ratio 改善；
4. residual monthly-cell max/min < X5F 的 2.4080。

结果：**没有任何候选通过全部四项**。

最接近的是 `COMMON20_CARRIER120`：

- cross-carrier range reduction ≈ **80.15%** — PASS；
- median monthly max/min：raw **3.3912× → 2.1657×**，改善约 **36.1%** — PASS；
- 4/5 carrier temporal ratio 改善 — PASS；
- residual monthly-cell max/min = **4.1675×**，高于 X5F **2.4080×** — FAIL。

更慢的 40/80 common window 或 240 carrier window，temporal stability 反而进一步恶化；说明 fixed-window smoothing 存在明显 regime-shift lag。

### X5G-3：post-hoc full-month diagnostic 不改变主判定

统一 warmup 后第一个评价月从 **2026-05-15** 才开始。预注册规则只要求当月 ≥20 measurements，因此 5 月必须保留在 primary decision。

事后只看完整的 2026-06..09：

```text
raw median within-carrier monthly max/min      ≈ 1.6006×
COMMON20_CARRIER120                            ≈ 1.6040×
raw monthly-cell max/min                       ≈ 2.7612×
COMMON20_CARRIER120 monthly-cell max/min       ≈ 2.2826×
```

因此 `(20,120)` 的 primary-window temporal improvement 很大一部分来自对 5 月 scale shift 的响应；在完整 6–9 月内，时间稳定性基本没有改善，只是 cell dispersion 略有下降。该分析是 post-hoc diagnostic，不用于修改预注册主结论。

## X5G 决策

```text
DYNAMIC_COMMON_SCALE_EFFECT                 = SUPPORTED
SLOW_CARRIER_COMPONENT                     = USEFUL FOR CROSS-CARRIER ALIGNMENT
CROSS_CARRIER_DYNAMIC_NORMALIZED_STRENGTH  = SUPPORTED RESEARCH DIAGNOSTIC ONLY
STABLE_TEMPORAL_NORMALIZED_STRENGTH         = NOT ESTABLISHED
FIXED_WINDOW_INTERACTION_RESOLUTION         = NOT SUPPORTED
V1_STATE                                    = NO CHANGE
V1_STRENGTH                                 = NO CHANGE
X6                                           = HOLD / NOT READY
```

X5G 后，剩余问题更像 **regime-shift / carrier-by-regime interaction**，而不是一个静态 carrier multiplier 或更慢 rolling window 能解决的噪声。若继续研究，下一优先级应是 **strength-only adaptive / change-point-aware scale response**，仍不得改写 DOWN/SIDEWAYS/UP。

## 当前总体判断

```text
UNIVERSAL_FIXED_T1                       = CURRENT V1 BASELINE, NOT UNIVERSAL LAW
STATIC_INTERVAL_SPECIFIC_T1              = NOT SUPPORTED FOR ADOPTION
STATIC_NORMALIZED_SCORE                  = NOT SUPPORTED FOR ADOPTION
CAUSAL_STATE_BOUNDARY_NORMALIZATION      = NOT SUPPORTED FOR ADOPTION
CROSS_CARRIER_STRENGTH_NORMALIZATION     = SUPPORTED RESEARCH DIAGNOSTIC ONLY
DYNAMIC_COMMON_PLUS_CARRIER_NORMALIZATION= CROSS-CARRIER SUPPORTED, TEMPORAL STABILITY NOT ESTABLISHED
CURRENT_DECISION                         = INSUFFICIENT_EVIDENCE
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
