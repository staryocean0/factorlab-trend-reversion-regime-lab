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
- X5K — **sparse / hysteretic scale update COMPLETE / NO GATE-QUALIFIED CANDIDATE**
- X5L — **partial-reset / cooldown COMPLETE / ANCHORED PARTIAL PASSES 6 OF 7 GATES / NO ADOPTION**
- X6 — **HOLD / NOT READY**

V1 release pointer `release/trend-regime-v1.0.0` 必须继续固定在 `5a563d87d1628379e0d9a04aa7c5500bc30c4bc2`。

## 接管必读

- `docs/ROADMAP.md`
- `docs/governance/TREND_X5L_PARTIAL_RESET_COOLDOWN_STRENGTH_SCALE_PROTOCOL_V1.json`
- `docs/governance/TREND_X5L_PARTIAL_RESET_COOLDOWN_STRENGTH_SCALE_RESULT_V1.json`
- `docs/governance/TREND_X5L_POSTHOC_INTERACTION_DIAGNOSTIC_V1.json`
- `docs/governance/TREND_X4_POST_X5L_UPDATE_V1.json`
- `docs/governance/TREND_X5K_SPARSE_HYSTERETIC_STRENGTH_SCALE_RESULT_V1.json`
- `docs/governance/TREND_X5J_TURNOVER_REGULARIZED_STRENGTH_SCALE_RESULT_V1.json`
- `docs/governance/TREND_X5I_PROSPECTIVE_FAST_VS_ADAPTIVE_STRENGTH_SCALE_RESULT_V1.json`
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

## X5L 最新结论

X5L 沿用 X5K 的七项 gate，不再调整阈值或做参数网格搜索。Tencent 为 primary，Sina 为同窗 cross-provider replication。

预注册 stateful 候选：

```text
PARTIAL_PERSIST2_GAP0P10_F0P50_COOLDOWN2
PARTIAL_DEADBAND0P12_F0P50_COOLDOWN2
ANCHORED_PARTIAL_DB0P12_F0P50_COOLDOWN2_SLOW25
```

Tencent 结果：

```text
PARTIAL_PERSIST2_GAP0P10_F0P50_COOLDOWN2
  range reduction      91.46%
  temporal improvement 23.92%
  breadth              4/5
  interaction improve  29.27%
  mean / q95 turnover  1.55x / 2.36x
  update fraction      23.2%
  result               FAIL (q95 jump)

PARTIAL_DEADBAND0P12_F0P50_COOLDOWN2
  range reduction      93.75%
  temporal improvement 23.98%
  breadth              4/5
  interaction improve  31.91%
  mean / q95 turnover  1.77x / 2.47x
  update fraction      31.7%
  result               FAIL (q95 jump)

ANCHORED_PARTIAL_DB0P12_F0P50_COOLDOWN2_SLOW25
  range reduction      92.06%
  temporal improvement 17.28%
  breadth              4/5
  interaction improve  18.54%
  mean / q95 turnover  1.38x / 1.88x
  update fraction      31.7%
  result               FAIL (interaction only)
```

Sina 几乎逐项复现。Anchored partial 是目前最接近稳定 normalized-strength 的研究候选：它在两个 provider 上都通过 6/7 gate，唯一未过的是预注册 interaction improvement `>=20%`，实际约 18.54%。不得因为只差约 1.46 个百分点就放宽 gate 或在当前 outcomes 上调整 25% slow anchor、50% partial fraction、0.12 trigger 或 cooldown=2。

Post-hoc diagnostic 只解释失败：Tencent / Sina 都由 2026-06 STAR50 最大 cell 与 CSI300 最小 cell 定义剩余 interaction；它不参与 primary selection。

因此：

```text
TENCENT_QUALIFIED_CANDIDATES        = []
SINA_QUALIFIED_CANDIDATES           = []
CROSS_PROVIDER_QUALIFIED_CANDIDATES = []
SELECTED_CANDIDATE                  = NONE
```

下一步若继续，优先级不再是继续调参，而是**冻结 anchored-partial 机制原样，寻找结构上新的时间窗口 / regime 做验证**。只有新的独立证据仍显示接近或跨过全部 gate，才有资格讨论参数修订或未来 representation decision。

## 历史回归锚点

以下字符串仅为 fail-closed 文档回归锚点，不代表当前采用：

```text
NO_CHANGE
ADAPT_DUAL_BLEND_1P5
FAST_COMMON5_CARRIER20
FAST_EWMA_A0P35
EVENT_PERSIST2_0P10_FULL
```

## 当前结论

```text
SHORT_MEMORY_SCALE_BENEFIT                  = REPLICATED
SCALE_TURNOVER_CONCERN                      = PROSPECTIVELY CONFIRMED
SIMPLE_CHANGE_RATE_CAP                      = NOT SUPPORTED
SIMPLE_EWMA                                 = NOT SUPPORTED
SIMPLE_DEADBAND                             = NOT SUPPORTED
PERSISTENCE_ONLY_SPARSE_UPDATE              = NOT SUPPORTED
SIMPLE_HYSTERETIC_EWMA                      = NOT SUPPORTED
PARTIAL_RESET_COOLDOWN                      = PROMISING BUT NO GATE-QUALIFIED CANDIDATE
ANCHORED_PARTIAL_6_OF_7_GATES               = RESEARCH NEAR-CANDIDATE ONLY
STABLE_TEMPORAL_PRODUCT_STRENGTH            = NOT ESTABLISHED
CURRENT_DECISION                            = INSUFFICIENT_EVIDENCE
V1                                          = NO CHANGE
X6                                          = HOLD / NOT READY
```

## 仍然禁止

- 重跑 M5 primary / T2 sensitivity / STAR50 replication；
- 打开旧 M4/M5 governed 2025 Holdout；
- 修改冻结的 M6/M7/M8/M9 semantics；
- 把 public/native-clock research source 写成 runtime admitted 或 DataHub exact identity；
- 输出 `global_state`、BUY/SELL、position/order、strategy selection/routing；
- 在 X5L outcomes 上调 anchor weight、partial fraction、trigger、cooldown 或 gate；
- 把 `production_authority=false` 或 `fresh_oos=false` 改成 true。

历史 V1 snapshots 永不原地改写。未来任何 T1、lookback、estimator、strength semantics 改动都必须经过新的版本化 representation decision。
