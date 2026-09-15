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
- **X5H — COMPLETE / RESEARCH CANDIDATE ONLY**：`ADAPT_DUAL_BLEND_1P5` 通过当时 scale gates，但 turnover 成为重大风险。
- **X5I — COMPLETE / NO CANDIDATE PASSES TURNOVER-AWARE PROSPECTIVE GATES**：Tencent 独立 source 复制 short-memory benefit，同时 prospectively 确认 high turnover。
- **X5J — COMPLETE / NO GATE-QUALIFIED TURNOVER-REGULARIZED CANDIDATE**：cap / EWMA 未同时解决响应速度与 turnover。
- **X5K — COMPLETE / NO GATE-QUALIFIED SPARSE-HYSTERETIC CANDIDATE**：deadband / persistence / hysteretic EWMA 仍未同时解决 update frequency、jump size 与 stability。
- **X5L — COMPLETE / ANCHORED PARTIAL PASSES 6 OF 7 GATES / NO ADOPTION**：partial reset + cooldown 显著推进 frontier，但 interaction gate 仍未过。
- **X6 — HOLD / NOT READY**：不做 representation / SemVer 变更。

V1 release pointer `release/trend-regime-v1.0.0` 必须继续指向 `5a563d87d1628379e0d9a04aa7c5500bc30c4bc2`。

## V1 冻结表示

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

Runtime admission 仍只有 `000852.SH` / `000688.SH` 的 1m official 与 5m offset0。Post-V1 research source 不产生 runtime admission。

## X5H–X5K 已知边界

X5H 的 `ADAPT_DUAL_BLEND_1P5` 与 pure-fast 5/20 显示 short-memory scale 能显著改善 cross-carrier / temporal alignment，但 median/q95 turnover 高。X5I 在 Tencent native 60m 上独立复制这个事实。X5J 的 `FAST_EWMA_A0P35` 能降低 tail turnover，却把更新摊成持续中等步长；固定 cap 则变成持续 catch-up。X5K 加入 update-frequency gate 后，`PERSIST2` 虽将更新频率降到约 34.7%，却把小更新积累成大跳。

因此到 X5K 为止：

```text
SHORT_MEMORY_SCALE_BENEFIT            = REPLICATED
HIGH_TURNOVER_COST                    = REPLICATED
CONTINUOUS_REGULARIZATION             = NO QUALIFIED CANDIDATE
SPARSE_HYSTERETIC_UPDATE              = NO QUALIFIED CANDIDATE
```

## X5L — Partial-Reset / Cooldown Stateful Strength Scale — COMPLETE

Protocol：`docs/governance/TREND_X5L_PARTIAL_RESET_COOLDOWN_STRENGTH_SCALE_PROTOCOL_V1.json`  
Result：`docs/governance/TREND_X5L_PARTIAL_RESET_COOLDOWN_STRENGTH_SCALE_RESULT_V1.json`  
Post-hoc interaction diagnostic：`docs/governance/TREND_X5L_POSTHOC_INTERACTION_DIAGNOSTIC_V1.json`  
Decision：`docs/governance/TREND_X4_POST_X5L_UPDATE_V1.json`

X5L 不再增加 persistence 次数或提高 deadband，而是测试事件发生后只释放部分累积误差，并强制 cooldown。候选在统计前冻结：

```text
SLOW_COMMON20_CARRIER120
FAST_COMMON5_CARRIER20
PARTIAL_PERSIST2_GAP0P10_F0P50_COOLDOWN2
PARTIAL_DEADBAND0P12_F0P50_COOLDOWN2
ANCHORED_PARTIAL_DB0P12_F0P50_COOLDOWN2_SLOW25
```

七项 gate 继续沿用 X5K：cross-carrier、temporal、breadth、interaction、mean turnover、q95 jump、update fraction；必须全部通过，并要求 Tencent 与 Sina 都通过。

### Tencent primary

| candidate | range reduction | temporal improvement | breadth | interaction | mean turnover | q95 turnover | update fraction | result |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| slow 20/120 | 84.57% | 10.85% | 2/5 | 0% | 1.00× | 1.00× | 78.4% | FAIL |
| fast 5/20 | 93.84% | 23.87% | 5/5 | 37.95% | 2.73× | 2.11× | 87.6% | FAIL |
| partial persist2 | 91.46% | 23.92% | 4/5 | 29.27% | 1.55× | **2.36×** | 23.2% | FAIL |
| partial deadband | 93.75% | 23.98% | 4/5 | 31.91% | 1.77× | **2.47×** | 31.7% | FAIL |
| **anchored partial** | **92.06%** | **17.28%** | **4/5** | **18.54%** | **1.38×** | **1.88×** | **31.7%** | **FAIL: interaction only** |

Sina replication 几乎逐项一致。`ANCHORED_PARTIAL_DB0P12_F0P50_COOLDOWN2_SLOW25` 是目前最接近全部 gate 的 research-only 候选：两个 provider 都通过 6/7 gate，但 interaction improvement 约 **18.54%**，低于预注册 **20%**。

Post-hoc diagnostic 显示这不是 provider 偶然差异：Tencent / Sina 都由 2026-06 的 STAR50 最大 cell 与 CSI300 最小 cell 定义剩余 monthly-cell ratio。该诊断不参与 selection，也不允许放宽 gate。

因此：

```text
TENCENT_QUALIFIED_CANDIDATES        = []
SINA_QUALIFIED_CANDIDATES           = []
CROSS_PROVIDER_QUALIFIED_CANDIDATES = []
SELECTED_CANDIDATE                  = NONE
```

X5L 之后不得在同一 outcomes 上调整 slow anchor 25%、partial fraction 50%、trigger 0.12、cooldown=2 或 interaction gate。下一步应冻结 anchored-partial 机制原样，在**结构上新的时间窗口 / regime**上验证；只有独立新证据支持，才有资格进入参数修订或未来 representation decision。

## 历史回归锚点

以下字符串保留用于 fail-closed 文档回归，不代表当前采用：

```text
NO_CHANGE
ADAPT_DUAL_BLEND_1P5
FAST_COMMON5_CARRIER20
FAST_EWMA_A0P35
EVENT_PERSIST2_0P10_FULL
```

## 当前总体判断

```text
UNIVERSAL_FIXED_T1                        = CURRENT V1 BASELINE, NOT UNIVERSAL LAW
CAUSAL_STATE_BOUNDARY_NORMALIZATION       = NOT SUPPORTED FOR ADOPTION
CROSS_CARRIER_STRENGTH_NORMALIZATION      = SUPPORTED RESEARCH DIAGNOSTIC
SHORT_MEMORY_SCALE                        = BENEFIT REPLICATED, TURNOVER TOO HIGH
CONTINUOUS_TURNOVER_REGULARIZATION        = NO GATE-QUALIFIED CANDIDATE IN X5J
SPARSE_HYSTERETIC_UPDATE                  = NO GATE-QUALIFIED CANDIDATE IN X5K
PARTIAL_RESET_COOLDOWN                    = PROMISING, NO GATE-QUALIFIED CANDIDATE IN X5L
ANCHORED_PARTIAL                          = CROSS-PROVIDER 6-OF-7 NEAR-CANDIDATE ONLY
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
- 不在 X5L outcomes 上调整 anchor、partial fraction、trigger、cooldown 或 gate；
- `production_authority=false`、`fresh_oos=false`；
- 任何改变 T1、lookback、estimator、strength semantics 或 snapshot lifecycle 的决定必须版本化；
- 历史 V1 snapshots 不得原地改写。
