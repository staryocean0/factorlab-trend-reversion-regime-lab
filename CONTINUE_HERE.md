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
- X6 — **HOLD / NOT READY**

V1 release pointer `release/trend-regime-v1.0.0` 必须继续固定在 `5a563d87d1628379e0d9a04aa7c5500bc30c4bc2`。

## 接管必读

- `docs/ROADMAP.md`
- `docs/governance/TREND_X5I_PROSPECTIVE_FAST_VS_ADAPTIVE_STRENGTH_SCALE_PROTOCOL_V1.json`
- `docs/governance/TREND_X5I_EASTMONEY_SOURCE_BLOCK_RECEIPT_V1.json`
- `docs/governance/TREND_X5I_SOURCE_RECOVERY_PROTOCOL_V1.json`
- `docs/governance/TREND_X5I_TENCENT_DEPTH_EXTENSION_RECEIPT_V1.json`
- `docs/governance/TREND_X5I_EVALUATION_METHOD_V1.json`
- `docs/governance/TREND_X5I_PROTOCOL_ERRATUM_V1.json`
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

## X5I 最新结论

### 数据与身份

Eastmoney primary source 在当前执行链连续被服务端断开，因此按预注册规则没有计算任何 Eastmoney candidate outcome。随后在无 outcome leakage 的前提下冻结 recovery protocol，使用结构独立的 **Tencent native 60m**。

Tencent `ifzq.gtimg.cn` m60 800-depth 稳定返回五指数各 800 根。统计加载后立刻过滤到 **2026-01-05..2026-09-14**，每 carrier 680 bars / 661 slope measurements；2025 public Tencent 行未参与统计，旧 governed 2025 Holdout 未读取。五指数时钟一致：`10:30 / 11:30 / 14:00 / 15:00`。

Primary evaluation：完整的 **2026-06 / 07 / 08**，每 carrier 260 measurements。9 月 1–14 日仅作 forward diagnostic。

### 候选与正式 gate

Prospective 候选只有：

```text
SLOW_COMMON20_CARRIER120
FAST_COMMON5_CARRIER20
ADAPT_DUAL_BLEND_1P5
```

Turnover 在看 Tencent outcome 前就被正式纳入 gate：median 与 q95 `|Δlog(scale)|` 必须都 ≤ slow baseline 的 **2.0×**。

结果：

```text
slow 20/120
  range reduction      84.57%
  temporal improvement 10.85%
  breadth              2/5
  turnover             1.00× / 1.00×
  result               FAIL (temporal/breadth/interaction)

fast 5/20
  range reduction      93.84%
  temporal improvement 23.87%
  breadth              5/5
  interaction improve  37.95%
  turnover median/q95  3.39× / 2.11×
  result               FAIL (both turnover gates)

dual blend
  range reduction      93.75%
  temporal improvement 22.97%
  breadth              5/5
  interaction improve  36.25%
  turnover median/q95  3.21× / 2.21×
  result               FAIL (both turnover gates)
```

因此：

```text
ALL_GATE_QUALIFIED_CANDIDATES = []
SELECTED_CANDIDATE             = NONE
```

9 月 extension 仍显示 short-memory 横截面改善：raw range ≈ 1.5037，fast ≈ 0.3146，dual ≈ 0.4418；但它不参与选择。

## 研究解释

X5I 在独立 provider/clock 上复制了 X5H 的两个事实：

1. **short-memory strength scaling 很强地改善 cross-carrier 与 monthly scale alignment**；
2. **这种改善伴随显著更高的 scale turnover**。

第二点在 X5H 只是 post-hoc concern；到 X5I 已成为预注册 prospective failure。因此现在没有证据支持把 pure-fast 或 dual blend 升级为产品 `normalized_strength`。

这里是结构独立 provider replication，不是新的时间 OOS；所以 `fresh_oos=false` 继续保持。

## 当前结论

```text
SHORT_MEMORY_SCALE_BENEFIT              = REPLICATED
ADAPTIVE_DUAL_SCALE_BENEFIT             = REPLICATED
SCALE_TURNOVER_CONCERN                  = PROSPECTIVELY CONFIRMED
SPECIFIC_REGIME_SHIFT_MECHANISM         = NOT IDENTIFIED
STABLE_TEMPORAL_PRODUCT_STRENGTH        = NOT ESTABLISHED
CURRENT_DECISION                        = INSUFFICIENT_EVIDENCE
V1                                      = NO CHANGE
X6                                      = HOLD / NOT READY
```

下一步若继续，应研究 **响应性与 jitter 的折中**，而不是继续在 fast/dual 二选一：例如 bounded-update、turnover-regularized、state-space / exponentially-smoothed fast scale，并把 turnover 保持为预注册 gate。不得用收益或 DOWN/SIDEWAYS/UP outcome 选择 strength estimator。

## 仍然禁止

- 重跑 M5 primary / T2 sensitivity / STAR50 replication；
- 打开旧 M4/M5 governed 2025 Holdout；
- 修改冻结的 M6/M7/M8/M9 semantics；
- 把 public/native-clock research source 写成 runtime admitted 或 DataHub exact identity；
- 输出 `global_state`、BUY/SELL、position/order、strategy selection/routing；
- 把 `production_authority=false` 或 `fresh_oos=false` 改成 true。

历史 V1 snapshots 永不原地改写。未来任何 T1、lookback、estimator、strength semantics 改动都必须经过新的版本化 representation decision。
