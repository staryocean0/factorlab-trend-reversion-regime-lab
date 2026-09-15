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

Post-V1 Cross-Profile Invariance & Calibration Study 是独立研究线，不是自动 M10，不修改 V1。

当前研究进度：

- X1–X3 — **COMPLETE**
- X4 — **`INSUFFICIENT_EVIDENCE` / NO V1 CHANGE**
- X5 / X5B — **5m replication + source robustness COMPLETE**
- X5C — **15m/60m cross-carrier COMPLETE**
- X5D — **static calibration COMPLETE / NO ADOPTION**
- X5E — **causal rolling normalization COMPLETE / NO ADOPTION**
- X5F — **60m carrier × common-time decomposition COMPLETE / DIAGNOSTIC ONLY**
- X5G — **dynamic common + slow carrier COMPLETE / DIAGNOSTIC ONLY**
- X5H — **dual blend became prospective research candidate, NO ADOPTION**
- X5I — **independent-source prospective validation COMPLETE / NO CANDIDATE PASSES TURNOVER-AWARE GATES**
- X5J — **turnover-regularized scale COMPLETE / NO GATE-QUALIFIED CANDIDATE**
- X6 — **HOLD / NOT READY**

V1 release pointer `release/trend-regime-v1.0.0` 必须继续固定在 `5a563d87d1628379e0d9a04aa7c5500bc30c4bc2`。

## 接管必读

- `docs/ROADMAP.md`
- `docs/governance/TREND_X5J_TURNOVER_REGULARIZED_STRENGTH_SCALE_PROTOCOL_V1.json`
- `docs/governance/TREND_X5J_TURNOVER_REGULARIZED_STRENGTH_SCALE_RESULT_V1.json`
- `docs/governance/TREND_X5J_POSTHOC_UPDATE_FREQUENCY_DIAGNOSTIC_V1.json`
- `docs/governance/TREND_X4_POST_X5J_UPDATE_V1.json`
- `docs/governance/TREND_X5I_PROSPECTIVE_FAST_VS_ADAPTIVE_STRENGTH_SCALE_RESULT_V1.json`
- `docs/governance/TREND_X4_POST_X5I_UPDATE_V1.json`
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

## 到 X5I 已知什么

X5I 在独立 Tencent native 60m provider 上 prospectively 复制了 short-memory scale 的好处，也正式确认了 turnover 风险：

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

因此 short-memory scale 的 alignment benefit 与 high-turnover cost 都已跨 provider 复制；但没有稳定产品 `normalized_strength`。

## X5J：Turnover-Regularized Strength Scale

X5J 利用已知的 turnover 问题做开发型研究，明确 `fresh_oos=false`，不做参数网格搜索。候选在统计前冻结：

```text
SLOW_COMMON20_CARRIER120
FAST_COMMON5_CARRIER20
ADAPT_DUAL_BLEND_1P5
FAST_CAP_0P06
FAST_EWMA_A0P35
DUAL_CAP_0P06
```

Primary 开发源仍是 Tencent native 60m，同窗 Sina 做 cross-provider replication。所有候选继续同时要求 cross-carrier、temporal、breadth、interaction、median turnover、q95 turnover 六项 gate。

### 结果

Tencent：

```text
slow 20/120
  range reduction      84.57%
  temporal improvement 10.85%
  breadth              2/5
  turnover             1.00× / 1.00×
  result               FAIL

fast 5/20
  range reduction      93.84%
  temporal improvement 23.87%
  breadth              5/5
  interaction improve  37.95%
  turnover             3.39× / 2.11×
  result               FAIL

dual blend
  range reduction      93.75%
  temporal improvement 22.97%
  breadth              5/5
  interaction improve  36.25%
  turnover             3.21× / 2.21×
  result               FAIL

FAST_CAP_0P06
  range reduction      88.73%
  temporal improvement -0.61%
  breadth              2/5
  interaction improve  2.37%
  turnover             1.73× / 0.25×
  result               FAIL

FAST_EWMA_A0P35
  range reduction      92.44%
  temporal improvement 25.06%
  breadth              4/5
  interaction improve  34.06%
  turnover             3.46× / 1.34×
  result               FAIL

DUAL_CAP_0P06
  range reduction      84.43%
  temporal improvement -0.03%
  breadth              2/5
  interaction improve  3.51%
  turnover             1.73× / 0.25×
  result               FAIL
```

Sina replication 几乎逐项一致，也没有任何候选通过全部 gate：

```text
TENCENT_QUALIFIED_CANDIDATES        = []
SINA_QUALIFIED_CANDIDATES           = []
CROSS_PROVIDER_QUALIFIED_CANDIDATES = []
SELECTED_CANDIDATE                  = NONE
```

### 为什么 cap / EWMA 没解决问题

`CAP_0.06` 在 post-hoc update-frequency diagnostic 中 q10 到 q95 的 `|Δlog(scale)|` **全部等于 0.06**。这说明目标长期远离当前 scale，cap 几乎每根都被打满；它变成了持续 catch-up，降低尾部 turnover 的同时制造响应滞后。

`EWMA α=0.35` 则保留了 scale alignment，q95 turnover 也从 fast 的约 2.11× slow 降到约 1.34×，但 median turnover 仍约 3.46×。它把大跳摊成了频繁中等更新，降低尾部但没有降低更新频率。

因此 X5J 的结论不是“再把 cap 调小一点”或“再把 α 调低一点”，而是：**连续型 regularization 暂时无法同时得到 fast-scale responsiveness 与 slow-scale low-turnover。** 下一步如继续，应研究 deadband / hysteresis / sparse event-driven causal updates，并把 update frequency 与 turnover 都预注册为 gate。

## 当前结论

```text
SHORT_MEMORY_SCALE_BENEFIT                = REPLICATED
SCALE_TURNOVER_CONCERN                    = PROSPECTIVELY CONFIRMED
SIMPLE_CHANGE_RATE_CAP                    = NOT SUPPORTED
SIMPLE_EWMA                               = NOT SUPPORTED
CONTINUOUS_TURNOVER_REGULARIZATION        = NO GATE-QUALIFIED CANDIDATE
STABLE_TEMPORAL_PRODUCT_STRENGTH          = NOT ESTABLISHED
CURRENT_DECISION                          = INSUFFICIENT_EVIDENCE
V1                                        = NO CHANGE
X6                                        = HOLD / NOT READY
```

## 仍然禁止

- 重跑 M5 primary / T2 sensitivity / STAR50 replication；
- 打开旧 M4/M5 governed 2025 Holdout；
- 修改冻结的 M6/M7/M8/M9 semantics；
- 把 public/native-clock research source 写成 runtime admitted 或 DataHub exact identity；
- 输出 `global_state`、BUY/SELL、position/order、strategy selection/routing；
- 把 `production_authority=false` 或 `fresh_oos=false` 改成 true。

历史 V1 snapshots 永不原地改写。未来任何 T1、lookback、estimator、strength semantics 改动都必须经过新的版本化 representation decision。
