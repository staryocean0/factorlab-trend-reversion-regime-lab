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

- X1 source/profile inventory — **COMPLETE**
- X2 distributional invariance + sensitivity — **COMPLETE**
- X3 state-dynamics invariance — **COMPLETE**
- X4 calibration-family decision — **`INSUFFICIENT_EVIDENCE` / NO V1 CHANGE**
- X5 five-carrier 5m replication — **COMPLETE**
- X5B 5m source robustness — **COMPLETE**
- X5C five-carrier 15m/60m + long-window 60m — **COMPLETE**
- X5D static interval-specific T1 vs static normalization — **COMPLETE / NO ADOPTION**
- X5E 60m temporal scale + causal rolling normalization — **COMPLETE / NO ADOPTION**
- X5F 60m strength scale decomposition — **COMPLETE / CROSS-CARRIER DIAGNOSTIC ONLY**
- X6 representation version decision — **HOLD / NOT READY**

V1 release pointer `release/trend-regime-v1.0.0` 必须继续固定在 `5a563d87d1628379e0d9a04aa7c5500bc30c4bc2`；Post-V1 research commits 不得移动它。

## 接管必读

- `docs/ROADMAP.md`
- `docs/governance/TREND_X5E_60M_TEMPORAL_SCALE_CAUSAL_NORMALIZATION_RESULT_V1.json`
- `docs/governance/TREND_X5F_60M_STRENGTH_SCALE_DECOMPOSITION_PROTOCOL_V1.json`
- `docs/governance/TREND_X5F_DECOMPOSITION_METHOD_V1.json`
- `docs/governance/TREND_X5F_CLOCK_SOURCE_IDENTIFIABILITY_RECEIPT_V1.json`
- `docs/governance/TREND_X5F_60M_STRENGTH_SCALE_DECOMPOSITION_RESULT_V1.json`
- `docs/governance/TREND_X4_POST_X5F_UPDATE_V1.json`
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

## 研究到现在真正知道什么

### 5m / phase

5m 是目前最稳的一层。五指数 replication 中 SIDEWAYS occupancy range ≈ **3.13pp**；Sina vs Eastmoney 在 CSI1000/STAR50 上三桶状态 **100% 一致**。同 interval phase 差异明显小于跨 interval 差异，因此没有证据要求 5m carrier-specific / phase-specific / provider-specific T1。

### 15m / 60m

15m 比 60m 稳定。X5C 的 60m 长窗口有五个 carrier、每个 661 measurements、最小 directional origins 181；underpower 已解除，但 cross-carrier heterogeneity 仍明显。X5D 的静态 interval T1 / static normalization 都有 persistence/reversal trade-off，因此不采纳。

### X5E：60m scale 确实时变

五指数 monthly `median(abs(slope_t))` 最大/最小比约 **1.61×–3.32×**。40/80/120-bar causal rolling scale 可将 cross-carrier median-strength range 压缩约 **92.7%–96.0%**，但没有一致改善 within-carrier temporal stability；用于动态 state boundary 时也没有 Pareto dominance。因此 normalization 不接管 DOWN/SIDEWAYS/UP。

## X5F：60m strength scale decomposition

X5F 把 monthly 60m strength scale 写为：

```text
log(scale) = grand + carrier_effect + common_time_effect + residual
```

五指数 × 2026-01..09 的 balanced log-cell 方差分解约为：

- **carrier：27.4%**
- **common-time：32.4%**
- **residual / carrier×time interaction：40.2%**

所以 carrier 与 common-time 都是重要的一阶成分，但二者合计只解释约 59.9%；剩余 interaction 不能忽略。

全样本 robust factors 中，carrier 最大/最小约 **1.50×**，common-time 最大/最小约 **1.99×**。完整样本 normalization 可把 carrier median-strength max/min 从 **1.514×** 压到 **1.039×**，但这只是样本内描述。

更重要的是 Jan–Apr → May–Sep leave-one-carrier-out：held-out carrier factor 只用 Jan–Apr，评价期 common-time 只由另外四个 carrier 估计，不使用 held-out future。May–Sep raw carrier median-strength range ≈ **1.470**，LOO 后 ≈ **0.270**，range 压缩约 **81.6%**。因此 cross-carrier normalized_strength diagnostic 有真实 transfer value。

但 stable temporal representation 仍未建立：

- train vs evaluation carrier-factor rank correlation ≈ **0.70**；
- 最大 factor drift ≈ **24%**；
- LOO 后单 carrier monthly normalized-strength max/min 仍约 **1.48×–2.39×**；
- two-way decomposition 后 residual cell factor 仍约 **0.754–1.816**，max/min ≈ **2.41×**。

所以当前可保留的只是 research-only diagnostic：

```text
normalized_strength_diag
  = raw abs(slope_t)
    / governed_carrier_scale
    / governed_common_time_scale
```

它不是 V1 产品输出，也不能改写 state boundary。

## Clock/source 与 regime 边界

STAR50 DataHub `60m_offset30` / `offset45` 在 2026 有重叠，可以在同一 provider 下识别 scope-limited clock-phase effect。满足样本 gate 的月份中，offset45/offset30 scale ratio 中位约 **0.956**，月度 ratio max/min ≈ **1.114×**。

Sina native 60m vs DataHub 同时改变 provider 与 clock，所以只能标记 `confounded_source_clock`；纯 provider effect、five-carrier clock effect 没有被识别。

没有独立外生 regime label，因此 common-time factor 不能被称作已识别的 causal regime effect。V1 state-conditional residual strength 只能是描述性统计，因为 state 来源于同一个 slope_t。

## 当前结论

```text
60M_CARRIER_SCALE_EFFECT              = SUPPORTED
60M_COMMON_TIME_SCALE_EFFECT          = SUPPORTED
CARRIER_TIME_INTERACTION              = MATERIAL / UNRESOLVED
CROSS_CARRIER_NORMALIZED_STRENGTH     = SUPPORTED RESEARCH DIAGNOSTIC ONLY
STABLE_TEMPORAL_NORMALIZED_STRENGTH   = NOT ESTABLISHED
CAUSAL_STATE_BOUNDARY_NORMALIZATION   = NOT SUPPORTED
INDEPENDENT_REGIME_EFFECT             = NOT IDENTIFIED
PURE_PROVIDER_EFFECT                  = NOT IDENTIFIED
CURRENT_DECISION                      = INSUFFICIENT_EVIDENCE
V1                                    = NO CHANGE
X6                                    = HOLD / NOT READY
```

下一步若继续，应优先研究 **carrier×time interaction、causal common-scale estimator、same-clock cross-provider 与更多 same-provider multi-clock 数据**。不要再通过调 T1 或让 normalization 改写 DOWN/SIDEWAYS/UP 来“解决”60m scale 问题。

## 仍然禁止

- 重跑 M5 primary / T2 sensitivity / STAR50 replication；
- 打开旧 M4/M5 2025 Holdout；
- 修改冻结的 M6/M7/M8/M9 semantics；
- 把 public/native-clock research source 写成 runtime admitted 或 DataHub exact identity；
- 输出 `global_state`、BUY/SELL、position/order、strategy selection/routing；
- 把 `production_authority=false` 或 `fresh_oos=false` 改成 true。

历史 V1 snapshots 永不原地改写。未来任何 T1、lookback、estimator、strength semantics 改动都必须经过新的版本化 representation decision。
