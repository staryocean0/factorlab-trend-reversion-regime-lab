# 趋势状态识别组件 API 合同（M1–M9 已冻结）

> 状态：**M9 已完成 V1 release governance。** M7 stable consumer 与 M8 上层所有权边界保持不变。
>
> Component release：`factorlab.layer2.trend_regime@1.0.0`。
>
> `production_authority=false`、`fresh_oos=false`。组件不输出买卖、仓位、订单、策略路由或多周期总趋势。

## 1. 正式调用面

```text
query_regime(
    symbol,
    as_of,
    bar_interval,
    profile_id = optional_when_unambiguous,
) -> RegimeQueryResult
```

Caller 只拥有 `symbol`、timezone-aware `as_of`、`bar_interval` 以及需要时的 `profile_id`。Caller 不得传入 lookback、estimator、T1/T2、normalization、provider admission、publication/validity policy 或 strategy action。

## 2. 正式产品表示

Machine authority：`docs/governance/TREND_M6_REPRESENTATION_DECISION_V1.json`。

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

representation schema：`trend_regime_three_bucket_plus_continuous_strength@1.0`。稳定 API 禁止 `STRONG_UP/STRONG_DOWN`、five-bucket state、T2 与 `global_state`。

## 3. Consumer / Snapshot schema

Consumer schema：`regime_state_consumer_v1`。Snapshot schema：`trend_regime_snapshot@1.0`。

AVAILABLE snapshot 至少包含 snapshot identity、symbol/interval/profile/view、decision/observation/publication/expiry clocks、`state/directional_score/strength`、representation identities、provider/source/receipt identities、measurement estimator identity，以及 `production_authority=false`。

Unavailable 查询返回 `snapshot=null`，不得把不可用伪装成 SIDEWAYS 或泄露旧 state/score/strength。

## 4. Snapshot lifecycle

M7 runtime 已实现：immutable snapshot、append-only ingest、duplicate identity guard、publication-before-receipt causality、receipt/source ordering、as-of receipt visibility、expiry，以及 **latest-expired / latest-explicit-unavailable no fallback**。

`valid_until` 属于 component/provider publication layer，不是 query caller 参数。Consumer 不自行猜测 Layer1 交易日完整性。

## 5. 当前 provider admission

当前 V1 registry 冻结为：

- provider `datahub`
- dataset `factorlab_unified_index_kline_v3_20260824`
- symbols `000688.SH`, `000852.SH`
- profiles `trend_1m_official_v1`, `trend_5m_offset0_v1`
- admission receipt `trend_m5_source_profile_admission_v1_20260914`

其他 M3 engineering profiles 在当前 runtime 下 fail closed 为 `STATE_NOT_ADMITTED`。不得由 caller/constructor 扩张 V1 registry。

## 6. Fail-closed reason families

包括 `NO_PUBLISHED_SNAPSHOT`、`LATEST_SNAPSHOT_EXPIRED`、`UNSUPPORTED_SYMBOL`、`UNSUPPORTED_PROFILE`、`STATE_NOT_ADMITTED`、`INSUFFICIENT_HISTORY`、`SOURCE_UNAVAILABLE`、`OUTSIDE_SUPPORTED_TIME`、`MEASUREMENT_INVALID`、`CADENCE_GAP`、`OFF_PROFILE_GRID`。

## 7. Immutability / identity

`snapshot_id` 绑定 provider/source、symbol、interval/profile/view 与 decision time。同 identity 内容不得改写。Estimator、T1、representation、profile/view 或 provider/source admission 改变必须新版本；`source_receipt_id` 必须是非空字符串。

## 8. M8 上层集成边界

Machine authority：`docs/governance/TREND_M8_STRATEGY_INTEGRATION_V1.json`。

1. Layer2 trend snapshot 是只读输入；caller 不在 Layer2 adapter 中修改 value/threshold/state semantics。
2. 同一 as-of 的 1m/5m snapshot 可以不同，必须分别上送；Layer2 不创建 `global_state`。
3. trend 与 risk 是并行 Layer2 namespaces；融合、冲突仲裁、选择属于 Layer3 或更高层。
4. `UNAVAILABLE` / expired 不能被 caller 转成 SIDEWAYS 来补值。
5. BUY/SELL、position/order、strategy/plugin selection、routing 全部在 Layer2 之外。
6. M8 不创建 production wiring，也不授权 production。

CSI1000 私仓已有真实 read-only Layer2 adapter 和 Layer3 orchestration kernel，M8 验证与其所有权模型兼容。STAR50 仓已有真实 risk-state consumer，但未证明有 connected external strategy caller；不能扩大表述。

## 9. M9 version / compatibility contract

Machine authority：`docs/governance/TREND_M9_RELEASE_GOVERNANCE_V1.json`。

Component semantic version：`1.0.0`。仓库 `pyproject.toml` distribution 仍是 `0.1.0`，因为其还包含大量历史研究和维护模块，**不作为 trend component semantic-version authority**。

Compatibility rule：

- **1.0.x patch**：只能做文档、测试/CI、内部重构且公共语义完全不变。
- **1.x minor**：只能做向后兼容增量；新增 provider/profile 必须先有新的 exact source admission receipt，旧 caller 行为不变。
- **new major**：state enum/T1、estimator、directional score、strength、required query semantics、snapshot identity、expiry/no-fallback、formal T2/STRONG state、Layer2 global state、strategy/action authority 任一发生语义变化。

任何 semantic change 必须获得新 schema/version identity；历史 V1 snapshots 永不原地改写。

迁移、API examples、known limitations、evidence lineage 和 release gate 分别见：

- `docs/governance/TREND_V1_RELEASE.md`
- `docs/governance/TREND_V1_API_EXAMPLES.md`
- `docs/governance/TREND_V1_CHANGELOG.md`
- `docs/governance/TREND_M9_RELEASE_GOVERNANCE_V1.json`

## 10. Governance closeout

M0–M9 已完成。后续新增能力不属于“继续执行 M10”，而应按 M9 SemVer/governance 新建立版本化变更。

V1 不得通过发布动作重开 M5、读取 2025 Holdout、扩大当前 source admission、引入 five-bucket product semantics，或把 `production_authority` / `fresh_oos` 改为 true。
