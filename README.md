# FactorLab 趋势状态识别组件

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 当前产品状态

**M0–M9 已完成。** 本仓交付的是 Layer 2 趋势状态识别组件，不是交易策略。

Component release：`factorlab.layer2.trend_regime@1.0.0`。仓库 `pyproject.toml` distribution 仍为 `0.1.0`，因为它还包含大量历史研究和维护模块；该 distribution 不是 trend component 的 SemVer authority。

正式表示：

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

Stable consumer：`regime_state_consumer_v1`；snapshot：`trend_regime_snapshot@1.0`；正式入口：`query_regime(symbol, as_of, bar_interval, profile_id=None)`。

当前 V1 runtime 只接纳两指数的 `trend_1m_official_v1` 与 `trend_5m_offset0_v1`；其他 M3 profiles 仍 `STATE_NOT_ADMITTED`。M7 的 immutable/append-only、causal receipt visibility、expiry/no-fallback 与 provider admission 保持不变。

M8 的结论保持 scope-limited：CSI1000 的真实 Layer2→Layer3 ownership boundary 已验证；STAR50 有真实 parallel risk-state provider，但没有被证明存在 connected external strategy caller。

M9 已冻结 component compatibility、migration、API examples、changelog、evidence lineage、known limitations 和 release gate。以后任何 semantic change 都必须新 schema/version identity，不能静默改写 V1 snapshot 或扩大 authority。

`production_authority=false`、`fresh_oos=false` 保持不变。V1 不产生交易动作、仓位、订单、策略选择、路由或 Layer2 `global_state`。

## V1 文档入口

- `docs/API_CONTRACT.md`
- `docs/governance/TREND_V1_API_EXAMPLES.md`
- `docs/governance/TREND_V1_RELEASE.md`
- `docs/governance/TREND_V1_CHANGELOG.md`
- `docs/governance/TREND_M9_RELEASE_GOVERNANCE_V1.json`
- `CONTINUE_HERE.md`

M0–M9 路线图已经收口。后续新增能力必须按 M9 versioned governance 独立立项，而不是自动进入未定义的新里程碑。
