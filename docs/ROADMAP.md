# 趋势状态识别组件路线图

> 本路线图定义执行顺序。组件是 Layer 2 市场状态基础设施，不是交易策略。
>
> 原 M0–M9 已完成；后续研究必须由新的显式授权与独立治理启动，不能静默改写 V1。

## 当前进度

- **M0–M9 — COMPLETE / PASS**：`factorlab.layer2.trend_regime@1.0.0` 已发布为稳定组件合同。
- **Post-V1 X1 — COMPLETE**：cross-profile source/profile inventory。
- **Post-V1 X2 fixed baseline — COMPLETE**：两指数 × 10 exact views 的固定 `20-bar slope_t / T1=2` 分布不变性诊断。
- **Post-V1 X2 sensitivity — COMPLETE**：预注册 `lookback=[10,20,40] × T1=[1.5,2.0,2.5]` diagnostic grid；没有产品参数选择。
- **Post-V1 X3 — PROTOCOL FROZEN / NEXT**：state-dynamics invariance。

V1 release pointer `release/trend-regime-v1.0.0` 保持指向已通过 M9 Gate 的 V1 commit；Post-V1 研究提交不得移动它。

## V1 阶段性成果与证据边界

阶段总结：`docs/governance/TREND_V1_STAGE_CLOSEOUT_V1.md`。

正式 V1 表示：

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

V1 已经完成统一 measurement family、stable API、snapshot lifecycle 与三桶 + continuous strength 表示，但 empirical certification 实际只覆盖：

- `000852.SH` / `000688.SH`；
- `trend_1m_official_v1`；
- `trend_5m_offset0_v1`。

因此 V1 不能被解释为已经证明 `20 bars`、`T1=2` 或 raw `abs(slope_t)` scale 跨所有 interval / phase / carrier 普适。

## Post-V1：Cross-Profile Invariance & Calibration Study

用户于 2026-09-14 明确授权启动。Machine protocol：`docs/governance/TREND_CROSS_PROFILE_INVARIANCE_PROTOCOL_V1.json`。

目标：判断统一趋势测量方法中，哪些部分可以跨 carrier / interval / phase 保持不变，哪些部分必须 profile-specific calibration。

### X1 — Source/Profile Inventory — COMPLETE

输出：`docs/governance/TREND_CROSS_PROFILE_SOURCE_INVENTORY_V1.json`。

已确认：

- M3 engineering registry 有 10 个 profile；
- runtime admission 仍只有两指数的 1m official / 5m offset0；
- STAR50 legacy development 保存完整 1m、5m offset0–4、15m offset5/10、60m offset30/45 exact views，覆盖 2020-07-23 至 2026-08-21；
- CSI1000 two-wave legacy 保存匹配 exact views，但只到 2020-12-31；
- 两指数可形成 2020-07-23 至 2020-12-31 的 matched Development-only 初始窗口；
- 当前可访问 GitHub 仓库中尚未定位 `000300.SH`、`000905.SH`、`000016.SH` exact-view source。

X1 只读取 source metadata，没有读取 market rows、没有计算 outcome、没有调参、没有改变 runtime admission。

### X2 — Distributional Invariance — FIXED BASELINE COMPLETE

Freeze：`docs/governance/TREND_X2_DISTRIBUTIONAL_INVARIANCE_FREEZE_V1.json`。

Result：`docs/governance/TREND_X2_DISTRIBUTIONAL_INVARIANCE_RESULT_V1.json`。

固定：

```text
window   = 2020-07-23 .. 2020-12-31
lookback = 20
score    = slope_t
T1       = 2.0
```

没有 resample、没有交易收益、没有调参数、没有打开旧 2025 Holdout。

初步结果：

1. **同一 interval 内 phase 差异较小。** 5m 五个 phase 的最大 occupancy range 在两个指数上都低于约 1%；15m/60m phase 差异也总体较小。
2. **跨 interval 差异明显大于 phase 差异。** 60m 最突出。
3. CSI1000 固定 T1=2 时，60m `SIDEWAYS` 约 40%，而 1m/5m 大约 23%–25%；60m `abs(slope_t)` q90 约 7.8–7.9，而 1m/5m/15m 多在约 10.9–11.5。
4. STAR50 60m `SIDEWAYS` 约 30%，5m/15m 多在约 22%–23%。
5. 两指数的 matched-profile occupancy 差异在 5m 较小，在 15m 增大，在 60m 可达到约 10 个百分点。
6. 60m 每个 phase 在该短窗口只有 201 个 available measurements，因此这些结果是**反对简单普适性假设的证据**，还不是 calibration final decision。

### X2 Diagnostic Sensitivity — COMPLETE

Result：`docs/governance/TREND_X2_DIAGNOSTIC_SENSITIVITY_RESULT_V1.json`。

预注册网格：

```text
lookback = [10, 20, 40]
T1       = [1.5, 2.0, 2.5]
```

主要结论：

- phase dispersion 在整个网格中仍然相对小；
- 5m 的 cross-carrier occupancy 差异持续最小；
- 60m 的 cross-carrier occupancy 差异最大，网格中最大约 15.8 个百分点；
- lookback 会显著改变 slope-t scale：1m/5m/15m 的 `abs(slope_t)` q90 随 10→20→40 明显上升；
- 因此不同 lookback 定义下的 raw strength 不能直接数值互换；
- 没有从 sensitivity 中选择新的 T1/lookback，V1 仍保持 20 / 2.0。

当前证据把研究重点从“每个 phase 单独调参”转向：**先检验 interval-level calibration / normalization 是否必要。**

### X3 — State-Dynamics Invariance — NEXT

Freeze：`docs/governance/TREND_X3_STATE_DYNAMICS_INVARIANCE_FREEZE_V1.json`。

仍先只用 V1 固定基线 `20 bars / T1=2`，比较：

- exact-state episode duration；
- one-step transition matrix；
- directional survival at `[1,3,5,10,20]` profile bars；
- opposite-direction entry probability。

X3 不计算交易收益；SIDEWAYS 可以打断 directional survival，但不等同于 opposite-direction reversal。跨 interval 的 bar horizon 不等同真实时间，因此必须分别报告，不能把 1m 的 5 bars 与 60m 的 5 bars 当成相同时长。

### X4 — Calibration Decision

只允许从以下结论选择：

- `UNIVERSAL_FIXED_T1`
- `INTERVAL_SPECIFIC_T1`
- `PROFILE_SPECIFIC_T1`
- `NORMALIZED_SCORE_PLUS_UNIVERSAL_SEMANTIC_THRESHOLD`
- `INSUFFICIENT_EVIDENCE`

选择标准是状态语义的可比性，而不是未来交易收益最大化。

### X5 — Cross-Carrier Expansion

在声称“普适规律”之前，目标至少覆盖 5 个结构上有差异的指数族。当前额外候选 `000300.SH`、`000905.SH`、`000016.SH` 仅是 source search targets，不视为已具备数据或已准入。

### X6 — Representation Version Decision

根据 X2–X5 结果决定 V1 保持不变、minor extension，或需要新的 major representation。历史 V1 snapshots 永不原地改写。

## 冻结边界

- M6 representation、M7 lifecycle、M8 integration boundary、M9 release governance 继续冻结；
- runtime source admission 仍只有两指数 1m official / 5m offset0；
- 不重跑 M5 primary / T2 sensitivity / STAR50 replication；
- 不打开旧 M4/M5 2025 Holdout；
- Legacy exact view 的 research use 不会自动带来 runtime admission；
- 不产生 `global_state`、BUY/SELL、position/order、strategy selection/routing；
- `production_authority=false`、`fresh_oos=false`。
