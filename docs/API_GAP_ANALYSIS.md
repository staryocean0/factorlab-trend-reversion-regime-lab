# 趋势状态 Consumer：M1 现状审计与 Gap List

> 本文是 `docs/API_CONTRACT.md` 的配套审计。它回答“当前仓库离目标 consumer 还有什么差距”，不把后续 M2–M7 的工作提前宣称完成。

## 1. 审计结论

当前仓库**已经具备 Layer 2 measurement plane 的权责边界和一批测量原语，但尚未具备正式可供策略调用的 trend-regime consumer**。

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

### A04 — 存在趋势/方向相关测量原语

`core_kline_attribute_pool.py` 当前已有包括：

- signed efficiency ratio；
- signed OLS slope t-stat；
- direction continuity / imbalance 类指标；
- volatility、reversal、jump 等基础属性。

**结论：M2 应审计这些现有原语后选择/冻结三桶基线，不应在 M1 新造公式。**

### A05 — 风险组件提供成熟 consumer 参考

`factorlab-star50-filter-lab/research/state_degree_consumer_d5/consumer.py` 已示范：

- immutable Snapshot；
- append-only ingest；
- as-of 查询；
- published/expiry；
- missing/expired 显式失败；
- latest expired 不回退；
- production authority=false。

**结论：借鉴 envelope 和时钟纪律，不复制风险业务字段。**

## 3. 当前缺口

| ID | Gap | 当前证据 | 目标 | 归属里程碑 |
|---|---|---|---|---|
| G01 | 没有公开 trend consumer entrypoint | 当前只有 measurement registry/validation 与底层属性模块 | `query_regime` / `as_of` facade | M7 |
| G02 | 没有正式 `regime_state_consumer_v1` schema | measurement plane schema 面向能力/坐标，不是 current-state query | 稳定 consumer envelope | M7，合同已在 M1 冻结 |
| G03 | 没有统一 current-state lifecycle | 有 `observation_time/available_at`，但无统一 `published_at/valid_until` 状态快照 | snapshot clocks + no-fallback | M2/M3 定规则，M7 实现 |
| G04 | 缺失/过期语义未统一到趋势调用面 | 各历史组件各自处理或根本不是 runtime consumer | `AVAILABLE/UNAVAILABLE + reason` | M7 |
| G05 | caller 与 component 参数所有权未通过公开 API 固化 | measurement plane 明确“不拥有 parameter selection”，但调用 facade 不存在 | caller 只选 versioned profile；低层参数由 component/profile 拥有 | M3/M7 |
| G06 | 三桶数学语义尚未冻结 | 当前有多个 slope/direction primitives，但没有一个被正式指定为 `DOWN/SIDEWAYS/UP` authority | 可复现三桶基线 | M2 |
| G07 | K 线完成、lookback、normalization、T1 尚未冻结 | 现有属性原语存在多 horizon/不同统计口径 | 单一基线定义与回归样例 | M2 |
| G08 | 多周期 profile 尚未冻结 | capability matrix 中有 daily、60m、caller-declared 等混合历史能力 | versioned profile / bar interval registry | M3 |
| G09 | 五桶没有正式证据 | 当前只是 H1“极端斜率耗竭”研究假设 | 预注册协议与实证裁决 | M4–M6 |
| G10 | capability registry 不等于本仓可执行 provider | registry 的若干 `source_refs` 指向当前 checkout 不存在的历史源码，且多项 capability 为 partial/compatibility | provider admission 必须验证实际 artifact/acceptance | M2–M7 |
| G11 | 没有 trend snapshot identity/immutable store | 当前 registry/attributes 不是发布事件存储 | stable snapshot ID + append-only semantics | M7 |
| G12 | 没有 consumer conformance / prefix-causality tests | 现有测试主要服务历史组件和治理 | API、expiry、no-fallback、future-leak、immutability tests | M7 |
| G13 | 当前组件索引没有把 trend consumer 登记为 active callable component | `docs/COMPONENTS.md` 仍以历史/复现生命周期为主 | consumer 生命周期、owner、version、status | M7/M9 |
| G14 | strategy integration 尚未证明 | 当前没有至少两个不同持仓逻辑只依赖公开 trend contract 的验收 | 两类调用者集成，不复制组件代码 | M8 |

## 4. 关键架构判断

### 4.1 不重写 measurement plane

现有 measurement plane 已经解决了“Layer 2 能测什么、来自哪里、是否有 measurement authority”的问题。直接另建一套平行 Layer 2 会制造双重 authority。

后续应把 trend consumer 视为其上方的**受限读取/状态发布面**。

### 4.2 capability registry 不能直接当 runtime provider registry

当前 capability matrix 是历史资产与能力分母，不能把：

```text
asset_id exists
```

等价为：

```text
provider executable + causal + accepted + current
```

尤其是当前裁剪仓 `src/factor_lab/market_state/` 实际只保留少量模块，而 capability rows 仍保存若干旧 source refs。

因此未来 profile 只能绑定通过 admission 的 provider；找不到实现、receipt 或 acceptance 时必须 fail closed。

### 4.3 三桶先于五桶

当前存在 signed OLS、efficiency、direction-continuity 等多种候选测量，说明“趋势强度”并非天然只有一个公式。

M2 必须先回答：

- 哪一个量才是三桶 authority；
- 为什么；
- K 线如何完成；
- lookback 和 normalization 是什么；
- `T1` 如何定义；
- 是否满足前缀因果与可复现。

在这之前不能开始调 `T2` 或把 extreme bucket 做成产品字段。

## 5. M1 已解决 vs 尚未解决

### M1 已解决

- 独立组件 vs 策略的接口边界；
- caller / component / strategy 参数所有权；
- `as_of` 消费模型；
- availability / expiry / no-fallback 语义；
- snapshot/provenance/authority envelope；
- provider admission 原则；
- 最小 schema 草案 `regime_state_consumer_v1`。

### M1 刻意未解决

- 三桶使用哪个 slope/strength 公式；
- `T1`；
- 支持哪些 bar intervals；
- profile 清单；
- 五桶是否成立；
- consumer 代码实现；
- production authority。

这些未解决项不是 M1 失败，而是路线图刻意留下的后续 Gate。

## 6. M1 Gate 判定

**PASS。**

原因：目标 consumer 可以在不知道任何交易策略的情况下独立定义；接口不包含买卖/仓位/路由语义；安全时钟与 unavailable 语义已经明确；当前实现与目标之间的缺口有清晰里程碑归属。

因此下一唯一里程碑为 **M2 — 三桶基线冻结与可复现性**。
