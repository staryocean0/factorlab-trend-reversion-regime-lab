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
- **X5N — COMPLETE / FAILURE ATTRIBUTION**：早期失败支持 broad regime-transition；Mar–May 失败集中于 `000016.SH` 的 carrier-specific regime interaction；peer composition 与 median-vs-mean common estimator 不是主要解释；clock 对主失败不可识别。
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

X5M 只验证一个冻结候选 `ANCHORED_PARTIAL_DB0P12_F0P50_COOLDOWN2_SLOW25`，七项 gate 与 X5L 完全不变。Structural Block A（Sina 2025-11/12 + 2026-01）通过 5/7，失败 temporal 与 q95 turnover；Structural Block B（Tencent + Sina 2026-03/04/05）通过 6/7，但 interaction improvement≈-11.15%。因此 `ANCHORED_PARTIAL_PROMOTION=REJECTED`，`STRUCTURAL_GENERALIZATION=NOT_ESTABLISHED`。

## X5N — Structural Failure Attribution & Regime Conditionality — COMPLETE

Protocol：`docs/governance/TREND_X5N_STRUCTURAL_FAILURE_ATTRIBUTION_PROTOCOL_V1.json`  
Result：`docs/governance/TREND_X5N_STRUCTURAL_FAILURE_ATTRIBUTION_RESULT_V1.json`  
Decision：`docs/governance/TREND_X4_POST_X5N_UPDATE_V1.json`

X5N 没有调任何 X5L/X5M 参数，只做归因：

- rolling 3-month panel 显示 failure pattern 随时间切换：早期连续失败 temporal；Mar–Jul 转为 interaction 主导，说明 regime conditionality 明显。
- 早期 Block A 五个 carrier 的 q95 turnover 全部超过 2x slow（约 2.06–2.63x），且 common raw strength 从约 3.81 下行到 2.99，支持 broad market-regime transition / controller response，而非单 carrier 故障。
- Mar–May 中，000852/000688/000300/000905 的 temporal improvement 约 19%–31%，但 `000016.SH` 从 raw monthly ratio≈1.296 恶化到 normalized≈2.423，即 temporal improvement≈-87%，支持 carrier-specific regime decoupling。
- 000016 peer jackknife 后 ratio 仍约 2.11–2.48，`CARRIER_COMPOSITION` 不支持作为主要驱动。
- peer median 改成 peer mean 后 000016 ratio 仅改善约 4.4%，interaction 反而约 -18%，`COMMON_SCALE_ESTIMATOR` 的 median-vs-mean 选择不支持作为主要驱动。
- 当前只有 Tencent/Sina native 60m 的 000016 同窗资产，没有 alternate 60m clock，所以 `CLOCK_STRUCTURE=NOT_IDENTIFIABLE`，不得硬归因。

当前归因：

```text
MARKET_REGIME_CONDITIONALITY              = SUPPORTED
CARRIER_SPECIFIC_REGIME_INTERACTION_000016 = SUPPORTED
CARRIER_COMPOSITION_PRIMARY_DRIVER         = NOT SUPPORTED
COMMON_MEDIAN_ESTIMATOR_PRIMARY_DRIVER     = NOT SUPPORTED
CLOCK_STRUCTURE                            = NOT IDENTIFIABLE
SINGLE_UNIFIED_STATEFUL_NORMALIZATION_LAW  = NOT ESTABLISHED
RETUNE_ON_X5N_OUTCOMES                     = FORBIDDEN
V1                                          = NO CHANGE
X6                                          = HOLD / NOT READY
```

X5N 之后不应继续局部修补 X5L 参数。未来若继续 normalized_strength 研究，应先提出新的结构假设（最自然的是显式 regime-conditional representation）或获得独立 alternate-clock 证据，再在看 outcomes 前冻结新协议。

## 历史回归锚点

以下字符串保留用于 fail-closed 文档回归，不代表当前采用；其中 X5F 的历史结论是 cross-carrier diagnostic 有价值但 stable temporal representation 未建立。

```text
X5B
X5C
X5D
X5E
X5F
X5G
X5H
X5I
X5J
X5K
X5L
NO_CHANGE
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
- 不基于 X5L/X5M/X5N outcomes 调 anchor、partial fraction、trigger、cooldown 或 gate；
- `production_authority=false`、`fresh_oos=false`；
- 历史 V1 snapshots 不得原地改写。
