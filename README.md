# FactorLab 趋势状态识别组件

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 当前产品状态

**M0–M8 已完成。** 本仓是 Layer 2 趋势状态识别组件，不是交易策略。

正式表示：

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

Stable consumer：`regime_state_consumer_v1`；snapshot：`trend_regime_snapshot@1.0`；正式入口：`query_regime(symbol, as_of, bar_interval, profile_id=None)`。

M7 已实现 immutable/append-only snapshot lifecycle、causal receipt visibility、expiry/no-fallback、stable identity 和 fail-closed provider admission。当前 V1 runtime 只接纳两指数的 `trend_1m_official_v1` 与 `trend_5m_offset0_v1`；其他 M3 profiles 当前仍 `STATE_NOT_ADMITTED`。

M8 已完成**上层集成边界验证**：CSI1000 私仓的真实 read-only Layer2 adapter / Layer3 orchestration 与 M7 所有权边界兼容；STAR50 的真实 risk-state consumer 作为并行 Layer2 risk provider 验证，但其仓内示例明确尚无 external consumer connected，所以不声称已经部署 STAR50 策略接线。Trend/risk、多周期组合、冲突仲裁和任何动作映射都留在 Layer3 或更高层。

M8 没有修改外部仓、没有读取市场 outcome、没有重开 M5/Holdout，也没有赋予 production authority。

`production_authority=false`、`fresh_oos=false` 保持不变。

**唯一下一步：M9 — release / version / documentation / governance。**

入口：[接管](CONTINUE_HERE.md) · [路线图](docs/ROADMAP.md) · [API 合同](docs/API_CONTRACT.md) · [M7 合同](docs/governance/TREND_M7_CONSUMER_CONTRACT_V1.md) · [M8 记录](docs/governance/TREND_M8_STRATEGY_INTEGRATION_V1.md)
