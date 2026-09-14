# 趋势状态 Consumer：当前 Gap List（已吸收 M2–M5-3）

> 本文追踪当前仓库距离最终 `regime_state_consumer_v1` 仍有哪些差距。M5-3 已在任何 Validation outcome 前完成 code/config/Development seal；Validation/Holdout 仍未读取，五桶 H1 尚未检验。

## 1. 当前结论

当前已经具备：M2 三桶数学、M3 versioned profiles、M4 预注册五桶协议、M5-1 exact source/profile admission、M5-2 Development-only sample adequacy，以及 **M5-3 byte-identity seal**。

当前路径：

```text
M5-1 exact source admission
        +
M5-2 Development sample adequacy
        +
M5-3 code/config/Development seal
        ↓
M5-4 one-shot primary T2=4 Validation
        ↓
M5-5 predeclared sensitivity / conditional holdout
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
| G20 | historical retrieval `available_at` 与 decision-time visibility 混用 | **M5-1/M5-2 RESOLVED**：raw historical `available_at` 仅 provenance；replay clock 使用 completed exact-view bar end |
| G21 | Validation 前 code/config/Development identity 未 seal | **M5-3 RESOLVED**：`TREND_M5_DEVELOPMENT_SEAL_V1.json` 固定 contracts、code blobs、data manifest、DataHub source SHA256、Development run/artifact；CI 用 `git hash-object` 守卫 |

## 3. 仍未解决的核心 Gap

| ID | Gap | 当前证据 | 目标 | 归属 |
|---|---|---|---|---|
| G01 | 无正式公开 trend consumer entrypoint | measurement primitives | `query_regime/as_of` facade | M7 |
| G02 | `regime_state_consumer_v1` 未代码实现 | contract 已冻结 | stable envelope | M7 |
| G03 | 无 snapshot lifecycle/store | measurement clocks 有 | immutable snapshot + expiry/no-fallback | M7 |
| G04 | consumer unavailable/expiry 未代码化 | 文档合同 | runtime semantics | M7 |
| G09 | 五桶没有正式市场证据 | M5-1/2/3 只完成准入、样本量与 seal | primary Validation→conditional holdout→M6 | M5–M6 |
| G10 | source admission 不完整 | 1m/5m admitted；15m/60m、phase sensitivity NOT_ADMITTED | exact current receipts 或继续 fail closed | M5/M7/M9 |
| G11 | 无 trend snapshot identity/history | measurement 不是发布事件 | stable snapshot ID | M7 |
| G12 | 无 consumer conformance suite | 当前仅底层/研究治理 tests | expiry/no-fallback/compatibility tests | M7 |
| G13 | callable consumer 生命周期未登记 | support/measurement 工程 | owner/version/status/migration | M7/M9 |
| G14 | strategy integration 未证明 | 无两个独立 caller | 多调用者集成 | M8 |
| G17 | 完整交易日 source completeness authority 不在 Layer-2 | session grid 可验 | Layer-1 calendar/provider receipt | M5/M7/M9 |
| G22 | primary `T2=4` Validation 尚未执行/裁决 | M5-3 seal 已具备，Validation rows 未读 | sealed identities 下 one-shot Validation，固定 8-contrast Holm family，形成不可覆盖 receipt | **M5-4** |

## 4. M5-3 Seal 的关键约束

机器 authority：`docs/governance/TREND_M5_DEVELOPMENT_SEAL_V1.json`。

Seal 固定了：

- M4 protocol；
- M5-1 source/profile admission；
- M5-2 Development receipt；
- M5-2 entrypoint/core；
- M2 slope baseline；
- M3 profile registry；
- Layer-1 clock contract；
- market-data reader；
- `data/manifest.json`；
- DataHub export/view SHA256；
- Development run/head/artifact digest。

默认 CI 对 sealed paths 重新计算 Git blob identity；byte drift 会直接失败。

M5-3 没有读取 Validation/Holdout，也没有计算 H1 outcome。

## 5. Primary family 不因 admission 缩小

M4 预注册 primary family 固定为 `4 intervals × 2 directions = 8`。M5-1 只使 1m/5m 可执行；15m/60m 对应的 4 个 planned contrasts 仍保留在 family 中，并按 M4 `unavailable_or_underpowered_primary_hypothesis_pvalue=1.0` 进入 Holm。不得在看到 source admission 后把 family 缩成 4。

## 6. 唯一下一任务

**M5-4 — one-shot primary `T2=4.0` Validation。**

只允许读取 `2023-01-03`–`2024-12-31`，使用 seal 中的 code/config/source identities，执行 admitted 1m/5m anchors；15m/60m 继续 NOT_ADMITTED；Holm family size=8；Holdout 保持 locked。M5-4 不得同轮运行 `T2=3/5` sensitivity 或打开 holdout。

M5 完成前不得进入 M6。
