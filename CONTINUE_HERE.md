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

2026-09-14 用户明确授权了一个新的独立 Post-V1 研究计划：**Cross-Profile Invariance & Calibration Study**。它不是自动 M10，也不会静默修改 V1。

接管必读：

- `docs/ROADMAP.md`
- `docs/governance/TREND_V1_STAGE_CLOSEOUT_V1.md`
- `docs/governance/TREND_CROSS_PROFILE_INVARIANCE_PROTOCOL_V1.json`
- `docs/governance/TREND_CROSS_PROFILE_SOURCE_INVENTORY_V1.json`
- `docs/API_CONTRACT.md`
- `docs/governance/TREND_V1_RELEASE.md`
- `docs/governance/TREND_M7_CONSUMER_CONTRACT_V1.json`
- `docs/governance/TREND_M8_STRATEGY_INTEGRATION_V1.json`
- `docs/governance/TREND_M9_RELEASE_GOVERNANCE_V1.json`

## V1 正式产品与 consumer

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

入口：`query_regime(symbol, as_of, bar_interval, profile_id=None)`。

M7 lifecycle 已冻结：immutable/append-only、receipt-causal as-of、expiry、latest-expired/unavailable no-fallback、stable source/provider identities。当前 runtime admission 仍只包括两指数 `trend_1m_official_v1` / `trend_5m_offset0_v1`；其他 M3 profiles fail closed。

## V1 当前真正证明了什么

科学证据只覆盖：

- `000852.SH`（CSI1000）；
- `000688.SH`（STAR50）；
- 1m official；
- 5m offset0。

M5 证明：在这些已准入视图上，极端 `|slope_t|` 比 moderate trend 更持续、反转更少；原 exhaustion H1 被反驳。

V1 **没有证明** `20 bars`、`T1=2`、strength scale 在所有 interval / phase / carrier 上具有相同含义。

## Post-V1 Cross-Profile 研究

Protocol：`docs/governance/TREND_CROSS_PROFILE_INVARIANCE_PROTOCOL_V1.json`。

研究目标不是强迫所有 profile 共用同一数字，而是判断：

- 哪些部分可以统一；
- 哪些必须 interval-specific；
- 哪些必须 phase/profile-specific；
- 是否需要 normalized strength 才能跨 profile 比较。

### X1 — COMPLETE

`docs/governance/TREND_CROSS_PROFILE_SOURCE_INVENTORY_V1.json` 已完成 source metadata 审计，未读取 market rows、未算 outcome、未调参。

结果：

- engineering registry：10 个 profile；
- runtime admitted：仍仅 1m official / 5m offset0；
- STAR50 legacy development 保存完整 1m、5m offset0–4、15m offset5/10、60m offset30/45 exact views，覆盖 2020-07-23 至 2026-08-21；
- CSI1000 two-wave legacy 保存匹配 exact views，覆盖 2015-01-05 至 2020-12-31；
- 两指数第一轮 matched Development-only 研究窗口可取 2020-07-23 至 2020-12-31；
- 当前 GitHub 可访问仓库中尚未定位 `000300.SH`、`000905.SH`、`000016.SH` exact-view source。

Legacy exact view 可以成为新研究候选材料，但不会因此获得 runtime admission。

### 当前下一步 — X2 Distributional Invariance

先保持：

```text
lookback = 20
score = slope_t
T1 = 2.0
```

逐 carrier / interval / phase 比较 slope-t 分布、`abs(slope_t)` 分布、三桶 occupancy、phase dispersion 与 carrier dispersion。固定基线结果出来以前禁止调 T1/lookback。

之后才允许执行协议中预声明的 diagnostic sensitivity：

```text
lookback = [10, 20, 40]
T1       = [1.5, 2.0, 2.5]
```

这些只是 invariance diagnostic，不是按结果优化产品参数。

## M8 边界保持不变

- CSI1000 私仓存在真实 read-only Layer2 adapter 与 Layer3 orchestration kernel；
- STAR50 有真实 parallel risk-state provider，但没有被证明存在 connected external strategy caller；
- 多周期组合、trend/risk 融合、冲突仲裁、策略选择和最终动作全部在 Layer2 之外。

## 仍然禁止

- 重跑 M5 primary / T2 sensitivity / STAR50 replication；
- 读取旧 M4/M5 2025 Holdout；
- 研究结果未完成就修改 M6 representation、M7 lifecycle 或 runtime admission；
- 把 legacy development source 写成 runtime admitted；
- 在 Layer2 输出 `global_state`、BUY/SELL、position/order、strategy selection/routing；
- 把 `production_authority` 或 `fresh_oos` 改成 true；
- 把两个指数的结果外推成普适市场规律。

如果 X2–X5 最终否定统一 T1/lookback，必须通过新的 versioned representation/calibration decision 处理，历史 V1 snapshots 不得原地改写。
