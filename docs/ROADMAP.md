# 趋势状态识别组件路线图

> 本路线图定义执行顺序。组件是 Layer 2 市场状态基础设施，不是交易策略。
>
> 执行纪律：一次会话只推进当前里程碑；通过 Gate 后也不自动进入未定义的新研究里程碑。

## 当前进度

- **M0 — PASS**：产品定位、白皮书与路线图。
- **M1 — PASS**：consumer 审计、API 合同与 Gap List。
- **M2 — PASS**：20-bar log-close OLS signed slope t-score 三桶基线，`T1=2.0`。
- **M3 — PASS**：versioned interval/profile registry、view/cadence/as-of 边界。
- **M4 — PASS**：五桶研究协议在 outcome 前冻结。
- **M5 — PASS**：CSI1000 primary、T2 sensitivity、STAR50 replication 收口；原 extreme-slope exhaustion H1 被稳健反驳。
- **M6 — PASS**：正式表示为三桶 + 连续 strength。
- **M7 — PASS**：stable consumer、immutable snapshot、append-only lifecycle、expiry/no-fallback 与 provider admission。
- **M8 — PASS（scope-limited）**：真实外部边界 + synthetic integration 验证完成；STAR50 没有被虚构成已连接的策略 caller。
- **M9 — PASS**：component `1.0.0` release governance、compatibility/migration、API examples、changelog、evidence lineage、known limitations 与 release gate 已冻结。

**M0–M9 路线图已完成。** 后续任何新增能力都必须走独立版本化变更，而不是静默继续扩大 V1。

## M6 正式表示

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

schema：`trend_regime_three_bucket_plus_continuous_strength@1.0`。V1 stable API 不包含 T2、`STRONG_UP/STRONG_DOWN`、five-bucket state 或 `global_state`。

## M7 Stable Consumer（PASS）

Machine authority：`docs/governance/TREND_M7_CONSUMER_CONTRACT_V1.json`。

正式调用面：`query_regime(symbol, as_of, bar_interval, profile_id=None)`。当前 V1 provider admission 仅两指数的 `trend_1m_official_v1` 与 `trend_5m_offset0_v1`；其余 M3 engineering profiles fail closed。Consumer 保持 immutable/append-only、receipt-causal、latest-expired/unavailable no-fallback、`production_authority=false`。

## M8 策略层调用集成验证（PASS）

Machine authority：`docs/governance/TREND_M8_STRATEGY_INTEGRATION_V1.json`。

- CSI1000 私仓存在真实 read-only Layer2 adapter 与 Layer3 orchestration kernel；M7 snapshot 与该 ownership boundary 兼容；
- STAR50 有真实 parallel risk-state provider，但没有被证明存在已连接 external strategy caller；
- synthetic integration 验证多周期状态分离、trend/risk namespace 分离、expired/unavailable 不补成 SIDEWAYS、未准入 profile 在上层前 fail closed；
- Layer2 不产生 `global_state`、BUY/SELL、position/order、strategy selection 或 route。

M8 的 PASS 是接口/所有权边界验证，不是 live/production integration certification。

## M9 发布、版本与治理（PASS）

Machine authority：`docs/governance/TREND_M9_RELEASE_GOVERNANCE_V1.json`。

Component release identity：`factorlab.layer2.trend_regime@1.0.0`。仓库 Python distribution 仍为 `0.1.0`，因为其范围还包含大量历史研究/维护模块；它不是 trend component 的 semantic-version authority。

M9 已冻结：

- stable API/schema compatibility matrix；
- patch/minor/major 变更规则；
- pre-M7 internal usage → V1 migration；
- M2→M9 evidence lineage；
- known limitations；
- `docs/RELEASE.md`、`docs/API_EXAMPLES.md`、`CHANGELOG.md`；
- release gate：必须保持 M6/M7/M8 语义、runtime admission、`production_authority=false`、`fresh_oos=false`，且不得重开 M5/Holdout。

以后如果新增 15m/60m、phase profile、formal STRONG state、global state 或任何 strategy/action authority，必须按 M9 SemVer/governance 重新立项；不能改写 V1 历史 snapshot。

## 全程不变原则

1. 组件不是交易策略。
2. 状态绑定 symbol / as_of / interval / profile / version。
3. V1 是三桶方向 + 连续强度。
4. 当前 runtime source admission 只有两指数 1m official / 5m offset0。
5. 研究阈值不得静默升级为产品语义。
6. `production_authority=false`、`fresh_oos=false` 保持不变，直到未来独立治理明确改变。
