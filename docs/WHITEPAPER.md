# 趋势状态识别组件：当前研究与工程白皮书

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](REPOSITORY_STATE.json) · [最新研究解释](research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

> 本白皮书定义产品定位与当前证据。工程里程碑完成不自动授予 production authority，也不产生 fresh OOS 结论。

## 1. 产品定位

本仓交付的是 **Layer 2 趋势状态识别组件**。它描述指定 `symbol + as_of + bar_interval/profile` 下的趋势方向和连续强度，不承担买卖、仓位、订单、策略路由或多周期总趋势语义。

## 2. M5/M6 证据与表示

M5 在 admitted 1m/5m exact views 上完整收口：CSI1000 primary、T2 sensitivity 与 STAR50 replication 都反驳原 extreme-slope exhaustion H1。M6 因此冻结为：

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

V1 stable semantics 不包含 `STRONG_UP/STRONG_DOWN`、five-bucket state、T2 或 `global_state`。

## 3. M7 Stable Consumer（PASS）

Machine authority：`docs/governance/TREND_M7_CONSUMER_CONTRACT_V1.json`。

`regime_state_consumer_v1` / `trend_regime_snapshot@1.0` 已实现 immutable identity、append-only ingest、publication/receipt causality、as-of visibility、expiry、latest-expired/unavailable no-fallback、provider/source receipt identity 与 M6 representation fields。

当前 runtime admission 仅两指数的 `trend_1m_official_v1` / `trend_5m_offset0_v1`。其余 M3 profiles 当前 `STATE_NOT_ADMITTED`；caller 不得扩张 registry。

## 4. M8 Strategy-Layer Integration Validation（PASS，scope-limited）

Machine authority：`docs/governance/TREND_M8_STRATEGY_INTEGRATION_V1.json`。

M8 没有新建策略，而是验证**分层所有权**：

- CSI1000 私仓已有真实 read-only Layer2 consumer adapter：不做 value transformation、不改 threshold、不改策略；其真实 Layer3 orchestration kernel 负责 state adapter、owner waterfall 与 conflict arbitration。
- M7 trend snapshot 与上述“Layer2 只读输入 → Layer3 组合/仲裁”边界兼容；没有安装新策略 plugin，也没有修改外部仓。
- STAR50 仓已有真实 append-only risk-state consumer，但其示例明确 `actual_external_consumer_connected=False`；所以 M8 只把它认证为**并行 Layer2 risk provider boundary**，不虚构已连接的策略 caller。
- Synthetic integration 验证 1m/5m 状态可以冲突并保持独立；trend/risk 分开上送；expired/unavailable 不回退、不变 SIDEWAYS；未准入 15m 在到达上层前就 fail closed。
- Layer2 stable payload 不产生 T2/strong/five-bucket/global-state，也不产生 BUY/SELL、position/order、strategy selection 或 route。

因此 M8 的 PASS 是**接口与所有权边界验证**，不是 live/production integration certification。

## 5. 当前证据与部署限制

- persistence/strength empirical certification 仍只覆盖 admitted 1m/5m 与 CSI1000/STAR50；
- 15m/60m 和 phase profiles 没有同等级认证；
- STAR50 没有已证明的 external strategy caller connection；
- 2025 Holdout 从未打开，M5 outcome 不重开；
- `production_authority=false`、`fresh_oos=false`。

## 6. 唯一下一步：M9

M9 只处理 release/version/documentation/governance：schema/version matrix、examples、migration/changelog、evidence lineage、known limitations 与 release policy。

M9 不得扩大 source admission、重开 M5、改变 M6/M7、把 M8 说成 production deployment，或授予 production authority。
