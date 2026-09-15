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
- **X5I — COMPLETE / NO CANDIDATE PASSES TURNOVER-AWARE PROSPECTIVE GATES**：独立 Tencent native 60m 复制 short-memory scale 优势，同时 prospectively 确认 high turnover。
- **X5J — COMPLETE / NO GATE-QUALIFIED TURNOVER-REGULARIZED CANDIDATE**：cap / EWMA 未同时解决响应速度与 turnover；Tencent 与 Sina 结果一致。
- **X5K — COMPLETE / NO GATE-QUALIFIED SPARSE-HYSTERETIC CANDIDATE**：deadband / persistence / hysteretic EWMA 仍未同时解决 update frequency、jump size 与 scale stability。
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

X5I 在结构独立的 Tencent native 60m 上重新比较 slow 20/120、fast 5/20 与 dual blend，并在看 Tencent candidate outcome 前把 median / q95 `|Δlog(scale)| <= 2.0× slow` 纳入正式 gate。Fast 与 dual 再次复制了强 scale alignment，但都因 turnover gate 失败；slow turnover 合格，但 temporal / breadth / interaction 不合格。因此无 candidate 晋级。

关键结果：

```text
fast 5/20
  range reduction      ≈ 93.84%
  temporal improvement ≈ 23.87%
  breadth              = 5/5
  interaction improve  ≈ 37.95%
  turnover median/q95  ≈ 3.39× / 2.11× slow
  result               = FAIL

dual blend
  range reduction      ≈ 93.75%
  temporal improvement ≈ 22.97%
  breadth              = 5/5
  interaction improve  ≈ 36.25%
  turnover median/q95  ≈ 3.21× / 2.21× slow
  result               = FAIL
```

## X5J — Turnover-Regularized Strength Scale Study — COMPLETE

X5J 是开发型研究，明确 `fresh_oos=false`。候选在统计前冻结，不做参数网格扫优：slow / fast / dual 三条 baseline 加 `FAST_CAP_0P06`、`FAST_EWMA_A0P35`、`DUAL_CAP_0P06`。Tencent 为 primary，Sina 为 cross-provider replication。

结果显示：

- `CAP_0.06` 通过 turnover non-inferiority，但 temporal / breadth / interaction 基本丢失；post-hoc 发现 q10–q95 `|Δlog(scale)|` 全部等于 0.06，说明它几乎每根都打满 cap，成为持续 catch-up。
- `EWMA α=0.35` 保留 alignment，并把 q95 turnover 降到 slow 的约 1.34×，但 median turnover 仍约 3.46×；它降低尾部，却没有降低更新频率。
- Tencent 与 Sina 均无全 gate candidate。

因此连续型 regularization 暂时无法同时得到 fast-scale responsiveness 与 slow-scale low-turnover。

## X5K — Sparse / Hysteretic Strength Scale Update Study — COMPLETE

Protocol：`docs/governance/TREND_X5K_SPARSE_HYSTERETIC_STRENGTH_SCALE_PROTOCOL_V1.json`  
Result：`docs/governance/TREND_X5K_SPARSE_HYSTERETIC_STRENGTH_SCALE_RESULT_V1.json`  
Post-hoc event-size diagnostic：`docs/governance/TREND_X5K_POSTHOC_EVENT_SIZE_DIAGNOSTIC_V1.json`  
Decision：`docs/governance/TREND_X4_POST_X5K_UPDATE_V1.json`

X5K 不再继续调 cap / EWMA 参数，而是把 **update frequency** 纳入正式 gate，并增加平均绝对 `Δlog(scale)` 与 q95 jump 两个 turnover gate，避免“更新很少但每次巨跳”被误判为稳定。

预注册稀疏候选：

```text
EVENT_DEADBAND_0P12_FULL
EVENT_PERSIST2_0P10_FULL
HYSTERETIC_EWMA_ENTRY0P16_EXIT0P06_A0P50
```

同时保留 slow 20/120 与 fast 5/20 作为 baseline。要求同时满足：cross-carrier range reduction ≥75%、temporal improvement ≥15%、breadth ≥4/5、interaction improvement ≥20%、mean turnover ≤2× slow、q95 turnover ≤2× slow、update fraction ≤35%。

Tencent primary：

| candidate | range reduction | temporal improvement | breadth | interaction improvement | mean turnover | q95 turnover | update fraction | all gates |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| slow 20/120 | 84.57% | 10.85% | 2/5 | 0% | 1.00× | 1.00× | 78.4% | FAIL |
| fast 5/20 | 93.84% | 23.87% | 5/5 | 37.95% | 2.73× | 2.11× | 87.6% | FAIL |
| deadband 0.12 full | 93.77% | 23.59% | 5/5 | 38.41% | 2.65× | 2.11× | 55.2% | FAIL |
| persist2 0.10 full | **94.35%** | 19.00% | 4/5 | 35.32% | 2.66× | **3.20×** | **34.7%** | FAIL |
| hysteretic EWMA | 93.81% | 23.18% | 4/5 | 30.14% | 2.43× | **1.60×** | 84.6% | FAIL |

Sina 几乎逐项复现，仍为：

```text
TENCENT_QUALIFIED_CANDIDATES        = []
SINA_QUALIFIED_CANDIDATES           = []
CROSS_PROVIDER_QUALIFIED_CANDIDATES = []
SELECTED_CANDIDATE                  = NONE
```

### X5K 失败机制

- Deadband 0.12 仍有约 **55.2%** 的观测发生更新，稀疏性不足，且 mean / q95 turnover 都超 gate。
- `PERSIST2` 是第一个真正进入 update-frequency gate 的方案（约 **34.7%**），但它把 fast 的很多小更新攒成大跳：post-hoc 条件更新次数从 fast 的 1148 次降到 451 次，条件均值从约 **0.197** 放大到 **0.483**，条件 q95 从 **0.520** 放大到 **0.969**，因此 mean / q95 turnover 反而失败。
- Hysteretic EWMA 的 q95 turnover 已降到约 **1.60×** slow，但 update fraction 仍约 **84.6%**，没有形成稀疏事件驱动。

因此 X5K 说明：**仅靠 deadband、持续性确认或简单 hysteretic EWMA，仍不能同时降低更新频率与单次跳跃幅度。** 下一研究问题应转向 sparse partial-reset / anchored event updates 或 cooldown-based stateful control，在触发事件时只释放一部分累积误差，并显式治理 cooldown 与 jump size；不得在同一 outcomes 上继续做阈值网格扫优。

## 当前总体判断

```text
UNIVERSAL_FIXED_T1                        = CURRENT V1 BASELINE, NOT UNIVERSAL LAW
CAUSAL_STATE_BOUNDARY_NORMALIZATION       = NOT SUPPORTED FOR ADOPTION
CROSS_CARRIER_STRENGTH_NORMALIZATION      = SUPPORTED RESEARCH DIAGNOSTIC
SHORT_MEMORY_SCALE                        = BENEFIT REPLICATED, TURNOVER TOO HIGH
CONTINUOUS_TURNOVER_REGULARIZATION        = NO GATE-QUALIFIED CANDIDATE IN X5J
SPARSE_HYSTERETIC_UPDATE                  = NO GATE-QUALIFIED CANDIDATE IN X5K
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
