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
- **X5C — COMPLETE**：五指数 15m/60m + 60m 长窗口；underpower 已解除，60m heterogeneity 持续。
- **X5D — COMPLETE / NO ADOPTION**：静态 interval-specific T1 与静态 normalization 无外部语义支配。
- **X5E — COMPLETE / NO ADOPTION**：60m temporal scale nonstationarity 得到支持；causal rolling normalization 只改善 cross-carrier strength scale，未建立 temporal stability。
- **X5F — COMPLETE / DIAGNOSTIC ONLY**：60m scale 分解出 carrier + common-time 两个真实一阶成分；cross-carrier normalized_strength diagnostic 获得支持，但 stable temporal representation 仍未建立。
- **X6 — HOLD / NOT READY**：不做 representation / SemVer 变更。

V1 release pointer `release/trend-regime-v1.0.0` 必须继续指向原 M9 gated commit `5a563d87d1628379e0d9a04aa7c5500bc30c4bc2`；Post-V1 研究提交不得移动它。

## V1 冻结表示

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

稳定入口：`query_regime(symbol, as_of, bar_interval, profile_id=None)`。Runtime admission 仍只有 `000852.SH` / `000688.SH` 的 1m official 与 5m offset0。Post-V1 public/legacy research source 不产生 runtime admission。

## 已建立的 Post-V1 基础结论

X2/X3 显示：同一 interval 内 phase dispersion 总体较小，跨 interval 差异明显更大。X5/X5B 又显示 5m 在五指数和两个公开 provider 之间相当稳定；目前没有证据支持 carrier-specific / phase-specific / provider-specific 的 5m T1。

X5C 将 60m 扩到五指数 2026-01-05 至 2026-09-14、每 carrier 661 measurements，最小 directional origins = 181。样本不足不再是主要解释，但 60m SIDEWAYS occupancy cross-carrier range 仍约 12.41pp，survival5 DOWN/UP range 约 14.75pp / 10.44pp。

X5D 用 2020 Development 拟合静态 calibration，再用 2026 五指数外部评价。interval-specific `T1_60m≈1.2225` 与 median-abs normalization 等价 `T1_60m≈1.2701` 都不能全面改善 persistence/reversal 语义，因此不采纳。

X5E 证明 60m raw strength 具有明显时间尺度漂移：五指数 monthly `median(abs(slope_t))` 最大/最小比约 1.61×–3.32×。40/80/120-bar strictly-causal rolling normalization 可把 cross-carrier median-strength range 压低约 92.7%–96.0%，但 within-carrier monthly stability 没有一致改善，动态 state boundary 也存在语义 trade-off，因此仍不修改 V1。

## X5F — 60m Strength Scale Decomposition — COMPLETE

Protocol：`docs/governance/TREND_X5F_60M_STRENGTH_SCALE_DECOMPOSITION_PROTOCOL_V1.json`  
Method：`docs/governance/TREND_X5F_DECOMPOSITION_METHOD_V1.json`  
Clock/source identifiability：`docs/governance/TREND_X5F_CLOCK_SOURCE_IDENTIFIABILITY_RECEIPT_V1.json`  
Result：`docs/governance/TREND_X5F_60M_STRENGTH_SCALE_DECOMPOSITION_RESULT_V1.json`  
Decision update：`docs/governance/TREND_X4_POST_X5F_UPDATE_V1.json`

X5F 仍只研究表示层的 strength scale；不算收益、不做策略选择、不改 state boundary、不改变 V1 `strength=abs(slope_t)`。

### X5F-1：carrier 与 common-time 都是真实一阶成分

五指数 × 9 个 2026 calendar months 上，以 monthly `median(abs(slope_t))` 为 scale cell，对 log-scale 做 robust two-way decomposition：

```text
log(scale) = grand + carrier_effect + common_time_effect + residual
```

balanced log-cell ANOVA 的描述性方差分解：

- carrier ≈ **27.4%**
- common-time ≈ **32.4%**
- residual / carrier×time interaction ≈ **40.2%**
- carrier + time 合计解释 ≈ **59.9%**

因此 60m scale 不能只解释成“某个指数天生更大”，也不能只解释成“某个月波动更大”；两者都重要，而且交互残差仍很大。

全样本 robust carrier multiplicative factors 约为：

```text
CSI1000  1.000
STAR50   1.148
CSI300   0.764
CSI500   1.124
SSE50    0.802
```

common-time factor 从 2026-01 的约 **0.626** 到 2026-06 的约 **1.248**，最大/最小约 **1.99×**。carrier factor 最大/最小约 **1.50×**。

### X5F-2：同样本 cross-carrier alignment 很强，但这不是 adoption 证据

完整样本中，carrier median-strength max/min 从 raw 的约 **1.514×** 降到 decomposition-normalized 的约 **1.039×**。由于 time/carrier factors 同样使用该样本估计，这只能算描述性压缩，不能当外部验证。

### X5F-3：leave-one-carrier-out 仍显示真实 transfer benefit

固定 Jan–Apr 为训练、May–Sep 为评价。对每个 held-out carrier：

- held-out carrier factor 只使用该 carrier 的 Jan–Apr；
- May–Sep common-time factor只使用另外四个 carrier；
- held-out carrier 的 May–Sep 未来数据不参与 factor 估计。

May–Sep raw carrier median-strength range ≈ **1.470**、max/min ≈ **1.494×**；LOO normalization 后 range ≈ **0.270**、max/min ≈ **1.301×**。range 压缩约 **81.6%**。

这说明 carrier + common-time decomposition 对 cross-carrier normalized_strength diagnostic 有真实 transfer value，而不只是同样本机械对齐。

### X5F-4：但 stable temporal representation 仍未建立

Jan–Apr 与 May–Sep 分别估计 carrier factor：rank correlation ≈ **0.70**，最大单 carrier multiplicative factor drift ≈ **1.242×**（约 24%），中位 log-factor drift ≈ 0.073。

更关键的是，LOO 后 held-out carrier 的 May–Sep monthly normalized-strength max/min 仍约：

```text
CSI1000  1.576×
STAR50   2.015×
CSI300   2.394×
CSI500   1.488×
SSE50    1.475×
```

完整 two-way decomposition 后 residual cell factor 仍约 **0.754–1.816**，max/min ≈ **2.41×**。所以简单 `carrier × common-time` 只解决了主要的一阶尺度差异，未消除 carrier×time interaction。

### X5F-5：regime 与 clock/source 的可识别边界

没有独立的外生 regime label，因此 common-time factor **不能**被重命名为已识别的 causal regime effect。按 V1 state 分组的 residual strength 只能做描述，不能作为独立 regime 证据。

Clock/source audit 中，STAR50 DataHub `60m_offset30` 与 `offset45` 在 2026 有重叠，因此可在同一 provider 下识别 scope-limited clock-phase effect。满足最小样本 gate 的月份里，offset45/offset30 scale ratio 中位数约 **0.956**，月度 ratio max/min ≈ **1.114×**：存在 clock-phase scale effect，但量级小于主 carrier/time 变化且本身也时变。

Sina native 60m 与 DataHub offset30/45 同时改变 provider 与 clock，只能标为 `confounded_source_clock`；纯 provider effect 和 five-carrier clock effect **未识别**。

## X5F 决策

```text
60M_CARRIER_SCALE_EFFECT                  = SUPPORTED
60M_COMMON_TIME_SCALE_EFFECT              = SUPPORTED
CARRIER_TIME_INTERACTION_RESIDUAL         = MATERIAL
CROSS_CARRIER_NORMALIZED_STRENGTH         = SUPPORTED_RESEARCH_ONLY_DIAGNOSTIC
STABLE_TEMPORAL_NORMALIZED_STRENGTH       = NOT ESTABLISHED
INDEPENDENT_CAUSAL_REGIME_EFFECT          = NOT IDENTIFIED
PURE_PROVIDER_EFFECT                      = NOT IDENTIFIED
V1_STATE                                  = NO CHANGE
V1_STRENGTH                               = NO CHANGE
X6                                        = HOLD / NOT READY
```

因此可以保留一个 research-only 候选：

```text
normalized_strength_diag
  = raw abs(slope_t)
    / governed_carrier_scale
    / governed_common_time_scale
```

但它不是 V1 产品输出，也不能改写 DOWN/SIDEWAYS/UP。下一步若继续，应研究 **carrier×time interaction / causal common-scale estimator / 更完整的 same-clock cross-provider 与 same-provider multi-clock 证据**，而不是重新调 T1。

## 当前总体判断

```text
UNIVERSAL_FIXED_T1                  = CURRENT_V1_BASELINE, NOT UNIVERSAL LAW
STATIC_INTERVAL_SPECIFIC_T1         = NOT SUPPORTED FOR ADOPTION
STATIC_NORMALIZED_SCORE             = NOT SUPPORTED FOR ADOPTION
CAUSAL_STATE_BOUNDARY_NORMALIZATION = NOT SUPPORTED FOR ADOPTION
CROSS_CARRIER_STRENGTH_NORMALIZATION= SUPPORTED RESEARCH DIAGNOSTIC ONLY
STABLE_TEMPORAL_STRENGTH_REPRESENTATION = NOT ESTABLISHED
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
