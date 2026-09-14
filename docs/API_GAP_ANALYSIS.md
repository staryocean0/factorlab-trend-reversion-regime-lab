# 趋势状态 Consumer：当前 Gap List（已吸收 M2–M5-2）

> 本文追踪当前仓库距离最终 `regime_state_consumer_v1` 仍有哪些差距。M5-2 已完成 Development sample adequacy，但 Validation/Holdout 仍未读取，五桶 H1 尚未检验。

## 1. 当前结论

当前已经具备：M2 三桶数学、M3 versioned profiles、M4 预注册五桶协议、M5-1 exact source/profile admission，以及 M5-2 Development-only sample adequacy。

当前路径：

```text
M5-1 exact source admission
        +
M5-2 Development sample adequacy
        ↓
M5-3 code/config/Development seal
        ↓
M5 primary Validation / conditional holdout
        ↓
M6 representation decision → M7 consumer
```

## 2. 已解决项

| ID | Gap | 解决状态 |
|---|---|---|
| G05 | caller/component 参数所有权 | **M3 RESOLVED** |
| G06 | 三桶数学未冻结 | **M2 RESOLVED** |
| G07 | completed-bar/lookback/T1 未冻结 | **M2 RESOLVED** |
| G08 | 多周期 profile 未冻结 | **M3 RESOLVED** |
| G15 | interval cadence gap | **M3 RESOLVED** |
| G16 | 多周期总趋势歧义 | **M3 RESOLVED**：无 `global_state` |
| G18 | 五桶协议可事后改口 | **M4 RESOLVED** |
| G19 | “文件存在”被误当 source admission | **M5-1 RESOLVED**：current active exact-view receipt 才能准入 |
| G20 | historical retrieval `available_at` 与 decision-time visibility 混用 | **M5-1/M5-2 RESOLVED**：raw historical `available_at` 仅 provenance；Development pipeline 使用 completed exact-view bars，并未把历史 retrieval time 当盘中延迟 |

## 3. 仍未解决的核心 Gap

| ID | Gap | 当前证据 | 目标 | 归属 |
|---|---|---|---|---|
| G01 | 无正式公开 trend consumer entrypoint | measurement primitives | `query_regime/as_of` facade | M7 |
| G02 | `regime_state_consumer_v1` 未代码实现 | contract 已冻结 | stable envelope | M7 |
| G03 | 无 snapshot lifecycle/store | measurement clocks 有 | immutable snapshot + expiry/no-fallback | M7 |
| G04 | consumer unavailable/expiry 未代码化 | 文档合同 | runtime semantics | M7 |
| G09 | 五桶没有正式市场证据 | M5-2 只证明 Development 样本量足够 | Validation→conditional holdout→M6 | M5–M6 |
| G10 | source admission 不完整 | 1m/5m admitted；15m/60m、phase sensitivity NOT_ADMITTED | exact current receipts 或继续 fail closed | M5/M7/M9 |
| G11 | 无 trend snapshot identity/history | measurement 不是发布事件 | stable snapshot ID | M7 |
| G12 | 无 consumer conformance suite | 当前仅底层/研究治理 tests | expiry/no-fallback/compatibility tests | M7 |
| G13 | callable consumer 生命周期未登记 | support/measurement 工程 | owner/version/status/migration | M7/M9 |
| G14 | strategy integration 未证明 | 无两个独立 caller | 多调用者集成 | M8 |
| G17 | 完整交易日 source completeness authority 不在 Layer-2 | session grid 可验 | Layer-1 calendar/provider receipt | M5/M7/M9 |
| G21 | Validation 前 code/config/Development identity 尚未正式 seal | M5-2 run 与 artifact 已有 identity，但还未形成不可覆盖 seal contract | 冻结 code blob/config/source/run/dataset identities，并保持 Validation locked | **M5-3** |

## 4. M5-2 Development Sample Adequacy

只读取 `2020-07-23`–`2022-12-30`，只运行 M5-1 admitted 的 1m/5m anchors。

主 5-bar 完整 episode-entry 数：

| carrier/profile | UP moderate | UP strong | DOWN moderate | DOWN strong |
|---|---:|---:|---:|---:|
| 000852.SH / 1m | 6012 | 3003 | 5912 | 2891 |
| 000852.SH / 5m | 1157 | 549 | 1202 | 587 |
| 000688.SH / 1m | 5805 | 2746 | 6319 | 3084 |
| 000688.SH / 5m | 1105 | 546 | 1267 | 631 |

四个组合的 primary floor=100 与 10/20-bar secondary floor=50 均通过。该结果只回答“样本够不够”，没有计算 H1 primary/secondary outcomes。

证据：`docs/governance/TREND_M5_DEVELOPMENT_ADEQUACY_V1.json`；真实 run `34812469153`。

## 5. 唯一下一任务

**M5-3 — Code / Config / Development Seal。**

只允许冻结 M5 pipeline code hash、M4 config identity、M5-1 admission identity、M5-2 run/artifact/dataset identity，以及仍为 locked 的 Validation/Holdout 状态。**M5-3 不运行 Validation。**

M5 完成前不得进入 M6。
