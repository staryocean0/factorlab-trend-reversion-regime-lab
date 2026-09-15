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

当前研究进度：X1–X5O 已执行；X4 总体仍为 `INSUFFICIENT_EVIDENCE / NO_CHANGE`；X6 **HOLD / NOT READY**。

V1 release pointer `release/trend-regime-v1.0.0` 必须继续固定在 `5a563d87d1628379e0d9a04aa7c5500bc30c4bc2`。

## V1 正式产品

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

Runtime admission 仍只有 `000852.SH` / `000688.SH` 的 1m official 与 5m offset0。Post-V1 public/native-clock research 数据不获得 admission。

## X5N → X5O

X5N 已确认：normalization failure 具有明显 `MARKET_REGIME_CONDITIONALITY`，且 Mar–May 的失败包含 `000016.SH` carrier-specific regime interaction；peer composition、median-vs-mean common estimator 均不是主要解释，clock 对主失败不可识别。

X5O 随后没有开发新 normalization 参数，而是测试能否用**独立于 slope_t / state 的严格因果 return-geometry observable**事前识别 failure zones。候选及 threshold 在评价前冻结：

```text
COMMON_VOL_SHIFT
XS_VOL_SHIFT_DISPERSION
CORRELATION_BREAK
SSE50_RELATIVE_VOL_SHIFT
```

threshold 只来自 2025-09/10 reference months 的 80th percentile；评价块完全不参与阈值生成。

正式结果：

```text
COMMON_REGIME_OBSERVABLE_IDENTIFIED        = false
SSE50_CARRIER_REGIME_OBSERVABLE_IDENTIFIED = false
common alert rho vs q95 severity            ≈ 0.405
000016 alert rho vs normalized ratio        ≈ 0.491
000016 alert rho vs interaction loss        ≈ 0.169
```

`CORRELATION_BREAK` 是唯一明显的 diagnostic clue：threshold-free rho vs q95 severity≈0.833，但首个 structural failure block alert fraction≈37.3%，未达到预注册 50% coverage gate。Tencent/Sina 的 2026 连续 observable Pearson≈0.99999994，因此该弱信号不是 provider artifact，但也没有资格变成 regime switch。

因此：

```text
REGIME_CONDITIONALITY_EXISTS         = SUPPORTED
CAUSAL_REGIME_IDENTIFIABILITY        = NOT ESTABLISHED
REGIME_SWITCH_RULE                   = NOT AUTHORIZED
UNIFIED_DYNAMIC_NORMALIZED_STRENGTH  = PAUSE DEVELOPMENT
RETUNE_ON_X5O_OUTCOMES               = FORBIDDEN
V1                                   = NO CHANGE
X6                                   = HOLD / NOT READY
```

接管必读：

- `docs/governance/TREND_X5O_CAUSAL_REGIME_OBSERVABLE_IDENTIFIABILITY_PROTOCOL_V1.json`
- `docs/governance/TREND_X5O_CAUSAL_REGIME_OBSERVABLE_IDENTIFIABILITY_RESULT_V1.json`
- `docs/governance/TREND_X5O_POSTHOC_OBSERVABLE_SOURCE_AGREEMENT_V1.json`
- `docs/governance/TREND_X4_POST_X5O_UPDATE_V1.json`
- `docs/governance/TREND_X5N_STRUCTURAL_FAILURE_ATTRIBUTION_RESULT_V1.json`
- `docs/ROADMAP.md`

下一步不应继续在现有 outcomes 上找 observable threshold 或切换逻辑。只有新的外生 regime 信息、000016 独立 alternate-clock 证据，或者完全新的且事前冻结的结构假设，才值得重启 normalized_strength representation 研究。

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
CLOCK_STRUCTURE
RETUNE_ON_X5N_OUTCOMES
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
- 基于 X5O outcomes 搜索新的 observable threshold、alert combination 或 regime-switched normalization；
- 把 `production_authority=false` 或 `fresh_oos=false` 改成 true。

历史 V1 snapshots 永不原地改写。未来任何 T1、lookback、estimator、strength semantics 改动都必须经过新的版本化 representation decision。
