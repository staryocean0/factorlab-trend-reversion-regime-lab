# 趋势状态 Consumer：当前 Gap List（已吸收 M2/M3/M4）

> 本文追踪当前仓库距离最终 `regime_state_consumer_v1` 仍有哪些差距。M2/M3 已解决 measurement/profile 问题；M4 已冻结五桶实验协议，但五桶证据仍未产生，也不等于 M7 consumer 已实现。

## 1. 当前结论

当前仓库已经具备：

- Layer-2 measurement-plane authority 边界；
- M2 三桶数学与 as-of/fail-closed 基线；
- M3 `1m/5m/15m/60m` 的 10 个 versioned profiles；
- view/cadence admission；
- 同一 `as_of` 多周期独立并存表达；
- M4 在结果之前冻结的五桶 H1 实验协议与机器可读合同。

正确演进路径仍是：

```text
existing Layer-2 measurement plane
        +
M2/M3 frozen trend measurements/profiles
        +
M4 frozen five-bucket protocol
        +
M5 evidence + M6 representation decision
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
| G18 | 五桶实验可被结果驱动改阈值/切分/profile/horizon | **M4 RESOLVED**：`trend_five_bucket_protocol_m4@1.0` 已冻结 primary T2、sensitivity、样本切分、anchors、endpoints、sample guards、bootstrap、Holm、holdout unlock 和负结果规则 |

## 3. 仍未解决的核心 Gap

| ID | Gap | 当前证据 | 目标 | 归属里程碑 |
|---|---|---|---|---|
| G01 | 没有正式公开 trend consumer entrypoint | 目前是 measurement primitives/wrappers | `query_regime` / `as_of` facade | M7 |
| G02 | `regime_state_consumer_v1` 尚未代码实现 | schema/contract 已文档冻结 | 稳定 consumer envelope | M7 |
| G03 | 没有正式 snapshot lifecycle/store | M2/M3 有 `observation_time/available_at`，无 consumer `published_at/valid_until` store | immutable snapshot + expiry/no-fallback | M7 |
| G04 | consumer 缺失/过期语义尚未代码化 | contract 已冻结，measurement 有 fail-closed | consumer `AVAILABLE/UNAVAILABLE + reason` | M7 |
| G09 | 五桶没有正式市场证据 | **M4 protocol 已冻结，但尚未运行 M5** | 按冻结协议完成 validation/holdout/replication，再由 M6 裁决 | M5–M6 |
| G10 | capability registry 不等于可执行 provider | 历史 capability/source refs 与当前 checkout 不完全一致；M4 要求 exact profile receipt admission | provider acceptance/receipt admission | M5 source admission + M7/M9 |
| G11 | 没有 trend snapshot identity/append-only history | measurement result 不是发布事件存储 | stable snapshot ID + immutable history | M7 |
| G12 | 没有 consumer conformance/expiry/no-fallback tests | M2/M3 已有 prefix/cadence tests；M4 有 protocol invariant tests | consumer contract regression suite | M7 |
| G13 | 组件索引尚未登记正式 callable consumer 生命周期 | 当前仍是 support/measurement 工程 | owner/version/status/migration | M7/M9 |
| G14 | strategy integration 尚未证明 | 尚无两个不同持仓逻辑只依赖公开 consumer contract | 多调用者集成，不复制组件代码 | M8 |
| G17 | 跨完整交易日缺失的完整性 authority 不在 Layer-2 | M3 只能验证 wall-clock grid 与 session edge | Layer-1 calendar/provider receipt admission | M5/M7/M9 与上游协同 |

## 4. M2–M4 关键架构判断

### 4.1 不重写 measurement plane
现有 measurement plane 继续作为“能测什么、来自哪里”的 authority 根。后续只在其上冻结状态语义和消费合同。

### 4.2 不把 capability registry 当 runtime provider registry
`asset_id exists` 不等于 `provider executable + causal + accepted + current`。M5 必须先 source/profile admission；拿不到 exact view/receipt 就 `NOT_ADMITTED`，不能本地补造。

### 4.3 不按周期提前调参
M3 的 10 个 profiles 全部保留 M2 `20 bars + T1=2.0`。M4 只增加研究用 primary `T2=4.0` 与固定 `3/5` sensitivity，不允许 outcome-driven 调整。

### 4.4 不自动聚合时间尺度
不同 timeframe 的状态可以冲突。Layer 2 只返回独立 measurements；如何组合属于 strategy layer。

### 4.5 五桶协议不等于五桶成立
M4 只保证 M5 无法事后改口。`STRONG_UP/STRONG_DOWN` 是否值得获得稳定产品语义，必须等待 M5 证据并由 M6 裁决。

## 5. 下一唯一任务

**M5 — 极端斜率持续性实证。**

M5 必须严格读取 `docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json` 执行：先 source/profile admission，再 development 管线与样本量检查、封存 receipt，然后 primary `T2=4` validation 一次；只有 validation 达到预注册支持规则才允许解锁 holdout。`T2=3/5`、phase sensitivity 和 STAR50 replication 都不能替代 CSI1000 primary。

M5 不得修改 M4 protocol version。M5 完成前不得进入 M6 架构裁决。
