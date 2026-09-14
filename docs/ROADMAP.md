# 趋势状态识别组件路线图

> 本仓的 trend-regime 是 Layer 2 市场状态基础设施，不是交易策略。
>
> 原 M0–M9 已完成并冻结；2026-09-14 用户显式授权独立的 Post-V1 Cross-Profile Invariance & Calibration Study。后续研究不得静默改写 V1。

## 当前进度

- **M0–M9 — COMPLETE / PASS**：`factorlab.layer2.trend_regime@1.0.0` 稳定组件合同已冻结。
- **X1 — COMPLETE**：source/profile inventory。
- **X2 fixed baseline — COMPLETE**：两指数 × 10 exact views，固定 `20-bar slope_t / T1=2` 分布不变性。
- **X2 diagnostic sensitivity — COMPLETE**：`lookback=[10,20,40] × T1=[1.5,2.0,2.5]`，无产品参数选择。
- **X3 — COMPLETE**：state-dynamics invariance；同 interval phase 稳定，60m carrier heterogeneity 明显且部分方向 underpowered。
- **X4 — DECISION = `INSUFFICIENT_EVIDENCE`**：不修改 V1。
- **X5 — COMPLETE（scope-limited）**：五指数 5m clock-aligned independent-source replication。
- **X5B — COMPLETE**：Sina ↔ Eastmoney 5m source robustness；两指数三桶状态 100% 一致。
- **X6 — HOLD / NOT READY**：跨 interval 尤其 60m 的更广 carrier 证据不足，不做 semantic-version 变更。

V1 release pointer `release/trend-regime-v1.0.0` 必须继续指向原 M9 gated commit；Post-V1 研究提交不得移动它。

## V1 冻结表示

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

稳定入口：`query_regime(symbol, as_of, bar_interval, profile_id=None)`。

当前 runtime admission 仍只有：

- symbols：`000852.SH`、`000688.SH`
- profiles：`trend_1m_official_v1`、`trend_5m_offset0_v1`

其他 M3 engineering profiles 继续 fail closed。Post-V1 research source 不产生 runtime admission。

## V1 阶段性证据边界

阶段总结：`docs/governance/TREND_V1_STAGE_CLOSEOUT_V1.md`。

V1 empirical certification 原本只覆盖 CSI1000 / STAR50 的 1m official 与 5m offset0；因此不能把 `20 bars`、`T1=2` 或 raw `abs(slope_t)` 解释为已经跨所有 interval / phase / carrier 证明普适。

## Post-V1 总协议

Machine protocol：`docs/governance/TREND_CROSS_PROFILE_INVARIANCE_PROTOCOL_V1.json`。

核心问题不是“找一个表现最好的阈值”，而是：

> 哪些 measurement semantics 可以跨 carrier / interval / phase 保持不变，哪些部分必须 calibration / normalization？

研究决策不得使用未来交易收益最大化作为阈值选择标准。

## X1 — Source/Profile Inventory — COMPLETE

Authority：`docs/governance/TREND_CROSS_PROFILE_SOURCE_INVENTORY_V1.json`。

已确认 M3 registry 有 10 个 engineering profiles：1m official、5m offset0–4、15m offset5/10、60m offset30/45。

- STAR50 legacy development 保存这些 exact views，覆盖 2020-07-23 至 2026-08-21；
- CSI1000 two-wave legacy 有匹配 exact views，但只到 2020-12-31；
- 两指数形成 2020-07-23 至 2020-12-31 matched Development-only exact-view 窗口；
- legacy research source 不等于 runtime admission。

## X2 — Distributional Invariance — COMPLETE

Freeze：`docs/governance/TREND_X2_DISTRIBUTIONAL_INVARIANCE_FREEZE_V1.json`  
Result：`docs/governance/TREND_X2_DISTRIBUTIONAL_INVARIANCE_RESULT_V1.json`

固定 `lookback=20 / slope_t / T1=2` 后：

- 5m offset0–4 同 carrier 的 phase occupancy range 低于约 1%；
- 15m phase 差异也小；
- 跨 interval 差异明显大于 phase 差异；
- CSI1000 60m SIDEWAYS 约 40%，而 1m/5m 约 23%–25%；
- STAR50 60m SIDEWAYS 约 30%，5m/15m 多在约 22%–23%；
- 两指数 60m matched-profile occupancy 差异可到约 10 个百分点；
- 60m 每 phase 在该窗口只有 201 measurements，不能据此直接定 calibration。

### X2 diagnostic sensitivity

Authority：`docs/governance/TREND_X2_DIAGNOSTIC_SENSITIVITY_RESULT_V1.json`。

预注册网格：

```text
lookback = [10, 20, 40]
T1       = [1.5, 2.0, 2.5]
```

结论：phase dispersion 仍小；5m cross-carrier 最稳；60m cross-carrier 差异最大；lookback 会明显改变 slope_t 数值尺度。没有从网格挑选新参数，V1 保持 20 / 2.0。

## X3 — State-Dynamics Invariance — COMPLETE

Freeze：`docs/governance/TREND_X3_STATE_DYNAMICS_INVARIANCE_FREEZE_V1.json`  
Result：`docs/governance/TREND_X3_STATE_DYNAMICS_INVARIANCE_RESULT_V1.json`

固定 V1 `20 bars / T1=2`，比较 episode duration、one-step transition、directional survival、opposite-direction entry。

结果继续支持：

- 同 interval 不同 phase 的 dynamics 接近；
- 1m/5m/15m 两指数之间差异总体有限；
- 60m carrier 差异明显放大；
- 60m UP 方向仅约 40–47 horizon origins，按冻结规则标记 `UNDERPOWERED_DESCRIPTIVE_ONLY`。

X3 没有计算交易收益，也没有调产品参数。

## X4 — Calibration Family Decision

原 decision：`docs/governance/TREND_X4_CALIBRATION_FAMILY_DECISION_V1.json`。  
Post-X5 additive update：`docs/governance/TREND_X4_POST_X5_UPDATE_V1.json`。

当前总体决策仍是：

```text
INSUFFICIENT_EVIDENCE
```

这意味着：

- `UNIVERSAL_FIXED_T1` 尚未建立；
- `INTERVAL_SPECIFIC_T1` 是合理候选，但尚未建立；
- `PROFILE_SPECIFIC_T1` 没有被 phase evidence 支持为默认方案；
- `NORMALIZED_SCORE_PLUS_UNIVERSAL_SEMANTIC_THRESHOLD` 仍是合理候选；
- V1 不变。

## X5 — Five-Carrier 5m Expansion — COMPLETE（scope-limited）

Primary freeze：`docs/governance/TREND_X5_CROSS_CARRIER_REPLICATION_FREEZE_V1.json`  
Source fallback freeze：`docs/governance/TREND_X5_SOURCE_FALLBACK_V1.json`  
Sina source receipt：`docs/governance/TREND_X5_SINA_SOURCE_RECEIPT_V1.json`  
Result：`docs/governance/TREND_X5_FIVE_CARRIER_5M_RESULT_V1.json`

研究 carrier：

- CSI1000 `000852.SH`
- STAR50 `000688.SH`
- CSI300 `000300.SH`
- CSI500 `000905.SH`
- SSE50 `000016.SH`

统一窗口：2026-08-17 至 2026-09-14，21 个完整交易日；每 carrier 1008 根 5m bars、989 个 slope_t measurements。Sina 5m close clock 逐日通过 M3 `5m_offset0` clock gate，但 source identity **不是 DataHub exact identity**。

核心结果：

- SIDEWAYS occupancy 五指数 range ≈ **3.13pp**；
- one-step self-transition range：DOWN ≈ **1.87pp**、SIDEWAYS ≈ **1.61pp**、UP ≈ **1.23pp**；
- 5-bar directional survival range：DOWN ≈ **6.54pp**、UP ≈ **2.81pp**；
- 10-bar opposite-direction entry range：DOWN ≈ **5.53pp**、UP ≈ **6.33pp**；
- 所有预注册 directional horizon origins 均 >=50。

解释：5m state semantics 在五个结构差异明显的指数族上表现出较强 carrier robustness；目前没有证据要求 carrier-specific 5m T1。但 21 个交易日的近期窗口不能证明全市场、全周期普适性。

## X5 source identity / equivalence boundary

Authority：`docs/governance/TREND_X5_EASTMONEY_EQUIVALENCE_RESULT_V1.json`。

Eastmoney 5m 与 DataHub retained STAR50 views 的 close timestamps 完全覆盖，但 point values 并非逐点完全相同。因此：

- public source 可以是 clock-aligned independent-source evidence；
- 不能称为 DataHub exact-view identity；
- 不能据此扩 runtime admission；
- public native 15m/60m 不能冒充 M3 exact profiles。

## X5B — 5m Source Robustness — COMPLETE

Freeze：`docs/governance/TREND_X5B_SOURCE_ROBUSTNESS_FREEZE_V1.json`  
Result：`docs/governance/TREND_X5B_SOURCE_ROBUSTNESS_RESULT_V1.json`

在 2026-08-17 至 2026-09-14、CSI1000 / STAR50、相同 5m clock、固定 `20/2.0` 下比较 Sina 与 Eastmoney：

- 每 carrier 1008 个共同 close timestamps；
- slope_t Pearson ≈ **0.9999994**；
- slope_t abs-diff q95 < **0.004**；
- 每 carrier 989 个三桶状态，**exact agreement = 100%**；
- DOWN ↔ UP opposite-direction disagreement = **0**。

所以 observed vendor differences 不要求 provider-specific 5m calibration；但 source identities 仍然必须分开治理。

## X6 — Representation / Version Decision — HOLD

当前不具备改变 representation / SemVer 的证据。

X6 只有在补齐以下证据后才重新评估：

1. 更广 carrier 的 15m / 60m evidence，且 source/clock semantics 明确；
2. 60m 样本充分到不再出现关键方向 underpower；
3. 直接比较 interval-specific threshold 与 score normalization 的 state-semantic comparability，而不是比较交易收益。

目前 action：**NO V1 CHANGE / NO ADMISSION EXPANSION / NO X6 VERSION BUMP**。

## 全程冻结边界

- 不重跑 M5 primary / T2 sensitivity / STAR50 replication；
- 不打开旧 M4/M5 2025 Holdout；
- 不把 research-only public/legacy source 写成 runtime admitted source；
- 不因为 clock alignment 宣称 exact source identity；
- 不产生 `global_state`、BUY/SELL、position/order、strategy selection/routing；
- `production_authority=false`、`fresh_oos=false`；
- 任何未来改变 T1、lookback、estimator、strength semantics 或 snapshot lifecycle 的决定必须版本化；
- 历史 V1 snapshots 不得原地改写。
