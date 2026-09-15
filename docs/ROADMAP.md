# 趋势状态识别组件路线图

> 本仓的 trend-regime 是 Layer 2 市场状态基础设施，不是交易策略。
>
> M0–M9 已完成并冻结。Post-V1 Cross-Profile Invariance & Calibration Study 是用户显式授权的独立研究线，不得静默改写 V1。

## 当前进度

- **M0–M9 — COMPLETE / PASS**：`factorlab.layer2.trend_regime@1.0.0` 已冻结。
- **X1–X3 — COMPLETE**：source/profile inventory、distributional / state-dynamics invariance。
- **X4 — `INSUFFICIENT_EVIDENCE` / NO_CHANGE**：不修改 V1。
- **X5 / X5B — COMPLETE**：五指数 5m replication + source robustness。
- **X5C — COMPLETE**：五指数 15m/60m + 60m 长窗口。
- **X5D–X5G — COMPLETE / NO ADOPTION**：静态、rolling、carrier×time 与 dynamic common/slow carrier 均未建立稳定产品表示。
- **X5H–X5K — COMPLETE / NO ADOPTION**：short-memory benefit 与 turnover cost 均被复制；continuous / sparse-hysteretic controls 无全 gate candidate。
- **X5L — COMPLETE / 6-OF-7 NEAR-CANDIDATE ONLY**：`ANCHORED_PARTIAL_DB0P12_F0P50_COOLDOWN2_SLOW25` 在 Jun–Aug 同窗跨 Tencent/Sina 通过 6/7 gate。
- **X5M — COMPLETE / STRUCTURAL VALIDATION FAILS PROMOTION**：冻结 anchored-partial 在结构新窗口未复制为 gate-qualified representation。
- **X6 — HOLD / NOT READY**：不做 representation / SemVer 变更。

V1 release pointer `release/trend-regime-v1.0.0` 必须继续指向 `5a563d87d1628379e0d9a04aa7c5500bc30c4bc2`。

## V1 冻结表示

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

Runtime admission 仍只有 `000852.SH` / `000688.SH` 的 1m official 与 5m offset0。Post-V1 research source 不产生 runtime admission。

## X5M — Frozen Anchored-Partial Structural Validation — COMPLETE

Protocol：`docs/governance/TREND_X5M_FROZEN_ANCHORED_STRUCTURAL_VALIDATION_PROTOCOL_V1.json`  
Result：`docs/governance/TREND_X5M_FROZEN_ANCHORED_STRUCTURAL_VALIDATION_RESULT_V1.json`  
Diagnostic：`docs/governance/TREND_X5M_POSTHOC_STRUCTURAL_FAILURE_DIAGNOSTIC_V1.json`  
Decision：`docs/governance/TREND_X4_POST_X5M_UPDATE_V1.json`

X5M 只验证一个冻结候选：

```text
ANCHORED_PARTIAL_DB0P12_F0P50_COOLDOWN2_SLOW25
slow target       = common20 / carrier120
fast target       = common5 / carrier20
trigger           = |log-gap| >= 0.12
event target      = 75% fast + 25% slow
partial fraction  = 50%
cooldown          = 2 measurements
```

七项 gate 与 X5L 完全不变：cross-carrier、temporal、breadth、interaction、mean turnover、q95 turnover、update fraction。

### Structural Block A

Sina native 60m，2025-11 / 12 + 2026-01；252 measurements/carrier。Public-native 2025 行此前被排除在候选统计之外；**没有读取旧 M4/M5 governed 2025 Holdout**。

```text
range reduction      ≈ 75.27%
temporal improvement ≈ 11.80%   FAIL
breadth              = 5/5
interaction improve  ≈ 30.63%
mean turnover        ≈ 1.61x slow
q95 turnover         ≈ 2.41x slow FAIL
update fraction      ≈ 31.08%
passed               = 5/7
```

### Structural Block B

Tencent + Sina native 60m，2026-03 / 04 / 05；244 measurements/carrier。两源几乎逐项一致：

```text
range reduction      ≈ 86.37%
temporal improvement ≈ 26.02%
breadth              = 4/5
interaction improve  ≈ -11.15%   FAIL
mean turnover        ≈ 1.26x slow
q95 turnover         ≈ 1.82x slow
update fraction      ≈ 31.28%
passed               = 6/7
```

Post-hoc diagnostic 显示 Block B 的 interaction failure 主要由上证50 `000016` 的月度 ratio≈2.42 驱动；另外四个 carrier 约 1.06–1.16。Tencent 与 Sina 同步复现，因此不是单一 provider 偶然差异。

## X5M 决策

```text
ANCHORED_PARTIAL_PROMOTION          = REJECTED
STRUCTURAL_GENERALIZATION           = NOT ESTABLISHED
RETUNE_ON_X5M_OUTCOMES              = FORBIDDEN
STABLE_TEMPORAL_PRODUCT_STRENGTH    = NOT ESTABLISHED
CURRENT_DECISION                    = INSUFFICIENT_EVIDENCE
V1                                  = NO CHANGE
X6                                  = HOLD / NOT READY
```

X5M 之后不应继续在同一 X5L/X5M outcomes 上微调 anchor、partial fraction、trigger、cooldown 或 gate。未来若继续，需要先提出**新的结构假设**或获得真正新的外部证据，再单独冻结协议。

## 历史回归锚点

以下字符串保留用于 fail-closed 文档回归，不代表当前采用：

```text
X5G
X5H
X5I
X5J
X5K
X5L
ADAPT_DUAL_BLEND_1P5
FAST_COMMON5_CARRIER20
FAST_EWMA_A0P35
EVENT_PERSIST2_0P10_FULL
```

## 全程冻结边界

- 不重跑 M5 primary / T2 sensitivity / STAR50 replication；
- 不打开旧 M4/M5 governed 2025 Holdout；
- 不把 public/native-clock research source 写成 runtime admitted source；
- 不产生 `global_state`、BUY/SELL、position/order、strategy selection/routing；
- `production_authority=false`、`fresh_oos=false`；
- 历史 V1 snapshots 不得原地改写。
