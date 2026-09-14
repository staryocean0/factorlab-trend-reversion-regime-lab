# 从这里接管

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 当前状态

本仓是 Layer 2 趋势状态识别组件，不是交易策略。**M0–M9 PASS**，V1 release 已冻结。

Component：`factorlab.layer2.trend_regime@1.0.0`。

2026-09-14 用户显式授权独立的 Post-V1 **Cross-Profile Invariance & Calibration Study**。它不是自动 M10，不修改 V1。

当前研究进度：

- X1–X3 — **COMPLETE**
- X4 — **`INSUFFICIENT_EVIDENCE` / NO V1 CHANGE**
- X5 / X5B — **5m replication + source robustness COMPLETE**
- X5C — **15m/60m cross-carrier COMPLETE**
- X5D — **static calibration COMPLETE / NO ADOPTION**
- X5E — **causal rolling normalization COMPLETE / NO ADOPTION**
- X5F — **60m carrier × common-time decomposition COMPLETE / DIAGNOSTIC ONLY**
- X5G — **dynamic common + slow carrier COMPLETE / DIAGNOSTIC ONLY**
- X5H — **adaptive regime-shift strength scale COMPLETE / ONE PRIMARY RESEARCH CANDIDATE QUALIFIED, NO ADOPTION**
- X6 — **HOLD / NOT READY**

V1 release pointer `release/trend-regime-v1.0.0` 必须继续固定在 `5a563d87d1628379e0d9a04aa7c5500bc30c4bc2`；Post-V1 research commits 不得移动它。

## 接管必读

- `docs/ROADMAP.md`
- `docs/governance/TREND_X5H_ADAPTIVE_REGIME_SHIFT_STRENGTH_SCALE_PROTOCOL_V1.json`
- `docs/governance/TREND_X5H_ADAPTIVE_REGIME_SHIFT_STRENGTH_SCALE_RESULT_V1.json`
- `docs/governance/TREND_X4_POST_X5H_UPDATE_V1.json`
- `docs/governance/TREND_X5G_DYNAMIC_COMMON_SCALE_CARRIER_INTERACTION_RESULT_V1.json`
- `docs/governance/TREND_X5F_60M_STRENGTH_SCALE_DECOMPOSITION_RESULT_V1.json`
- `docs/governance/TREND_M7_CONSUMER_CONTRACT_V1.json`
- `docs/governance/TREND_M9_RELEASE_GOVERNANCE_V1.json`

## V1 正式产品

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

入口：`query_regime(symbol, as_of, bar_interval, profile_id=None)`。

Runtime admission 仍只有 `000852.SH` / `000688.SH` 的 1m official 与 5m offset0；Post-V1 public/native-clock research 数据不获得 admission。

## X5F / X5G 背景

X5F 将 60m monthly scale 拆为 carrier、common-time 与 residual：carrier ≈ **27.4%**，common-time ≈ **32.4%**，interaction residual ≈ **40.2%**。Cross-carrier normalization 有真实 transfer value，但 residual cell factor max/min 仍约 **2.408×**。

X5G 的 strictly-causal fixed-window common+carrier 候选均能把 cross-carrier range 压低约 80%–86%，但没有候选同时通过 temporal / breadth / interaction gates；更慢窗口还会出现明显 regime-shift lag。因此下一步转为 X5H 的快慢自适应 scale。

## X5H：Adaptive Regime-Shift Strength Scale

主评价固定为完整的 **2026-06 / 07 / 08**，每 carrier 260 measurements；9 月 1–14 日仅作 forward extension，不参与候选选择。common fast/slow = **5 / 20**，carrier fast/slow = **20 / 120**，所有 scale 只读取 `t-1` 及更早信息。

### 主结论

唯一通过全部预注册 gate 的候选：

```text
ADAPT_DUAL_BLEND_1P5
```

主样本表现：

```text
cross-carrier range reduction             ≈ 93.75%
median monthly max/min                     1.5066× -> 1.1604×
temporal reduction                         ≈ 22.98%
carriers improved                          5/5
monthly-cell max/min                       1.3560×
interaction reduction vs X5G baseline      ≈ 36.26%
```

因此它是 **gate-qualified research candidate**，可以进入新的 prospective replication；但它不是产品采用结论。

### 为什么仍不能改 V1

Dual blend 大多数时候都明显偏向 fast scale：common mean blend weight ≈ **0.761**，carrier mean ≈ **0.708**，约 70%–75% observations 的 blend weight ≥0.5。

Post-hoc mechanism diagnostic（不参与主判定）发现，纯 fast `common=5 / carrier=20` 甚至略优：主样本 cross-carrier reduction ≈ **93.83%**、temporal reduction ≈ **23.87%**、5/5 carrier 改善、monthly-cell max/min ≈ **1.320×**；9 月前推 cross-carrier reduction ≈ **79.1%**。

所以 X5H 不能证明“adaptive regime-shift blend”这一机制本身优于简单 short-memory scaling。

另外 scale turnover 显著升高：

```text
median |Δ log(scale)|
X5G baseline     ≈ 0.0346
dual blend       ≈ 0.1112   (~3.21×)
pure fast        ≈ 0.1175   (~3.39×)

q95 |Δ log(scale)|
X5G baseline     ≈ 0.2400
dual blend       ≈ 0.5310   (~2.21×)
pure fast        ≈ 0.5061   (~2.11×)
```

Turnover 不是 X5H 预注册 gate，因此不能事后取消主样本 pass；但它足以阻止我们把候选直接升级成稳定产品 representation。

## 当前结论

```text
GATE_QUALIFIED_RESEARCH_CANDIDATE        = ADAPT_DUAL_BLEND_1P5
SPECIFIC_REGIME_SHIFT_MECHANISM          = NOT IDENTIFIED
PURE_FAST_5_20                           = POST_HOC COMPARATOR, MUST BE PREREGISTERED NEXT
SCALE_TURNOVER                           = MATERIAL NEW CONCERN
STABLE_TEMPORAL_PRODUCT_STRENGTH         = NOT ESTABLISHED
CAUSAL_STATE_BOUNDARY_NORMALIZATION      = NOT SUPPORTED
CURRENT_DECISION                         = INSUFFICIENT_EVIDENCE
V1                                       = NO CHANGE
X6                                       = HOLD / NOT READY
```

下一步如继续，必须新开预注册研究：直接比较 **dual blend vs pure-fast 5/20 vs slow baseline**，新增 scale-turnover/jitter non-inferiority gate，并使用 fresh 或结构独立的 validation window/source/carrier set。不得用交易收益或 state outcome 选择 strength estimator。

## 仍然禁止

- 重跑 M5 primary / T2 sensitivity / STAR50 replication；
- 打开旧 M4/M5 2025 Holdout；
- 修改冻结的 M6/M7/M8/M9 semantics；
- 把 public/native-clock research source 写成 runtime admitted 或 DataHub exact identity；
- 输出 `global_state`、BUY/SELL、position/order、strategy selection/routing；
- 把 `production_authority=false` 或 `fresh_oos=false` 改成 true。

历史 V1 snapshots 永不原地改写。未来任何 T1、lookback、estimator、strength semantics 改动都必须经过新的版本化 representation decision。
