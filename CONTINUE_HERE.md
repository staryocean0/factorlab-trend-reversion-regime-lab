# 从这里接管

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 当前状态

本仓是 Layer 2 趋势状态识别组件，不是交易策略。**M0–M9 PASS**；V1 release 已冻结。

Component release identity：`factorlab.layer2.trend_regime@1.0.0`。

2026-09-14 用户明确授权新的独立 Post-V1 研究计划：**Cross-Profile Invariance & Calibration Study**。它不是自动 M10，也不会静默修改 V1。

当前研究进度：

- X1 source/profile inventory — **COMPLETE**
- X2 fixed-baseline distributional invariance — **COMPLETE**
- X2 preregistered lookback/T1 diagnostic sensitivity — **COMPLETE**
- X3 state-dynamics invariance — **COMPLETE**
- X4 provisional calibration-family decision — **COMPLETE / `INSUFFICIENT_EVIDENCE` / NO V1 CHANGE**
- X5 five-carrier 5m external replication — **COMPLETE**
- X5B 5m source robustness — **COMPLETE**
- X6 representation version decision — **HOLD / NOT READY**

V1 release pointer `release/trend-regime-v1.0.0` 继续固定在 M9 通过提交 `5a563d87d1628379e0d9a04aa7c5500bc30c4bc2`；Post-V1 研究提交不得移动它。

## 接管必读

- `docs/ROADMAP.md`
- `docs/governance/TREND_V1_STAGE_CLOSEOUT_V1.md`
- `docs/governance/TREND_CROSS_PROFILE_INVARIANCE_PROTOCOL_V1.json`
- `docs/governance/TREND_CROSS_PROFILE_SOURCE_INVENTORY_V1.json`
- `docs/governance/TREND_X2_DISTRIBUTIONAL_INVARIANCE_RESULT_V1.json`
- `docs/governance/TREND_X2_DIAGNOSTIC_SENSITIVITY_RESULT_V1.json`
- `docs/governance/TREND_X3_STATE_DYNAMICS_INVARIANCE_RESULT_V1.json`
- `docs/governance/TREND_X4_CALIBRATION_FAMILY_DECISION_V1.json`
- `docs/governance/TREND_X5_SINA_SOURCE_RECEIPT_V1.json`
- `docs/governance/TREND_X5_FIVE_CARRIER_5M_RESULT_V1.json`
- `docs/governance/TREND_X5B_SOURCE_ROBUSTNESS_RESULT_V1.json`
- `docs/governance/TREND_X4_POST_X5_UPDATE_V1.json`
- `docs/governance/TREND_M7_CONSUMER_CONTRACT_V1.json`
- `docs/governance/TREND_M9_RELEASE_GOVERNANCE_V1.json`

## V1 正式产品

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

入口：`query_regime(symbol, as_of, bar_interval, profile_id=None)`。

当前 runtime admission 仍只包括两指数 `trend_1m_official_v1` / `trend_5m_offset0_v1`；其他 M3 profiles fail closed。Post-V1 的 Sina/Eastmoney 研究数据不获得 runtime admission。

## Post-V1 目前真正证明到哪里

V1 原 empirical certification 只覆盖 CSI1000 / STAR50 的 1m official 与 5m offset0。Post-V1 研究把证据进一步扩展，但**没有**证明 `20 bars`、`T1=2` 或 raw `abs(slope_t)` scale 跨所有 interval / phase / carrier 普适。

### X2/X3：两指数 × 多周期/多 phase

2020-07-23 至 2020-12-31 Development-only exact-view 结果显示：

- 同一 interval 内 phase 差异总体较小；5m offset0–4 phase dispersion 尤其小；
- 跨 interval 差异明显大于 phase 差异；
- 60m 的 score scale、SIDEWAYS occupancy、carrier dispersion 与短周期差异最明显；
- lookback 10→20→40 会明显改变 slope-t 数值尺度，因此 raw strength 不应跨不同 lookback 直接比较；
- 60m 部分 UP horizon origins 低于预注册最小样本要求，只能 `UNDERPOWERED_DESCRIPTIVE_ONLY`。

X4 因此选择 `INSUFFICIENT_EVIDENCE`，没有修改 V1。

### X5：五指数 5m external replication

五指数：`000852.SH`、`000688.SH`、`000300.SH`、`000905.SH`、`000016.SH`。

统一窗口：2026-08-17 至 2026-09-14，共 21 个完整交易日；每个指数 1008 根 5m bar、989 个有效 measurement。Sina 5m close clock 与 M3 `5m_offset0` 时钟完全对齐，但 source identity 不是 DataHub exact identity。

固定 `lookback=20 / slope_t / T1=2`：

- SIDEWAYS occupancy 跨五指数 range ≈ **3.13 个百分点**；
- one-step self-transition 跨指数 range ≈ **1.23–1.87 个百分点**；
- 5-bar directional survival range：DOWN ≈ **6.54 个百分点**，UP ≈ **2.81 个百分点**；
- 10-bar opposite-direction entry range：DOWN ≈ **5.53 个百分点**，UP ≈ **6.33 个百分点**；
- 所有预注册 directional metrics 的 origin count 均 ≥ 50。

这强化了“5m 三桶语义具有较强 cross-carrier robustness”的证据，但不等于证明 T1=2 跨 interval 普适。

### X5B：5m source robustness

CSI1000 / STAR50，Sina vs Eastmoney，同一 2026-08-17 至 2026-09-14 5m clock：

- 每个指数 1008 个共同 close timestamps；
- source point values 存在微小差异，所以 source identity 不能合并；
- slope_t Pearson correlation ≈ **0.9999994**；
- slope_t absolute-difference q95 < **0.004**；
- 每个指数 989 个三桶状态，**state agreement = 100%**；
- DOWN↔UP opposite-direction disagreements = **0**。

因此当前没有证据支持 provider-specific 5m T1；但 public source 仍不能冒充 DataHub exact source，也不会扩大 runtime admission。

## 当前 calibration 判断

Post-X5 update 仍然保持：

```text
UNIVERSAL_FIXED_T1                              = NOT_ESTABLISHED
INTERVAL_SPECIFIC_T1                            = PLAUSIBLE_LEADING_CANDIDATE_NOT_YET_ESTABLISHED
PROFILE_SPECIFIC_T1                             = NOT_SUPPORTED_AS_DEFAULT_BY_PHASE_EVIDENCE
NORMALIZED_SCORE_PLUS_UNIVERSAL_SEMANTIC_THRESHOLD = PLAUSIBLE_CANDIDATE_NOT_YET_ESTABLISHED
CURRENT_DECISION                                = INSUFFICIENT_EVIDENCE
```

研究不确定性已经明显从“每个 carrier / phase / provider 是否各自调参”收缩到：**跨 interval 的尺度和状态语义，尤其 60m。**

## X6 为什么 HOLD

在以下证据补齐之前，不做 representation version change：

1. 15m/60m 更广的 cross-carrier 证据，且 clock/source semantics 必须显式治理；
2. 更长窗口的 60m 样本，消除之前 UP-direction underpower；
3. 直接比较 `INTERVAL_SPECIFIC_T1` 与 `NORMALIZED_SCORE`，评价标准是状态语义可比性，不是交易收益。

所以当前动作是 **保持 V1 不变，继续收集跨 interval 证据**，而不是为了结束研究强行选参数或发布 V2。

## 仍然禁止

- 重跑 M5 primary / T2 sensitivity / STAR50 replication；
- 打开旧 M4/M5 2025 Holdout；
- 修改冻结的 M6 representation、M7 lifecycle、M8 integration boundary 或 M9 release governance；
- 把 legacy/public research source 写成 runtime admitted；
- 把 source clock alignment 写成 DataHub exact-source identity；
- 输出 `global_state`、BUY/SELL、position/order、strategy selection/routing；
- 把 `production_authority` 或 `fresh_oos` 改成 true；
- 从 21 个交易日的 X5 窗口外推市场普适定律。

历史 V1 snapshots 永不原地改写。未来 calibration/normalization 若改变 T1、lookback 或 strength semantics，必须先形成新的版本化 representation decision。