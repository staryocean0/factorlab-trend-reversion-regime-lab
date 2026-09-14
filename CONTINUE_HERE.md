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
- X3 state-dynamics invariance — **PROTOCOL FROZEN / NEXT**

接管必读：

- `docs/ROADMAP.md`
- `docs/governance/TREND_V1_STAGE_CLOSEOUT_V1.md`
- `docs/governance/TREND_CROSS_PROFILE_INVARIANCE_PROTOCOL_V1.json`
- `docs/governance/TREND_CROSS_PROFILE_SOURCE_INVENTORY_V1.json`
- `docs/governance/TREND_X2_DISTRIBUTIONAL_INVARIANCE_FREEZE_V1.json`
- `docs/governance/TREND_X2_DISTRIBUTIONAL_INVARIANCE_RESULT_V1.json`
- `docs/governance/TREND_X2_DIAGNOSTIC_SENSITIVITY_RESULT_V1.json`
- `docs/governance/TREND_X3_STATE_DYNAMICS_INVARIANCE_FREEZE_V1.json`
- `docs/governance/TREND_M7_CONSUMER_CONTRACT_V1.json`
- `docs/governance/TREND_M9_RELEASE_GOVERNANCE_V1.json`

## V1 正式产品

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

入口：`query_regime(symbol, as_of, bar_interval, profile_id=None)`。

当前 runtime admission 仍只包括两指数 `trend_1m_official_v1` / `trend_5m_offset0_v1`；其他 M3 profiles fail closed。

## 当前真正证明到哪里

V1 empirical certification 只覆盖 CSI1000 / STAR50 的 1m official 与 5m offset0。它没有证明 `20 bars`、`T1=2` 或 raw strength 在所有 interval / phase / carrier 上普适。

X1 进一步确认：两个现有指数都保存有可审计的多周期、多 phase exact-view 历史资产，但这些 legacy research sources **不等于 runtime admission**。

## X2 已得到的第一轮结果

研究窗口固定为 2020-07-23 至 2020-12-31，只做 Development-only matched exact-view 诊断；未打开旧 2025 Holdout。

固定 `lookback=20 / T1=2` 下：

- 同 interval 不同 phase 的 occupancy / score 差异总体很小；
- 5m offset0–4 在两个指数上的最大 phase occupancy range 均低于约 1%；
- 跨 interval 的差异明显比 phase 差异大，60m 最突出；
- CSI1000 60m SIDEWAYS 约 40%，1m/5m 约 23%–25%；
- STAR50 60m SIDEWAYS 约 30%，5m/15m 约 22%–23%；
- 两指数 60m matched-profile occupancy 差异可到约 10 个百分点；
- 60m 短窗口每 phase 只有 201 个 available measurements，因此只能作为反对“简单普适性”的初步证据，不能直接定 calibration。

预注册 sensitivity `lookback=[10,20,40] × T1=[1.5,2.0,2.5]` 后：

- phase dispersion 仍较小；
- 5m 的 cross-carrier occupancy 差异最稳定、最小；
- 60m 的 cross-carrier occupancy 差异最大，网格中最大约 15.8 个百分点；
- lookback 会显著改变 slope-t 数值尺度，特别是 1m/5m/15m 的 `abs(slope_t)` q90 随 lookback 增长明显上升；
- 没有选择新的 T1/lookback，V1 仍是 20 / 2.0。

当前最合理的研究优先级因此是：**interval-level calibration / normalization 是否必要**，而不是先给每个 phase 单独调阈值。

## 下一步：X3 state-dynamics invariance

协议已经冻结：`docs/governance/TREND_X3_STATE_DYNAMICS_INVARIANCE_FREEZE_V1.json`。

继续固定 V1 `20 bars / T1=2`，比较：

- state episode duration；
- one-step transition matrix；
- directional survival at 1/3/5/10/20 profile bars；
- opposite-direction entry probability。

X3 不计算交易收益，不调产品参数。跨 interval 的 bar horizon 不等同真实时间，所以按 interval 分开报告。

## 仍然禁止

- 重跑 M5 primary / T2 sensitivity / STAR50 replication；
- 打开旧 M4/M5 2025 Holdout；
- 在 X2/X3 结果未形成版本化 decision 前修改 M6 representation、M7 lifecycle 或 runtime admission；
- 把 legacy research source 写成 runtime admitted；
- 输出 `global_state`、BUY/SELL、position/order、strategy selection/routing；
- 把 `production_authority` 或 `fresh_oos` 改成 true；
- 用两个指数外推普适市场规律。

V1 release pointer 不随 Post-V1 研究提交移动。任何未来 calibration/normalization 若改变 T1、lookback 或 strength semantics，必须通过新的版本化 representation decision，历史 V1 snapshots 不得原地改写。
