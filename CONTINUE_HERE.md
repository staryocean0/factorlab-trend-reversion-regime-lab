# 从这里接管

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 当前状态

本仓是 Layer 2 趋势状态识别组件，不是交易策略。**M0–M9 PASS**；原路线图已经收口。

Component release identity：`factorlab.layer2.trend_regime@1.0.0`。

接管必读：

- `docs/ROADMAP.md`
- `docs/API_CONTRACT.md`
- `docs/governance/TREND_V1_RELEASE.md`
- `docs/governance/TREND_V1_API_EXAMPLES.md`
- `docs/governance/TREND_V1_CHANGELOG.md`
- `docs/governance/TREND_M7_CONSUMER_CONTRACT_V1.json`
- `docs/governance/TREND_M8_STRATEGY_INTEGRATION_V1.json`
- `docs/governance/TREND_M9_RELEASE_GOVERNANCE_V1.json`

## 正式产品与 consumer

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

入口：`query_regime(symbol, as_of, bar_interval, profile_id=None)`。

M7 lifecycle 已冻结：immutable/append-only、receipt-causal as-of、expiry、latest-expired/unavailable no-fallback、stable source/provider identities。当前 runtime admission 仍只包括两指数 `trend_1m_official_v1` / `trend_5m_offset0_v1`；其他 M3 profiles fail closed。

## M8 边界保持不变

- CSI1000 私仓存在真实 read-only Layer2 adapter 与 Layer3 orchestration kernel；M7 trend snapshot 与该 ownership boundary 兼容。
- STAR50 存在真实 parallel risk-state provider，但没有被证明存在 connected external strategy caller。
- 多周期组合、trend/risk 融合、冲突仲裁、策略选择和最终动作全部在 Layer2 之外。

## M9 已完成

Machine authority：`docs/governance/TREND_M9_RELEASE_GOVERNANCE_V1.json`。

已冻结：

- component semantic version `1.0.0`；
- stable schema/API compatibility matrix；
- patch/minor/major rules；
- migration；
- M2→M9 evidence lineage；
- API examples、changelog、known limitations；
- release gate 与 forbidden release actions。

仓库 `pyproject.toml` distribution 仍为 `0.1.0`，因为它包含超出 trend component stable surface 的历史研究/维护模块；不要把 package version 当成 component SemVer authority。

## 仍然禁止

- 重跑 M5 或读取 2025 Holdout；
- 修改 M6 representation 或 M7 lifecycle/admission 而不升级版本；
- 无新 exact source receipt 就扩张 15m/60m/phase provider admission；
- 在 Layer2 输出 `global_state`、交易动作、position/order、strategy selection/routing；
- 把 STAR50 说成已经连接 external strategy caller；
- 把 M8 说成 live deployment certification；
- 把 release 动作解释成 `production_authority=true` 或 `fresh_oos=true`。

## 后续如何继续

没有自动 M10。后续需求先分类：

- 不改语义的 bugfix/docs/test → V1 patch；
- 向后兼容的新 admitted source/profile → 新 exact receipt + minor version；
- 改 state/T1/estimator/strength/snapshot lifecycle、引入 formal strong/global/action semantics → new major version；
- production/live/OOS certification → 独立治理项目，不由 component SemVer 自动授予。

历史 V1 snapshots 不得原地改写。
