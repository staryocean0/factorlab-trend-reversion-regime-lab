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

M9 component release identity：`factorlab.layer2.trend_regime@1.0.0`。仓库 Python distribution 仍为 `0.1.0`，因为其范围还包含历史研究/回放/维护模块，不能把这些模块一并宣称为 stable 1.0 API。

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

- CSI1000 私仓已有真实 read-only Layer2 consumer adapter / Layer3 orchestration boundary，M7 trend snapshot 与该所有权模型兼容。
- STAR50 仓已有真实 append-only risk-state consumer，但其示例明确没有 connected external strategy caller；所以这里只认证为并行 Layer2 risk-provider boundary。
- Synthetic integration 验证多周期状态可保持不同、trend/risk namespace 分离、expired/unavailable 不被补成 SIDEWAYS、未准入 profile 在上层前 fail closed。
- Layer2 不产生策略选择、路由、仓位、订单或交易动作。

因此 M8 的 PASS 是接口/所有权边界验证，不是 live/production integration certification。

## 5. M9 Release / Version / Governance（PASS）

Machine authority：`docs/governance/TREND_M9_RELEASE_GOVERNANCE_V1.json`。

M9 把 M0–M8 已冻结的技术与研究边界整理成稳定发布合同，而不是新增模型能力。已经冻结：

- component semantic version `1.0.0`；
- stable query/schema compatibility matrix；
- patch/minor/major 变更规则；
- pre-M7 internal usage → V1 migration；
- M2→M9 evidence lineage；
- API examples / changelog / release policy；
- known limitations；
- release gate 与 forbidden release actions。

Semantic change 必须新 schema/version identity；历史 V1 snapshots 永不原地重写。新增 profile/provider admission 也必须有新的 exact source admission receipt 和版本化治理。

## 6. V1 证据与部署限制

- persistence/strength empirical certification 只覆盖 admitted 1m/5m 与 CSI1000/STAR50；
- 15m/60m 和 phase profiles 没有同等级认证，也没有进入 V1 runtime admission；
- STAR50 没有已证明的 connected external strategy caller；
- M8 不是 live deployment certification；
- 2025 protocol Holdout 未打开；
- Layer2 不自行声明完整交易日日历 authority；
- `production_authority=false`、`fresh_oos=false`。

## 7. 路线图收口

M0–M9 已完成。后续变化必须按 M9 SemVer/source-admission/authority governance 重新立项，而不是静默扩大 V1 或自动进入未定义的 M10。

发布动作本身不能改变研究结论、representation、consumer lifecycle、runtime admission 或 authority。
