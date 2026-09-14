# 趋势状态 Consumer：M1 现状审计与 Gap List

> 本文是 `docs/API_CONTRACT.md` 的配套审计，并随里程碑更新 gap 状态。M2 已冻结三桶 measurement baseline；正式 consumer 仍未进入 M7。

## 1. 审计结论

当前仓库**已经具备 Layer 2 measurement plane、M2 三桶趋势测量基线和一批辅助测量原语，但尚未具备正式可供策略调用的 trend-regime consumer**。

因此正确演进路径不是重写 Layer 2，而是：

```text
保留已有 measurement plane
        +
冻结/补齐 trend state semantics（M2–M6）
        +
新增稳定 as-of consumer facade（M7）
```

## 2. 已经具备的基础

### A01 — Layer 2 authority 边界已经存在

`src/factor_lab/market_state/timing_layer2_measurement_plane.py` 明确：

- measurement authority = true；
- strategy selection = false；
- parameter selection = false；
- routing = false；
- production = false。

**结论：保留。** 新 consumer 继承该 authority，不另造策略 authority。

### A02 — 因果测量坐标已经存在

`Layer2MeasurementCoordinate` 已包含：

- `observation_time`
- `available_at`
- source/version
- source receipt SHA-256
- estimator/version
- bar authority
- gap policy
- quality status

并要求 timezone-aware、禁止 available time 早于 observation time。

**结论：复用为 snapshot provenance 的底层合同。**

### A03 — 策略字段污染已有防线

measurement plane 已拒绝 `position/action/selected_*` 等策略字段。

**结论：M1 API 合同把这条限制提升到公开 consumer 语义。**

### A04 — 趋势/方向原语与 M2 主 authority

`core_kline_attribute_pool.py` 当前已有 signed efficiency ratio、signed OLS slope t-stat、direction continuity / imbalance 等属性；BDCI/DII 也提供辅助方向诊断。

M2 已进一步冻结 `src/factor_lab/market_state/trend_regime_baseline.py`：20 根 completed bars、log-close signed OLS slope t-score、`T1=2.0`，唯一决定 `DOWN/SIDEWAYS/UP`。BDCI/DII 不参与主状态投票。

### A05 — 风险组件提供成熟 consumer 参考

`factorlab-star50-filter-lab/research/state_degree_consumer_d5/consumer.py` 已示范 immutable Snapshot、append-only ingest、as-of 查询、published/expiry、missing/expired 显式失败、latest expired 不回退以及 production authority=false。

**结论：借鉴 envelope 和时钟纪律，不复制风险业务字段。**

## 3. 当前缺口

| ID | Gap | 当前状态 | 目标 | 归属里程碑 |
|---|---|---|---|---|
| G01 | 没有公开 trend consumer entrypoint | OPEN：当前有 measurement primitive，无 `query_regime` facade | `query_regime` / `as_of` facade | M7 |
| G02 | 没有正式运行中的 `regime_state_consumer_v1` schema | OPEN：M1 已冻结合同，代码未实现 | 稳定 consumer envelope | M7 |
| G03 | 没有统一 current-state lifecycle | PARTIAL：M2 已冻结 bar-level `as_of/observation_time/available_at`；尚无 snapshot `published_at/valid_until` 与 expiry store | snapshot clocks + no-fallback | M3/M7 |
| G04 | 缺失/过期语义未统一到趋势 consumer | PARTIAL：M2 measurement 已 fail-closed；consumer expiry/no-fallback 未实现 | `AVAILABLE/UNAVAILABLE + reason` | M7 |
| G05 | caller 与 component 参数所有权未通过公开 API 固化 | PARTIAL：M1 已定原则，M2 低层参数已冻结；profile registry 尚不存在 | caller 只选 versioned profile | M3/M7 |
| G06 | 三桶数学语义尚未冻结 | **RESOLVED M2**：`log_close_ols_slope_t@1.0` 是唯一主 authority | 可复现三桶基线 | M2 PASS |
| G07 | K 线完成、lookback、normalization、T1 尚未冻结 | **RESOLVED M2**：20 bars、log-close、`T1=2.0`、completed+available as-of、坏 close fail-closed | 单一基线定义与回归样例 | M2 PASS |
| G08 | 多周期 profile 尚未冻结 | OPEN：M2 刻意不绑定 interval，也不猜 cadence gap | versioned profile / bar interval registry | M3 |
| G09 | 五桶没有正式证据 | OPEN：仍只是 H1“极端斜率耗竭”研究假设 | 预注册协议与实证裁决 | M4–M6 |
| G10 | capability registry 不等于本仓可执行 provider | OPEN：M1 已确认旧 source refs 不能当 runtime admission；M2 新 baseline 是实际可执行 primitive | provider admission 验证 artifact/acceptance | M3–M7 |
| G11 | 没有 trend snapshot identity/immutable store | OPEN | stable snapshot ID + append-only semantics | M7 |
| G12 | 没有 consumer conformance / prefix-causality tests | PARTIAL：M2 已有 measurement future-leak/as-of 回归；consumer expiry/immutability tests 尚无 | consumer API、expiry、no-fallback、immutability tests | M7 |
| G13 | 当前组件索引没有把 trend consumer 登记为 active callable component | OPEN | consumer 生命周期、owner、version、status | M7/M9 |
| G14 | strategy integration 尚未证明 | OPEN | 两类调用者集成，不复制组件代码 | M8 |

## 4. 关键架构判断

### 4.1 不重写 measurement plane

现有 measurement plane 已经解决“Layer 2 能测什么、来自哪里、是否有 measurement authority”。直接另建平行 Layer 2 会制造双重 authority。

M2 新增的是受该边界约束的趋势 measurement primitive；未来 trend consumer 仍应是其上方的**受限读取/状态发布面**。

### 4.2 capability registry 不能直接当 runtime provider registry

当前 capability matrix 是历史资产与能力分母，不能把：

```text
asset_id exists
```

等价为：

```text
provider executable + causal + accepted + current
```

审计还确认 capability row 引用的旧 `trend_continuity_regime.py` 在本仓没有可恢复实现，所以 M2 没有伪称“恢复旧公式”，而是从当前可审计的 signed OLS 原语冻结了新基线。

未来 profile 只能绑定通过 admission 的 provider；找不到实现、receipt 或 acceptance 时必须 fail closed。

### 4.3 三桶已经冻结，五桶仍未开始

M2 现在明确：

- 主 authority：signed log-close OLS slope t-score；
- lookback：20 completed/available bars；
- `T1=2.0`；
- `-2/+2` 都属于 SIDEWAYS；
- future/unpublished bars 不可见；
- 坏 close 不跳过、不回填、不插值。

这解决的是**参考定义**，没有证明 20 或 2.0 是任何时间尺度上的收益最优参数，也没有给 `T2` 或 `STRONG_*` 任何产品 authority。

## 5. 已完成与尚未解决

### 已完成：M1 + M2

- 独立组件 vs 策略的接口边界；
- caller / component / strategy 参数所有权原则；
- consumer `as_of`/availability/expiry/no-fallback 合同；
- snapshot/provenance/authority envelope；
- provider admission 原则；
- `regime_state_consumer_v1` 最小合同；
- 三桶数学 authority、20-bar lookback、log-close、`T1=2.0`；
- completed/available as-of 与 measurement fail-closed；
- 合成因果与可复现回归测试。

### 仍未解决

- 正式支持哪些 `bar_interval`；
- interval/profile registry 与 cadence-gap admission；
- `T1` 在不同 K 线周期下是否需要不同 profile/解释；
- 五桶是否成立；
- consumer snapshot/store 代码；
- production authority；
- strategy integration。

## 6. 当前 Gate

**M1 PASS；M2 PASS。**

下一唯一里程碑为 **M3 — 多 K 线级别参数化**。M3 只解决 interval/profile 与跨周期测量可解释性，不自动进入 M4/M5 的五桶研究。
