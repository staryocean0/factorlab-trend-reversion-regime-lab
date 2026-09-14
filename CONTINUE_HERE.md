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
- X2 distributional invariance + preregistered sensitivity — **COMPLETE**
- X3 state-dynamics invariance — **COMPLETE**
- X4 calibration-family decision — **`INSUFFICIENT_EVIDENCE` / NO V1 CHANGE**
- X5 five-carrier 5m replication — **COMPLETE**
- X5B 5m source robustness — **COMPLETE**
- X5C five-carrier 15m/60m + long-window 60m — **COMPLETE**
- X5D static interval-specific T1 vs static robust normalization — **COMPLETE / NO ADOPTION**
- X5E 60m temporal scale + causal rolling normalization — **COMPLETE / NO ADOPTION**
- X6 representation version decision — **HOLD / NOT READY**

V1 release pointer `release/trend-regime-v1.0.0` 必须继续固定在 `5a563d87d1628379e0d9a04aa7c5500bc30c4bc2`；Post-V1 research commits 不得移动它。

## 接管必读

- `docs/ROADMAP.md`
- `docs/governance/TREND_CROSS_PROFILE_INVARIANCE_PROTOCOL_V1.json`
- `docs/governance/TREND_X5C_15M_60M_CROSS_CARRIER_RESULT_V1.json`
- `docs/governance/TREND_X5D_INTERVAL_CALIBRATION_COMPARISON_RESULT_V1.json`
- `docs/governance/TREND_X5E_60M_TEMPORAL_SCALE_CAUSAL_NORMALIZATION_PROTOCOL_V1.json`
- `docs/governance/TREND_X5E_60M_TEMPORAL_SCALE_CAUSAL_NORMALIZATION_RESULT_V1.json`
- `docs/governance/TREND_X4_POST_X5E_UPDATE_V1.json`
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

## Post-V1 核心结论

### 5m 与 phase

5m 是目前最稳的一层。五指数 replication 中 SIDEWAYS occupancy range ≈ **3.13pp**，one-step self-transition range ≈ **1.23–1.87pp**；Sina vs Eastmoney 在 CSI1000/STAR50 上三桶状态 **100% 一致**。同 interval 的不同 phase 差异也显著小于跨 interval 差异。因此当前没有证据要求 5m carrier-specific / phase-specific / provider-specific T1。

### 15m 与 60m

X5C 显示 15m 相对稳定，而 60m 的 carrier heterogeneity 在长窗口下仍明显。60m 使用 2026-01-05 至 2026-09-14，五个 carrier 各 661 measurements，最小 directional origins = **181**，所以早先的 underpower 已解除。固定 V1 `20-bar slope_t / T1=2` 时，60m SIDEWAYS occupancy cross-carrier range ≈ **12.41pp**，survival5 DOWN/UP range ≈ **14.75pp / 10.44pp**。

### X5D：静态 calibration 不采纳

2020 Development 拟合曾同时指向更低的 60m raw-equivalent boundary（interval T1 ≈ **1.2225**；median-abs normalization ≈ **1.2701**），但 2026 五指数外部评价出现 persistence/reversal trade-off，候选无严格 Pareto dominance，因此不修改 V1。

### X5E：60m temporal scale nonstationarity 已得到支持

X5E 只用 X5C retained Sina 60m 的 **2026-01-05 至 2026-09-14** 行；源文件中其它年份的公共行情行不参与统计，旧 M4/M5 governed 2025 Holdout 未读取。

五指数 monthly `median(abs(slope_t))` 最大/最小比：

```text
CSI1000  ≈ 2.50x
STAR50   ≈ 2.76x
CSI300   ≈ 3.32x
CSI500   ≈ 1.61x
SSE50    ≈ 1.63x
```

因此 60m raw score scale 在该 2026 窗口具有明显时间变化，不能把一个静态 scale 当成已证明全年稳定。

X5E 预注册了严格 causal rolling median-abs scale，窗口 **40 / 80 / 120** 个既往 60m scores；时点 `t` 只能使用 `t-1` 及更早信息。normalized threshold 固定来自 X5D 2020 Development 的 `0.44780633341059867`，没有利用 2026 再拟合。

共同 120-score warmup 后，五个 carrier 都在 **2026-03-02 15:00 至 2026-09-14 15:00** 的 541 个 measurements 上公平比较。cross-carrier median-strength range 从 raw **1.4307** 降至：

- 40-bar：**0.1052**（约 -92.7%）
- 80-bar：**0.0778**（约 -94.6%）
- 120-bar：**0.0573**（约 -96.0%）

这说明 causal scale 对 cross-carrier strength-level alignment 很有效。

但它没有解决 within-carrier temporal drift。五指数的月度 median-strength max/min ratio 中位数：

```text
V1 raw           ≈ 1.694
causal 40        ≈ 1.689
causal 80        ≈ 2.056
causal 120       ≈ 1.990
```

同时，作为动态 state boundary 时：40/120 各 **5 个语义 dispersion 改善 / 3 个恶化**，80 为 **3 改善 / 5 恶化**；无候选严格 Pareto-dominates V1。恶化主要落在 SIDEWAYS self-transition 与 opposite-entry10。

所有候选的 DOWN↔UP disagreement vs V1 都是 **0**；变化只发生 directional ↔ SIDEWAYS，但状态改写比例可达约 **2.4%–12.8%**。因此不能把 causal normalization 升级为新的 state boundary。

## 当前结论

```text
UNIVERSAL_FIXED_T1                  = current V1 baseline, not a proven universal law
STATIC_INTERVAL_SPECIFIC_T1         = not supported for adoption
STATIC_NORMALIZED_SCORE             = not supported for adoption
CAUSAL_STATE_BOUNDARY_NORMALIZATION = not supported for adoption
CAUSAL_STRENGTH_SCALE_NORMALIZATION = promising cross-carrier diagnostic only
TEMPORAL_STABILITY                  = not established
CURRENT_DECISION                    = INSUFFICIENT_EVIDENCE
X6                                  = HOLD / NOT READY
```

下一步如果继续研究，优先考虑 **strength-only temporal scale estimator** 或 **carrier × time/regime × clock/source scale decomposition**。在未来候选没有达到预注册的 state-semantic non-inferiority 前，不再让 normalization 改写 DOWN/SIDEWAYS/UP 边界。

## 仍然禁止

- 重跑 M5 primary / T2 sensitivity / STAR50 replication；
- 打开旧 M4/M5 2025 Holdout；
- 修改冻结的 M6/M7/M8/M9 semantics；
- 把 public/native-clock research source 写成 runtime admitted 或 DataHub exact identity；
- 输出 `global_state`、BUY/SELL、position/order、strategy selection/routing；
- 把 `production_authority=false` 或 `fresh_oos=false` 改成 true。

历史 V1 snapshots 永不原地改写。未来任何 T1、lookback、estimator、strength semantics 改动都必须经过新的版本化 representation decision。
