# Trend Regime V1 阶段性成果与证据边界

本文件记录 `factorlab.layer2.trend_regime@1.0.0` 在 M0–M9 完成后的**阶段性成果**与**尚未证明的边界**。它不是新的产品语义，也不改变 V1 release pointer、M6 representation、M7 lifecycle 或当前 runtime admission。

## 1. 已经完成并可稳定依赖的成果

V1 已经形成一套明确、可复现、可被上层稳定消费的 Layer 2 趋势状态接口：

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

基础测量候选形式为：

```text
20 completed bars
→ log(close)
→ OLS signed slope t-score
→ T1=2.0 三桶方向状态
→ continuous strength = abs(slope_t)
```

工程上已经建立了多周期 / 多 phase profile registry：

- 1m：official
- 5m：offset0 / 1 / 2 / 3 / 4
- 15m：offset5 / 10
- 60m：offset30 / 45

M7 stable consumer 已冻结 immutable snapshot、append-only ingest、receipt-causal as-of、expiry/no-fallback、provider/source/admission identity 与 fail-closed unavailable semantics。

## 2. 当前真正完成实证验证的范围

截至 V1 release，科学证据只覆盖：

- carriers：`000852.SH`（CSI1000）、`000688.SH`（STAR50）
- profiles：`trend_1m_official_v1`、`trend_5m_offset0_v1`
- M5 finding：预注册的 extreme-slope exhaustion H1 被反驳；在已准入 1m/5m 视图中，更极端的 `|slope_t|` 表现为更高 directional persistence、较低 reversal。

M4/M5 曾研究五桶及 `T2=3/4/5`，但没有发现一个具有充分证据优势的唯一 T2。因此正式 V1 没有采用五桶，而是三桶 + continuous strength。

## 3. 当前不能宣称的事情

V1 **没有证明**以下命题：

1. `20 bars` 在所有 interval 上都是最合适或可比的观察窗；
2. `T1=2.0` 在 1m / 5m / 15m / 60m 上具有相同的统计与状态语义；
3. 同一 interval 的不同 phase/offset 具有相同的 slope-t 分布、状态占比和持续性；
4. 不同 profile 的 `strength=abs(slope_t)` 数值可以直接横向比较；
5. CSI1000 与 STAR50 上成立的现象可以外推为跨指数普适规律；
6. 15m / 60m / 其他 phase 已经拥有与 1m/5m offset0 同等级的 empirical certification。

因此必须区分三种含义：

- **engineering computable**：profile registry 和计算逻辑能够处理该视图；
- **historical research available**：存在可审计的历史 exact-view 数据，可作为新研究的候选材料；
- **runtime admitted**：stable consumer 当前正式允许对外提供该 profile。

三者不能互相替代。

## 4. 关于“统一逻辑”的当前结论

现阶段已经抽象出的，是统一的**测量方法与输出语义**，不是已经证明的统一数值参数。

下一阶段应检验：

```text
统一方法是否成立？
    score = standardized signed trend statistic

哪些参数可统一？
    lookback
    T1
    strength scale

哪些参数可能必须 profile-specific？
    interval-specific threshold
    phase-specific calibration
    normalized strength mapping
```

可能的最终架构不是强制所有 profile 共用相同数字，而是：

```text
统一 measurement family
+ 可治理的 profile calibration
+ 统一 DOWN / SIDEWAYS / UP 语义
+ 可比较或明确不可比较的 strength 定义
```

## 5. V1 仍保持冻结

新的 cross-profile 研究不得自动改变：

- V1 state enum；
- M2 T1；
- estimator / directional_score；
- M7 snapshot lifecycle；
- 当前 runtime admission；
- `production_authority=false`；
- `fresh_oos=false`。

任何最终需要改变 T1、lookback、strength normalization 或 profile semantics 的结论，都必须经过新的版本化 representation decision；不能原地改写 V1 snapshot。

## 6. 下一阶段

用户于 2026-09-14 明确授权启动独立 Post-V1 研究阶段：**Cross-Profile Invariance & Calibration Study**。

研究协议见：

- `TREND_CROSS_PROFILE_INVARIANCE_PROTOCOL_V1.json`
- `TREND_CROSS_PROFILE_SOURCE_INVENTORY_V1.json`

该阶段首先做 source/profile coverage 与证据边界审计，然后再做预注册的 distribution/state-dynamics invariance 研究。研究完成前，不扩 runtime admission，不声称跨周期/跨 phase 普适性。
