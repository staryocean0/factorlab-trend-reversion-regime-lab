# 趋势状态 Consumer：当前 Gap List（已吸收 M2/M3）

> 本文追踪当前仓库距离最终 `regime_state_consumer_v1` 仍有哪些差距。M2/M3 已解决的 measurement/profile 问题不再列为未完成，但不等于 M7 consumer 已实现。

## 1. 当前结论

当前仓库已经具备：

- Layer-2 measurement-plane authority 边界；
- M2 三桶数学与 as-of/fail-closed 基线；
- M3 `1m/5m/15m/60m` 的 10 个 versioned profiles；
- view/cadence admission；
- 同一 `as_of` 多周期独立并存表达。

正确演进路径仍是：

```text
existing Layer-2 measurement plane
        +
M2/M3 frozen trend measurements/profiles
        +
M4-M6 state-representation evidence
        +
M7 stable as-of consumer facade
```

## 2. 已解决项

| ID | 原 Gap | 解决状态 |
|---|---|---|
| G05 | caller 与 component 参数所有权未通过公开 API 固化 | **M3 RESOLVED**：caller 选 `bar_interval/profile_id`；lookback/estimator/T1/grid 由 versioned profile 持有 |
| G06 | 三桶数学语义未冻结 | **M2 RESOLVED**：20-bar log-close OLS signed slope t-score，`T1=2.0` |
| G07 | completed-bar/lookback/normalization/T1 未冻结 | **M2 RESOLVED**：completed+available prefix、20 bars、log-close、T1=2、坏值 fail closed |
| G08 | 多周期 profile 未冻结 | **M3 RESOLVED**：1m×1、5m×5、15m×2、60m×2，共 10 profiles |
| G15 | interval cadence 缺口无法判定 | **M3 RESOLVED（session grid 层）**：`CADENCE_GAP/OFF_PROFILE_GRID` fail closed；整日交易日缺失仍归 Layer-1 receipt |
| G16 | 多周期是否自动合成总趋势不明确 | **M3 RESOLVED**：multi-interval envelope 无 `state/global_state`，聚合属于策略层 |

## 3. 仍未解决的核心 Gap

| ID | Gap | 当前证据 | 目标 | 归属里程碑 |
|---|---|---|---|---|
| G01 | 没有正式公开 trend consumer entrypoint | 目前是 measurement primitives/wrappers | `query_regime` / `as_of` facade | M7 |
| G02 | `regime_state_consumer_v1` 尚未代码实现 | schema/contract 已文档冻结 | 稳定 consumer envelope | M7 |
| G03 | 没有正式 snapshot lifecycle/store | M2/M3 有 `observation_time/available_at`，无 consumer `published_at/valid_until` store | immutable snapshot + expiry/no-fallback | M7 |
| G04 | consumer 缺失/过期语义尚未代码化 | contract 已冻结，measurement 有 fail-closed | consumer `AVAILABLE/UNAVAILABLE + reason` | M7 |
| G09 | 五桶没有正式证据 | 仅有 H1“极端斜率耗竭”假设 | 预注册协议 + 实证 + 架构裁决 | M4–M6 |
| G10 | capability registry 不等于可执行 provider | 历史 capability/source refs 与当前 checkout 不完全一致 | provider acceptance/receipt admission | M7/M9 |
| G11 | 没有 trend snapshot identity/append-only history | measurement result 不是发布事件存储 | stable snapshot ID + immutable history | M7 |
| G12 | 没有 consumer conformance/expiry/no-fallback tests | M2/M3 已有 prefix/cadence tests | consumer contract regression suite | M7 |
| G13 | 组件索引尚未登记正式 callable consumer 生命周期 | 当前仍是 support/measurement 工程 | owner/version/status/migration | M7/M9 |
| G14 | strategy integration 尚未证明 | 尚无两个不同持仓逻辑只依赖公开 consumer contract | 多调用者集成，不复制组件代码 | M8 |
| G17 | 跨完整交易日缺失的完整性 authority 不在 Layer-2 | M3 只能验证 wall-clock grid 与 session edge | Layer-1 calendar/provider receipt admission | M7/M9 与上游协同 |

## 4. M2/M3 关键架构判断

### 4.1 不重写 measurement plane

现有 measurement plane 继续作为“能测什么、来自哪里”的 authority 根。M2/M3 只在其上冻结趋势测量与 profile，不建立平行 Layer 2。

### 4.2 不把 capability registry 当 runtime provider registry

`asset_id exists` 不等于 `provider executable + causal + accepted + current`。正式 consumer 仍必须验证实现、source identity/receipt、clock、profile admission 与 acceptance。

### 4.3 不按周期提前调参

M3 的 10 个 profiles 全部保留 M2 `20 bars + T1=2.0`。这是为了维持一个未经过绩效搜索的统一基线，不是宣称它已经被证明在所有周期上最优。

### 4.4 不自动聚合时间尺度

不同 timeframe 的状态可以冲突。Layer 2 只返回独立 measurements；如何组合属于 strategy layer。

## 5. 下一唯一任务

**M4 — 五桶假设与实验协议冻结。**

M4 只允许预注册：`T2` 候选、纳入 profiles、样本切分、forward horizons、持续时间/转移概率/方向延续率、reversal metrics、adverse/favorable excursion、稳健性、最小样本量、停止条件和负结果处理。

在协议冻结之前不得运行 M5；M4 也不得把 `STRONG_UP/STRONG_DOWN` 写成正式产品状态。
