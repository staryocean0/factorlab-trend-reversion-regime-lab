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

当前研究进度：X1–X5M 已执行；X4 总体仍为 `INSUFFICIENT_EVIDENCE / NO_CHANGE`；X6 **HOLD / NOT READY**。

V1 release pointer `release/trend-regime-v1.0.0` 必须继续固定在 `5a563d87d1628379e0d9a04aa7c5500bc30c4bc2`。

## V1 正式产品

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

Runtime admission 仍只有 `000852.SH` / `000688.SH` 的 1m official 与 5m offset0。Post-V1 public/native-clock research 数据不获得 admission。

## X5L → X5M

X5L 的 `ANCHORED_PARTIAL_DB0P12_F0P50_COOLDOWN2_SLOW25` 在 Tencent/Sina 的 2026-06/07/08 同窗上曾达到 **6/7 gate**，唯一失败 interaction≈18.54% < 20%；因此只作为 research near-candidate，未采纳。

X5M 将该候选**原样冻结**，没有调整 slow anchor 25%、partial fraction 50%、trigger 0.12、cooldown=2 或任何 gate，并做两个结构块验证：

- Block A：Sina native 60m，2025-11 / 12 + 2026-01；public-native 2025 行此前未进入候选统计，且不是旧 M4/M5 governed Holdout。结果 **5/7**，失败 temporal 与 q95 turnover。
- Block B：Tencent + Sina native 60m，2026-03 / 04 / 05。两源结果同步为 **6/7**，但 interaction improvement≈**-11.15%**，相对 slow baseline 反而恶化。

因此：

```text
X5M_STRUCTURAL_GENERALIZATION       = NOT ESTABLISHED
ANCHORED_PARTIAL_PROMOTION          = REJECTED
RETUNE_ON_X5M_OUTCOMES              = FORBIDDEN
STABLE_NORMALIZED_STRENGTH          = NOT ESTABLISHED
V1                                  = NO CHANGE
X6                                  = HOLD / NOT READY
```

接管必读：

- `docs/governance/TREND_X5M_FROZEN_ANCHORED_STRUCTURAL_VALIDATION_PROTOCOL_V1.json`
- `docs/governance/TREND_X5M_FROZEN_ANCHORED_STRUCTURAL_VALIDATION_RESULT_V1.json`
- `docs/governance/TREND_X5M_POSTHOC_STRUCTURAL_FAILURE_DIAGNOSTIC_V1.json`
- `docs/governance/TREND_X4_POST_X5M_UPDATE_V1.json`
- `docs/ROADMAP.md`

## 历史回归锚点

以下字符串仅用于 fail-closed 文档回归，不代表当前采用：

```text
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
- 基于 X5L/X5M outcomes 继续调整 anchor、partial fraction、trigger、cooldown 或 gate；
- 把 `production_authority=false` 或 `fresh_oos=false` 改成 true。

历史 V1 snapshots 永不原地改写。未来任何 T1、lookback、estimator、strength semantics 改动都必须经过新的版本化 representation decision。
