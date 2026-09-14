# FactorLab 趋势状态识别组件

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 当前产品状态

**M0–M7 已完成。** 本仓是 Layer 2 趋势状态识别组件，不是交易策略。

正式表示：

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

Stable consumer：`regime_state_consumer_v1`；snapshot：`trend_regime_snapshot@1.0`。

正式入口：

```text
query_regime(symbol, as_of, bar_interval, profile_id=None)
```

M7 已实现 immutable/append-only snapshot lifecycle、causal receipt visibility、expiry、latest-expired/unavailable no-fallback、deterministic snapshot identity 和 fail-closed provider admission。

当前 V1 runtime source 只接纳两指数的 `trend_1m_official_v1` 与 `trend_5m_offset0_v1`；15m/60m 与其他 phase profiles 在当前 provider registry 下返回 `STATE_NOT_ADMITTED`。V1 stable output 不含 T2、`STRONG_*`、five-bucket state、`global_state` 或交易动作字段。

`production_authority=false`、`fresh_oos=false` 保持不变。

**唯一下一步：M8 — 策略层调用集成验证。**

入口：[接管](CONTINUE_HERE.md) · [路线图](docs/ROADMAP.md) · [API 合同](docs/API_CONTRACT.md) · [M7 合同](docs/governance/TREND_M7_CONSUMER_CONTRACT_V1.md)
