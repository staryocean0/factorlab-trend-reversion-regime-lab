# 从这里接管

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 当前状态

本仓是 Layer 2 趋势状态识别组件，不是交易策略。**M0–M8 PASS**；M8 是 scope-limited integration-boundary PASS。当前唯一下一步：**M9 — release / version / documentation / governance**。

接管必读：`docs/ROADMAP.md`、`docs/API_CONTRACT.md`、`docs/governance/TREND_M7_CONSUMER_CONTRACT_V1.json`、`docs/governance/TREND_M8_STRATEGY_INTEGRATION_V1.json`。

## 正式产品与 consumer

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

入口：`query_regime(symbol, as_of, bar_interval, profile_id=None)`。

M7 lifecycle 已冻结：immutable/append-only、receipt-causal as-of、expiry、latest-expired/unavailable no-fallback、stable source/provider identities。当前 runtime admission 仍只包括两指数 `trend_1m_official_v1` / `trend_5m_offset0_v1`；其他 M3 profiles fail closed。

## M8 已完成

Machine authority：`docs/governance/TREND_M8_STRATEGY_INTEGRATION_V1.json`。

- CSI1000 私仓存在真实 read-only Layer2 adapter 与 Layer3 orchestration kernel；M8 验证 M7 trend snapshot 与这个 ownership boundary 兼容。
- STAR50 存在真实 `state_degree_consumer_d5` risk-state provider，但其示例明确 `actual_external_consumer_connected=False`；因此只能作为并行 Layer2 risk boundary，不得声称已有真实策略 caller 接线。
- Synthetic tests 验证多周期状态分离、trend/risk namespace 分离、expired/unavailable 不补成 SIDEWAYS、15m 未准入在上层之前 fail closed、Layer2 不产生任何 strategy/action 字段。
- 外部仓库没有被修改，没有 market outcome、M5 reopen 或 Holdout read。

M8 的 PASS 是 interface/ownership compatibility，不是 live/production integration certification，也没有安装新策略 plugin。

## 仍然禁止

- 重跑 M5 或读取 2025 Holdout；
- 修改 M6 representation 或 M7 lifecycle/admission；
- 扩张 15m/60m/phase provider admission；
- 在 Layer2 输出 `global_state`、BUY/SELL、position/order、strategy selection/routing；
- 把 STAR50 说成已经连接外部策略 caller；
- 把工程完成解释成 `production_authority=true` 或 `fresh_oos=true`。

## M9 唯一任务

只做 release/version/governance 收口：schema/version compatibility matrix、API examples、changelog/migration、evidence lineage、known limitations、release policy 与 CI/release governance。

M9 不得通过“发布”动作改变已经冻结的研究结论、representation、consumer runtime admission 或 authority。
