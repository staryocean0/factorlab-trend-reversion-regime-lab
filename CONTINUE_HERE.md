# 从这里接管

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 当前状态

本仓是 Layer 2 趋势状态识别组件，不是交易策略。**M0–M9 PASS**；V1 release 已冻结。Post-V1 是独立研究线，不是自动 M10。

当前研究进度：X1–X5N 已执行；X4 总体仍为 `INSUFFICIENT_EVIDENCE / NO_CHANGE`；X6 **HOLD / NOT READY**。

V1 release pointer `release/trend-regime-v1.0.0` 必须继续固定在 `5a563d87d1628379e0d9a04aa7c5500bc30c4bc2`。

## V1 正式产品

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

Runtime admission 仍只有 `000852.SH` / `000688.SH` 的 1m official 与 5m offset0。Post-V1 public/native-clock research 数据不获得 admission。

## X5M → X5N

X5M 将 `ANCHORED_PARTIAL_DB0P12_F0P50_COOLDOWN2_SLOW25` 原样冻结后做结构验证：Block A 为 5/7，Block B 为 6/7 且 interaction≈-11.15%，因此 structural generalization 未建立，禁止基于 X5M outcomes retune。

X5N 不再找参数，只归因。结果：

- rolling 三个月窗口显示 failure pattern 明显随时间切换；早期主要失败 temporal，Mar–Jul 转为 interaction 主导，`MARKET_REGIME_CONDITIONALITY=SUPPORTED`。
- 早期 Block A 五个 carrier 的 q95 turnover 都 >2x slow，同时 common raw strength 从约 3.81 下行到 2.99，说明早期 temporal/q95 failure 是 broad regime-transition / controller response，不是单一 carrier 拖累。
- Mar–May 中，四个非上证50 carrier 的 temporal improvement 约 19%–31%，但 `000016.SH` 从 raw ratio≈1.296 恶化到 normalized≈2.423，`CARRIER_SPECIFIC_REGIME_INTERACTION_000016=SUPPORTED`。
- 对 000016 的 peer jackknife 后 ratio 仍约 2.11–2.48，carrier composition 不支持为主要驱动。
- peer median 改成 peer mean 后 ratio 仅改善约 4.4%，interaction 约 -18%，median-vs-mean common estimator 不支持为主要驱动。
- 当前没有 000016 同窗 alternate 60m clock；`CLOCK_STRUCTURE=NOT_IDENTIFIABLE`。

因此：

```text
SINGLE_UNIFIED_STATEFUL_NORMALIZATION_LAW = NOT ESTABLISHED
RETUNE_ON_X5N_OUTCOMES                    = FORBIDDEN
STABLE_NORMALIZED_STRENGTH                 = NOT ESTABLISHED
V1                                         = NO CHANGE
X6                                         = HOLD / NOT READY
```

接管必读：

- `docs/governance/TREND_X5N_STRUCTURAL_FAILURE_ATTRIBUTION_PROTOCOL_V1.json`
- `docs/governance/TREND_X5N_STRUCTURAL_FAILURE_ATTRIBUTION_RESULT_V1.json`
- `docs/governance/TREND_X4_POST_X5N_UPDATE_V1.json`
- `docs/governance/TREND_X5M_FROZEN_ANCHORED_STRUCTURAL_VALIDATION_RESULT_V1.json`
- `docs/ROADMAP.md`

下一步如果继续，不应再修 X5L 参数；应先提出新的结构假设，最自然的是 **regime-conditional normalized_strength representation**，或者先取得 000016 的独立 alternate-clock 证据。新假设必须在看 outcomes 前单独冻结。

## 历史回归锚点

以下字符串仅用于 fail-closed 文档回归，不代表当前采用；其中 X5F 的历史结论是 cross-carrier diagnostic 有价值但 stable temporal representation 未建立。

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

## 仍然禁止

- 重跑 M5 primary / T2 sensitivity / STAR50 replication；
- 打开旧 M4/M5 governed 2025 Holdout；
- 修改冻结的 M6/M7/M8/M9 semantics；
- 把 public/native-clock research source 写成 runtime admitted 或 DataHub exact identity；
- 输出 `global_state`、BUY/SELL、position/order、strategy selection/routing；
- 基于 X5L/X5M/X5N outcomes 继续调整 anchor、partial fraction、trigger、cooldown 或 gate；
- 把 `production_authority=false` 或 `fresh_oos=false` 改成 true。

历史 V1 snapshots 永不原地改写。未来任何 T1、lookback、estimator、strength semantics 改动都必须经过新的版本化 representation decision。
