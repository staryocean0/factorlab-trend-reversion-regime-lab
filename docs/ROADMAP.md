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
- **X5N — COMPLETE / FAILURE ATTRIBUTION**：regime conditionality 与 `000016.SH` carrier×regime interaction 得到支持；peer composition / median-vs-mean estimator 不是主要解释；clock 对主失败不可识别。
- **X5O — COMPLETE / NO CAUSAL REGIME OBSERVABLE IDENTIFIED**：预注册的 slope_t-independent return-geometry observables 未达到 identifiability gates；`CORRELATION_BREAK` 仅保留为 diagnostic clue。
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

X5M 只验证冻结候选 `ANCHORED_PARTIAL_DB0P12_F0P50_COOLDOWN2_SLOW25`。Structural Block A（Sina 2025-11/12 + 2026-01）通过 5/7，失败 temporal 与 q95 turnover；Structural Block B（Tencent + Sina 2026-03/04/05）通过 6/7，但 interaction improvement≈-11.15%。因此 `ANCHORED_PARTIAL_PROMOTION=REJECTED`，`STRUCTURAL_GENERALIZATION=NOT_ESTABLISHED`。

## X5N — Structural Failure Attribution & Regime Conditionality — COMPLETE

Protocol：`docs/governance/TREND_X5N_STRUCTURAL_FAILURE_ATTRIBUTION_PROTOCOL_V1.json`  
Result：`docs/governance/TREND_X5N_STRUCTURAL_FAILURE_ATTRIBUTION_RESULT_V1.json`  
Decision：`docs/governance/TREND_X4_POST_X5N_UPDATE_V1.json`

X5N 只归因、不调参。rolling 3-month panel 显示 failure pattern 随时间切换；早期五 carrier q95 turnover 全部 >2x slow，支持 broad `MARKET_REGIME_CONDITIONALITY`。Mar–May 的 interaction reversal 则集中于 `000016.SH`，支持 carrier-specific regime interaction。000016 peer jackknife 与 peer median→mean counterfactual 均不足以解释主失败；clock 对 000016 主失败不可识别。

## X5O — Causal Regime Observable Identifiability — COMPLETE

Protocol：`docs/governance/TREND_X5O_CAUSAL_REGIME_OBSERVABLE_IDENTIFIABILITY_PROTOCOL_V1.json`  
Result：`docs/governance/TREND_X5O_CAUSAL_REGIME_OBSERVABLE_IDENTIFIABILITY_RESULT_V1.json`  
Post-hoc source diagnostic：`docs/governance/TREND_X5O_POSTHOC_OBSERVABLE_SOURCE_AGREEMENT_V1.json`  
Decision：`docs/governance/TREND_X4_POST_X5O_UPDATE_V1.json`

X5O 在看到评价统计前冻结了四个完全独立于 `slope_t` / state 的严格因果 observable：`COMMON_VOL_SHIFT`、`XS_VOL_SHIFT_DISPERSION`、`CORRELATION_BREAK`、`SSE50_RELATIVE_VOL_SHIFT`。所有 alert threshold 只由 2025-09/10 reference months 的 80th percentile 决定，评价块不参与阈值生成。

正式结果：

```text
COMMON_REGIME_OBSERVABLE_IDENTIFIED        = false
SSE50_CARRIER_REGIME_OBSERVABLE_IDENTIFIED = false
common alert rho vs q95 severity            ≈ 0.405
000016 alert rho vs normalized ratio        ≈ 0.491
000016 alert rho vs interaction loss        ≈ 0.169
```

`CORRELATION_BREAK` 的 threshold-free rho vs q95 severity≈0.833，是最强 diagnostic clue，但首个结构失败块 alert fraction≈37.3%，低于预注册 50% gate，因此不能宣称具备可靠的事前识别能力。其 2026 同窗 Tencent/Sina 连续值 Pearson≈0.99999994，说明弱信号不是单一 provider artifact，但 source agreement 不会改变主 identifiability failure。

因此：

```text
REGIME_CONDITIONALITY_EXISTS                = SUPPORTED BY X5N
CAUSAL_REGIME_IDENTIFIABILITY               = NOT ESTABLISHED BY X5O
REGIME_SWITCH_RULE                          = NOT AUTHORIZED
UNIFIED_DYNAMIC_NORMALIZED_STRENGTH         = PAUSE DEVELOPMENT
RETUNE_ON_X5O_OUTCOMES                      = FORBIDDEN
CURRENT_DECISION                            = INSUFFICIENT_EVIDENCE
V1                                          = NO CHANGE
X6                                          = HOLD / NOT READY
```

X5O 之后不应在当前 outcomes 上搜索新 threshold、组合 observable 或拟合 regime-switched normalization。只有真正新的外生 regime 信息、独立 alternate-clock 证据，或完全新且事前冻结的结构假设，才足以重启这条 representation 研究线。

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
CLOCK_STRUCTURE
RETUNE_ON_X5N_OUTCOMES
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
- 不基于 X5O outcomes 搜索 observable threshold、alert combination 或 regime-switched law；
- `production_authority=false`、`fresh_oos=false`；
- 历史 V1 snapshots 不得原地改写。
