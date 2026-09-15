# 趋势状态识别组件路线图

> 本仓的 trend-regime 是 Layer 2 市场状态基础设施，不是交易策略。
>
> M0–M9 已完成并冻结。Post-V1 Cross-Profile Invariance & Calibration Study 是用户显式授权的独立研究线，不得静默改写 V1。

## 当前进度

- **M0–M9 — COMPLETE / PASS**：`factorlab.layer2.trend_regime@1.0.0` 已冻结。
- **X1–X3 — COMPLETE**：source/profile inventory、distributional / state-dynamics invariance。
- **X4 — `INSUFFICIENT_EVIDENCE`**：不修改 V1。
- **X5 / X5B — COMPLETE**：五指数 5m replication + source robustness。
- **X5C — COMPLETE**：五指数 15m/60m + 60m 长窗口；60m heterogeneity 持续。
- **X5D — COMPLETE / NO ADOPTION**：静态 interval T1 / static normalization 无全面语义优势。
- **X5E — COMPLETE / NO ADOPTION**：causal rolling normalization 改善 cross-carrier scale，但未建立 temporal stability。
- **X5F — COMPLETE / DIAGNOSTIC ONLY**：carrier + common-time 约解释 59.9% log-scale variation，约 40.2% interaction 未解决。
- **X5G — COMPLETE / DIAGNOSTIC ONLY**：strictly-causal dynamic common + slow carrier 改善横截面对齐，fixed-window temporal stability 未建立。
- **X5H — COMPLETE / RESEARCH CANDIDATE ONLY**：dual blend 通过当时预注册 scale gates，但 turnover 为后验重大风险。
- **X5I — COMPLETE / NO CANDIDATE PASSES TURNOVER-AWARE PROSPECTIVE GATES**：独立 Tencent native 60m 复制 short-memory scale 优势，同时 prospectively 确认 high turnover，因而无候选晋级产品表示。
- **X6 — HOLD / NOT READY**：不做 representation / SemVer 变更。

V1 release pointer `release/trend-regime-v1.0.0` 必须继续指向 `5a563d87d1628379e0d9a04aa7c5500bc30c4bc2`。

## V1 冻结表示

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

Runtime admission 仍只有 `000852.SH` / `000688.SH` 的 1m official 与 5m offset0。Post-V1 research source 不产生 runtime admission。

## X5F–X5H 背景

X5F 显示 60m scale 同时具有 carrier effect、common-time effect 与大量 carrier×time residual。X5G 的 strictly-causal common/carrier normalization 稳定改善 cross-carrier strength alignment，但无法解决时间稳定性。X5H 随后测试 fast/slow adaptive scale，在 2026-06/07/08 的 Sina native 60m 上，`ADAPT_DUAL_BLEND_1P5` 曾通过当时四个 scale gates；但 post-hoc 发现 pure-fast 5/20 同样或更好，且 dual / fast 的逐步 scale turnover 分别约为 slow baseline 的 3.21× / 3.39×（median）和 2.21× / 2.11×（q95）。因此 X5H 只把 dual 晋级为 prospective research candidate，未采纳。

## X5I — Prospective Fast-vs-Adaptive Strength Scale Validation — COMPLETE

Protocol：`docs/governance/TREND_X5I_PROSPECTIVE_FAST_VS_ADAPTIVE_STRENGTH_SCALE_PROTOCOL_V1.json`  
Primary-source block：`docs/governance/TREND_X5I_EASTMONEY_SOURCE_BLOCK_RECEIPT_V1.json`  
Recovery protocol：`docs/governance/TREND_X5I_SOURCE_RECOVERY_PROTOCOL_V1.json`  
Tencent source receipt：`docs/governance/TREND_X5I_TENCENT_SOURCE_RECEIPT_V1.json`  
Depth extension receipt：`docs/governance/TREND_X5I_TENCENT_DEPTH_EXTENSION_RECEIPT_V1.json`  
Method：`docs/governance/TREND_X5I_EVALUATION_METHOD_V1.json`  
Protocol erratum：`docs/governance/TREND_X5I_PROTOCOL_ERRATUM_V1.json`  
Result：`docs/governance/TREND_X5I_PROSPECTIVE_FAST_VS_ADAPTIVE_STRENGTH_SCALE_RESULT_V1.json`  
Decision：`docs/governance/TREND_X4_POST_X5I_UPDATE_V1.json`

### Source / design

Eastmoney primary endpoint 在当前执行链连续被远端断开，因此按预注册规则没有计算任何 primary-source candidate outcome。随后在没有 outcome leakage 的前提下冻结 source-recovery protocol，改用结构独立的 **Tencent native 60m**。

Tencent `ifzq.gtimg.cn` m60 对 800-depth 请求稳定返回五指数各 800 根。统计加载后立刻过滤到 **2026-01-05..2026-09-14**，每 carrier 680 bars / 661 slope measurements；公共源返回的 2025 行未参与任何统计，旧 M4/M5 governed 2025 Holdout 未读取。五指数 native clock 都为 `10:30 / 11:30 / 14:00 / 15:00`，0 bad days。

Primary evaluation 固定为完整的 **2026-06 / 07 / 08**，每 carrier 260 measurements；9 月 1–14 日仅作 forward diagnostic。

Prospective 候选只有：

```text
SLOW_COMMON20_CARRIER120
FAST_COMMON5_CARRIER20
ADAPT_DUAL_BLEND_1P5
```

Turnover gate 在看 Tencent 候选结果前冻结：median 和 q95 `|Δlog(scale)|` 都必须 ≤ slow baseline 的 **2.0×**。

### Prospective result

Raw primary：

```text
cross-carrier range              = 2.1943
median monthly max/min           = 1.5066×
monthly-cell max/min             = 2.7612×
```

| candidate | range reduction | temporal improvement | carriers improved | interaction improvement vs slow | median turnover vs slow | q95 turnover vs slow | all gates |
|---|---:|---:|---:|---:|---:|---:|---|
| slow 20/120 | 84.57% | 10.85% | 2/5 | 0% | 1.00× | 1.00× | FAIL |
| fast 5/20 | **93.84%** | **23.87%** | **5/5** | **37.95%** | **3.39×** | **2.11×** | FAIL |
| dual blend | **93.75%** | **22.97%** | **5/5** | **36.25%** | **3.21×** | **2.21×** | FAIL |

Fast 与 dual 在独立 Tencent source 上复制了 X5H 的 scale-level 优势，但两者均同时违反 median 与 q95 turnover non-inferiority gate。Slow turnover 合格，但 temporal / breadth / interaction 不合格。因此：

```text
ALL_GATE_QUALIFIED_CANDIDATES = []
SELECTED_CANDIDATE             = NONE
```

9 月 forward diagnostic 仍显示 short-memory 有横截面改善：raw range ≈ 1.5037，fast ≈ 0.3146，dual ≈ 0.4418；但它不参与选择。

### X5I 科学结论

```text
SHORT_MEMORY_SCALE_BENEFIT                    = REPLICATED_ON_INDEPENDENT_PROVIDER
ADAPTIVE_DUAL_SCALE_BENEFIT                   = REPLICATED
SCALE_TURNOVER_CONCERN                        = PROSPECTIVELY CONFIRMED
SPECIFIC_REGIME_SHIFT_MECHANISM               = NOT IDENTIFIED
STABLE_TEMPORAL_NORMALIZED_STRENGTH            = NOT ESTABLISHED
V1_STATE                                      = NO CHANGE
V1_STRENGTH                                   = NO CHANGE
X6                                            = HOLD / NOT READY
```

这一步把 X5H 的 turnover 从“后验担忧”升级为“独立源上的预注册 gate failure”。因此当前不应继续争论 dual vs pure-fast 谁更好，而应研究 **响应性与 jitter 的折中**：例如 bounded-update / turnover-regularized / smoother-fast causal scale estimator。

## 当前总体判断

```text
UNIVERSAL_FIXED_T1                        = CURRENT V1 BASELINE, NOT UNIVERSAL LAW
CAUSAL_STATE_BOUNDARY_NORMALIZATION       = NOT SUPPORTED FOR ADOPTION
CROSS_CARRIER_STRENGTH_NORMALIZATION      = SUPPORTED RESEARCH DIAGNOSTIC
SHORT_MEMORY_SCALE                        = REPLICATED, BUT TURNOVER TOO HIGH UNDER X5I GATES
STABLE_TEMPORAL_PRODUCT_STRENGTH          = NOT ESTABLISHED
CURRENT_DECISION                          = INSUFFICIENT_EVIDENCE
```

## X6 — Representation / Version Decision — HOLD

当前 action：**NO V1 CHANGE / NO ADMISSION EXPANSION / NO X6 VERSION BUMP**。

## 全程冻结边界

- 不重跑 M5 primary / T2 sensitivity / STAR50 replication；
- 不打开旧 M4/M5 governed 2025 Holdout；
- 不把 public/native-clock research source 写成 runtime admitted source；
- 不产生 `global_state`、BUY/SELL、position/order、strategy selection/routing；
- `production_authority=false`、`fresh_oos=false`；
- 任何改变 T1、lookback、estimator、strength semantics 或 snapshot lifecycle 的决定必须版本化；
- 历史 V1 snapshots 不得原地改写。
