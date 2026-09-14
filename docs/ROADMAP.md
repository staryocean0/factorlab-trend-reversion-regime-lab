# 趋势状态识别组件路线图

> 本路线图定义执行顺序。组件是 Layer 2 市场状态基础设施，不是交易策略。
>
> 执行纪律：原 M0–M9 已完成；任何后续研究必须由新的显式授权与独立治理文件启动，不能静默改写 V1。

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

**M0–M9 路线图已完成。** V1 release pointer 继续保持冻结；Post-V1 研究不会自动移动该 release pointer。

## V1 阶段性成果与证据边界

阶段总结：`docs/governance/TREND_V1_STAGE_CLOSEOUT_V1.md`。

V1 已经完成统一的 measurement family、stable API 与三桶 + continuous strength 表示，但当前 empirical certification 实际只覆盖：

- `000852.SH` / `000688.SH`；
- `trend_1m_official_v1`；
- `trend_5m_offset0_v1`。

因此 V1 不能被解释为已经证明：

- `20 bars` 跨所有 interval 普适；
- `T1=2` 跨所有 interval/phase 普适；
- 不同 profile 的 `abs(slope_t)` 可直接横向比较；
- 15m/60m/其他 phase 已经获得与 1m/5m offset0 相同等级的科学认证。

工程 computability、historical research availability、runtime admission 必须继续严格区分。

## Post-V1：Cross-Profile Invariance & Calibration Study（已授权，执行中）

用户于 2026-09-14 明确授权启动新的独立研究阶段。该阶段**不是自动 M10**，也不是 V1 silent expansion。

Machine protocol：`docs/governance/TREND_CROSS_PROFILE_INVARIANCE_PROTOCOL_V1.json`。

目标：回答“统一趋势测量方法中，哪些部分可以跨 carrier / interval / phase 保持不变，哪些部分必须 profile-specific calibration”。

### X1 — Source/Profile Inventory — COMPLETE

输出：`docs/governance/TREND_CROSS_PROFILE_SOURCE_INVENTORY_V1.json`。

已确认：

- M3 engineering registry 有 10 个 profile；
- 当前 runtime admission 仍只有两指数的 1m official / 5m offset0；
- STAR50 legacy development manifest 保存 1m、5m offset0–4、15m offset5/10、60m offset30/45 exact views，覆盖 2020-07-23 至 2026-08-21；
- CSI1000 two-wave legacy manifest 保存匹配的 exact views，但只到 2020-12-31；
- 两指数可形成 2020-07-23 至 2020-12-31 的 matched Development-only 初始诊断窗口；
- 当前可访问 GitHub 仓库中尚未定位到 `000300.SH`、`000905.SH`、`000016.SH` 的 exact-view source，因此不能假设跨指数扩展数据已具备。

X1 只读取 source metadata，没有读取 market rows、没有计算 outcome、没有调参，也没有改变 runtime admission。

### X2 — Distributional Invariance — NEXT

先固定现有候选：

```text
lookback = 20 bars
score    = slope_t
T1       = 2.0
```

在不调参的前提下，逐 carrier / interval / phase 比较：

- slope_t median / robust scale / quantiles；
- `abs(slope_t)` quantiles；
- 固定 `T1=2` 下 DOWN/SIDEWAYS/UP occupancy；
- 同一 interval 不同 phase 的 dispersion；
- 同一 profile 在两个 carrier 间的 dispersion。

只有 X2 固定基线结果出来后，才允许进入预声明的 `lookback=[10,20,40]`、`T1=[1.5,2.0,2.5]` diagnostic sensitivity；这些 sensitivity 不是产品参数调优。

### X3 — State-Dynamics Invariance

预注册比较：

- state duration distribution；
- one-step transition matrix；
- predeclared bar horizons 的 directional-family survival；
- opposite-direction entry probability。

这一阶段不要求交易收益，不产生 BUY/SELL/position/order 语义。

### X4 — Calibration Decision

只允许从以下结论中选择：

- `UNIVERSAL_FIXED_T1`
- `INTERVAL_SPECIFIC_T1`
- `PROFILE_SPECIFIC_T1`
- `NORMALIZED_SCORE_PLUS_UNIVERSAL_SEMANTIC_THRESHOLD`
- `INSUFFICIENT_EVIDENCE`

原则：选择能够维持可比较状态语义的**最简单** calibration family，不按未来交易收益最大化阈值。

### X5 — Cross-Carrier Expansion

在声称“普适规律”之前，目标至少覆盖 5 个结构上有差异的指数族。当前额外候选仅作为 source search target，不视为已准入：`000300.SH`、`000905.SH`、`000016.SH`。

### X6 — Representation Version Decision

根据 X2–X5 结果决定：

- V1 保持不变；或
- backward-compatible minor metadata/calibration extension；或
- 若 T1/lookback/strength semantics 需要变化，则新 major representation。

历史 V1 snapshots 永不原地改写。

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
- `docs/governance/TREND_V1_RELEASE.md`、`docs/governance/TREND_V1_API_EXAMPLES.md`、`docs/governance/TREND_V1_CHANGELOG.md`；
- release gate：必须保持 M6/M7/M8 语义、runtime admission、`production_authority=false`、`fresh_oos=false`，且不得重开 M5/Holdout。

## 全程不变原则

1. 组件不是交易策略。
2. 状态绑定 symbol / as_of / interval / profile / version。
3. V1 是三桶方向 + 连续强度。
4. 当前 runtime source admission 只有两指数 1m official / 5m offset0。
5. 研究阈值不得静默升级为产品语义。
6. Cross-profile 研究不得重跑 M5、不得打开旧 M4/M5 2025 Holdout。
7. Legacy exact view 即使被新研究使用，也不会因此自动获得 runtime admission。
8. `production_authority=false`、`fresh_oos=false` 保持不变，直到未来独立治理明确改变。
