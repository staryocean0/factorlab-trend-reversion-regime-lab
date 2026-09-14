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
- X4 calibration-family decision — **`INSUFFICIENT_EVIDENCE` / NO V1 CHANGE**
- X5 / X5B — **5m replication + source robustness COMPLETE**
- X5C — **15m/60m cross-carrier COMPLETE**
- X5D — **static calibration COMPLETE / NO ADOPTION**
- X5E — **causal rolling normalization COMPLETE / NO ADOPTION**
- X5F — **60m carrier × common-time scale decomposition COMPLETE / DIAGNOSTIC ONLY**
- X5G — **dynamic common scale + slow carrier interaction study COMPLETE / DIAGNOSTIC ONLY**
- X6 — **HOLD / NOT READY**

V1 release pointer `release/trend-regime-v1.0.0` 必须继续固定在 `5a563d87d1628379e0d9a04aa7c5500bc30c4bc2`；Post-V1 research commits 不得移动它。

## 接管必读

- `docs/ROADMAP.md`
- `docs/governance/TREND_X5F_60M_STRENGTH_SCALE_DECOMPOSITION_RESULT_V1.json`
- `docs/governance/TREND_X5G_DYNAMIC_COMMON_SCALE_CARRIER_INTERACTION_PROTOCOL_V1.json`
- `docs/governance/TREND_X5G_DYNAMIC_COMMON_SCALE_CARRIER_INTERACTION_RESULT_V1.json`
- `docs/governance/TREND_X4_POST_X5G_UPDATE_V1.json`
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

## 到 X5F 已知的 60m scale 结构

X5F 用五指数 × 2026-01..09 monthly `median(abs(slope_t))` 得到：

```text
log(scale) = grand + carrier_effect + common_time_effect + residual
```

描述性 log-cell variance fractions：carrier ≈ **27.4%**，common-time ≈ **32.4%**，residual / carrier×time interaction ≈ **40.2%**。

Jan–Apr → May–Sep leave-one-carrier-out 可将 carrier median-strength range 从约 **1.470** 压到 **0.270**（约 -81.6%），说明 normalized_strength 的 cross-carrier 对齐不是纯样本内假象。但 residual cell factor max/min 仍约 **2.408×**，stable temporal representation 未建立。

## X5G：Dynamic Common Scale & Carrier-Time Interaction

X5G 在计算前冻结四个严格因果候选：

```text
COMMON20_CARRIER120
COMMON40_CARRIER120
COMMON40_CARRIER240
COMMON80_CARRIER240
```

对 carrier `i`，common factor 只用另外四个 carrier 的历史；common 和 carrier component 都只能使用 `t-1` 及更早数据。统一 warmup = **320 measurements**，共同评价窗口 **2026-05-15 15:00 至 2026-09-14 15:00**，每 carrier **341 measurements**。

### 横截面对齐继续成立

同窗 raw carrier median-strength range = **1.4847**。四个候选的 range reduction 都在约 **80.2%–85.9%**：

```text
COMMON20_CARRIER120   80.15%
COMMON40_CARRIER120   85.74%
COMMON40_CARRIER240   85.94%
COMMON80_CARRIER240   80.56%
```

因此“common scale + carrier component 可显著改善 cross-carrier strength alignment”在 strictly-causal 版本下再次得到支持。

### 但 stable temporal representation 仍未建立

预注册 gate 要求同时满足 cross-carrier、temporal、breadth、interaction 四项。**没有候选全部通过。**

最接近的是 `COMMON20_CARRIER120`：

- cross-carrier range reduction ≈ **80.15%** — PASS；
- median within-carrier monthly max/min：raw **3.3912× → 2.1657×**，约改善 **36.1%** — PASS；
- 4/5 carrier temporal ratio 改善 — PASS；
- residual monthly-cell max/min = **4.1675×**，高于 X5F **2.4080×** — FAIL。

40/80 common window 或 240 carrier window 的 temporal stability 更差，说明简单延长 fixed rolling window 会产生 regime-shift lag，并不能解决 interaction。

统一评价的第一个月从 2026-05-15 开始；按预注册最小样本规则必须纳入 primary decision。事后只看完整 2026-06..09，`COMMON20_CARRIER120` 的 median temporal ratio 是 **1.6040×**，raw 是 **1.6006×**，基本没有改善；monthly-cell ratio 则从 **2.7612×** 降到 **2.2826×**。因此 primary-window temporal improvement 很大一部分来自对 5 月 scale shift 的处理。这只是 post-hoc diagnostic，不改主结论。

## 当前结论

```text
60M_CARRIER_SCALE_EFFECT                   = SUPPORTED
60M_COMMON_TIME_SCALE_EFFECT               = SUPPORTED
CARRIER_TIME_INTERACTION                   = MATERIAL / UNRESOLVED
CROSS_CARRIER_NORMALIZED_STRENGTH          = SUPPORTED RESEARCH DIAGNOSTIC ONLY
DYNAMIC_COMMON_PLUS_CARRIER_NORMALIZATION  = CROSS-CARRIER SUPPORTED
STABLE_TEMPORAL_NORMALIZED_STRENGTH        = NOT ESTABLISHED
FIXED_WINDOW_INTERACTION_RESOLUTION        = NOT SUPPORTED
CAUSAL_STATE_BOUNDARY_NORMALIZATION        = NOT SUPPORTED
CURRENT_DECISION                           = INSUFFICIENT_EVIDENCE
V1                                         = NO CHANGE
X6                                         = HOLD / NOT READY
```

下一步若继续，不应再调 T1，也不应继续单纯增加 rolling window。优先研究 **strength-only adaptive / change-point-aware regime-shift response**，并继续禁止 normalized_strength 改写 DOWN/SIDEWAYS/UP。

## 仍然禁止

- 重跑 M5 primary / T2 sensitivity / STAR50 replication；
- 打开旧 M4/M5 2025 Holdout；
- 修改冻结的 M6/M7/M8/M9 semantics；
- 把 public/native-clock research source 写成 runtime admitted 或 DataHub exact identity；
- 输出 `global_state`、BUY/SELL、position/order、strategy selection/routing；
- 把 `production_authority=false` 或 `fresh_oos=false` 改成 true。

历史 V1 snapshots 永不原地改写。未来任何 T1、lookback、estimator、strength semantics 改动都必须经过新的版本化 representation decision。
