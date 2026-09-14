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

### 1. Phase 不是主要不稳定源

X2/X3 的 2020-07-23 至 2020-12-31 Development-only exact-view 研究显示：同一 interval 内 phase dispersion 总体较小；5m offset0–4 尤其稳定。跨 interval 差异明显大于 phase 差异。

### 2. 5m 对 carrier 与 public source 较稳健

X5 五指数 5m（CSI1000、STAR50、CSI300、CSI500、SSE50）结果：

- SIDEWAYS occupancy range ≈ **3.13pp**；
- one-step self-transition range ≈ **1.23–1.87pp**；
- 5-bar directional survival range：DOWN ≈ **6.54pp**、UP ≈ **2.81pp**。

X5B 在 CSI1000 / STAR50 上比较 Sina 与 Eastmoney：

- slope_t Pearson ≈ **0.9999994**；
- slope_t abs-diff q95 < **0.004**；
- 三桶状态 **100% 一致**；
- DOWN ↔ UP disagreement = **0**。

因此当前没有证据支持 carrier-specific、phase-specific 或 provider-specific 的 5m T1。

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

60m 所有预注册 directional metrics 的最小 origins = **181**，已超过 adequate threshold 100；因此早先的 60m UP underpower 不再是主要解释。

同一 2026-08-17 至 2026-09-14 日历切片中，60m 的 score/occupancy dispersion 仍显著高于 5m/15m，进一步支持 interval effect。

同时，60m 月度 SIDEWAYS occupancy 在单 carrier 内也高度漂移，说明不能把“强制占比恒定”当作正确 calibration 的定义。

## X5D — Static Calibration Comparison — COMPLETE

Protocol：`docs/governance/TREND_X5D_INTERVAL_CALIBRATION_COMPARISON_PROTOCOL_V1.json`  
Calibration method：`docs/governance/TREND_X5D_DEVELOPMENT_CALIBRATION_METHOD_V1.json`  
Development receipt：`docs/governance/TREND_X5D_DEVELOPMENT_CALIBRATION_RECEIPT_V1.json`  
Result：`docs/governance/TREND_X5D_INTERVAL_CALIBRATION_COMPARISON_RESULT_V1.json`  
Decision update：`docs/governance/TREND_X4_POST_X5D_UPDATE_V1.json`

参数只使用 2020 Development exact-view 数据拟合；2026 五指数只用于外部 candidate evaluation，没有使用交易收益。

Development 5m 参考 SIDEWAYS target = **0.2382626877**。

拟合得到：

```text
interval-specific T1:
5m  ≈ 1.9989
15m ≈ 1.9351
60m ≈ 1.2225

primary median-abs normalization equivalent raw T1:
5m  = 2.0000
15m ≈ 2.0717
60m ≈ 1.2701
```

两种独立方法都在 Development 上指向“60m raw-equivalent threshold 应低于 2”，但它们没有干净转移到 2026：

- interval-specific T1 相对 V1：16 个 15m+60m 事前语义 dispersion 指标中 **9 改善 / 7 恶化**；
- primary median-abs normalization：**10 改善 / 5 恶化 / 1 持平**；
- MAD normalization：**9 / 7**；
- q75 normalization：**7 / 9**；
- 所有候选之间 **无严格 Pareto dominance**。

60m 静态 calibration 虽把 SIDEWAYS carrier dispersion 从约 **12.4pp** 降至约 **6.8pp**，却明显恶化部分 reversal/persistence 指标；DOWN opposite-entry10 dispersion 从 V1 的约 **5.2pp** 上升到约 **11%–12%**。候选同时改变约 **10%–15%** 的 60m 状态分类。

q75 normalization 将 cross-interval strength-level range 从 raw 的约 **0.506** 降至约 **0.157**，说明 strength scaling 值得继续研究；但它没有同步支配 state semantics，因此不能据此改变状态边界或 strength 定义。

## 当前 calibration 判断

```text
UNIVERSAL_FIXED_T1                  = CURRENT_V1_BASELINE, NOT UNIVERSAL LAW
STATIC_INTERVAL_SPECIFIC_T1         = NOT SUPPORTED FOR ADOPTION
PROFILE_SPECIFIC_T1                 = NOT SUPPORTED AS DEFAULT
STATIC_NORMALIZED_SCORE             = NOT SUPPORTED FOR ADOPTION
NORMALIZED_STRENGTH_SCALE           = PROMISING DIAGNOSTIC, NOT PRODUCT SEMANTICS
CURRENT_DECISION                    = INSUFFICIENT_EVIDENCE
```

当前 60m 问题已经从“样本太少”升级为：**interval scale + temporal/regime nonstationarity + clock/source identity** 的联合问题。

## X6 — Representation / Version Decision — HOLD

当前 action：**NO V1 CHANGE / NO ADMISSION EXPANSION / NO X6 VERSION BUMP**。

如果继续研究 normalization，下一步必须：

1. 明确区分 **state-boundary normalization** 与 **strength-scale normalization**；
2. 使用 causal / out-of-time 方法，不能拿 2026 evaluation 再拟合一个静态阈值；
3. 不通过强制固定 SIDEWAYS occupancy 抹掉真实市场 regime 信息；
4. 优先增加 governed/exact 60m clock 证据，或预注册新的因果 normalization protocol。

## 全程冻结边界

- 不重跑 M5 primary / T2 sensitivity / STAR50 replication；
- 不打开旧 M4/M5 2025 Holdout；
- 不把 research-only public/legacy source 写成 runtime admitted source；
- 不因 clock alignment 宣称 exact source identity；
- 不产生 `global_state`、BUY/SELL、position/order、strategy selection/routing；
- `production_authority=false`、`fresh_oos=false`；
- 任何改变 T1、lookback、estimator、strength semantics 或 snapshot lifecycle 的决定必须版本化；
- 历史 V1 snapshots 不得原地改写。
