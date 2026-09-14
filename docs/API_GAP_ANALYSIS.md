# 趋势状态 Consumer：当前 Gap List（已吸收 M2–M5-1）

> 本文追踪当前仓库距离最终 `regime_state_consumer_v1` 仍有哪些差距。M5-1 已完成 source/profile admission，但没有读取 Validation/Holdout outcome，也没有产生五桶市场证据。

## 1. 当前结论

当前仓库已经具备：

- Layer-2 measurement-plane authority 边界；
- M2 三桶数学与 as-of/fail-closed 基线；
- M3 10 个 versioned profile registry；
- M4 结果前冻结的五桶实验协议；
- M5-1 source/profile admission receipt：两指数的 `1m_official` / `5m_offset_0` 已准入；15m/60m 与 phase-sensitivity profiles 当前 fail closed。

正确演进路径：

```text
M2/M3 frozen measurement/profile
        +
M4 frozen five-bucket protocol
        +
M5-1 exact source/profile admission
        ↓
M5-2 development pipeline + sample adequacy
        ↓
sealed development receipt
        ↓
M5 validation / conditional holdout / replication
        ↓
M6 representation decision → M7 consumer
```

## 2. 已解决项

| ID | 原 Gap | 解决状态 |
|---|---|---|
| G05 | caller/component 参数所有权 | **M3 RESOLVED**：caller 选 interval/profile；低层语义由 versioned profile 持有 |
| G06 | 三桶数学未冻结 | **M2 RESOLVED**：20-bar log-close OLS signed slope t-score，`T1=2.0` |
| G07 | completed-bar/lookback/T1 未冻结 | **M2 RESOLVED** |
| G08 | 多周期 profile 未冻结 | **M3 RESOLVED**：1m×1、5m×5、15m×2、60m×2 |
| G15 | interval cadence gap | **M3 RESOLVED（session grid 层）**：`CADENCE_GAP/OFF_PROFILE_GRID` fail closed |
| G16 | 多周期总趋势歧义 | **M3 RESOLVED**：无 `global_state` |
| G18 | 五桶协议可事后改口 | **M4 RESOLVED**：T2/splits/profiles/endpoints/sample guards/holdout rule 已冻结 |
| G19 | M5 是否会把“文件存在”直接当 source admission | **M5-1 RESOLVED**：建立 `TREND_M5_SOURCE_PROFILE_ADMISSION_V1`，只接受 current active exact-view lineage；legacy 文件不自动升级 |

## 3. 仍未解决的核心 Gap

| ID | Gap | 当前证据 | 目标 | 归属 |
|---|---|---|---|---|
| G01 | 没有正式公开 trend consumer entrypoint | measurement primitives/wrappers | `query_regime/as_of` facade | M7 |
| G02 | `regime_state_consumer_v1` 尚未代码实现 | contract 已冻结 | 稳定 consumer envelope | M7 |
| G03 | 没有正式 snapshot lifecycle/store | measurement clocks 有，consumer lifecycle 无 | immutable snapshot + expiry/no-fallback | M7 |
| G04 | consumer 缺失/过期语义未代码化 | 文档冻结 | runtime unavailable reasons | M7 |
| G09 | 五桶没有正式市场证据 | M4 已冻结协议；M5-1 仅 source admission | development→validation→conditional holdout→M6 | M5–M6 |
| G10 | runtime provider/source admission 不完整 | **PARTIAL**：M5-1 已准入两指数 1m/5m；15m/60m 和 phase sensitivity 无 current active exact receipt | 为未准入 profile 提供 exact current source receipt，或保持 NOT_ADMITTED | M5/M7/M9 |
| G11 | 没有 trend snapshot identity/append-only history | measurement result 不是发布事件 | stable snapshot ID + immutable history | M7 |
| G12 | 没有 consumer conformance/expiry/no-fallback tests | M2/M3/M4/M5-1 有底层/治理 tests | consumer contract suite | M7 |
| G13 | 正式 callable consumer 生命周期未登记 | support/measurement 工程 | owner/version/status/migration | M7/M9 |
| G14 | strategy integration 尚未证明 | 无两个调用者只依赖公开 consumer | 多调用者集成 | M8 |
| G17 | 跨完整交易日缺失 authority 不在 Layer-2 | session grid 可查，整日 source completeness 仍需 receipt | Layer-1 calendar/provider receipt | M5/M7/M9 |
| G20 | historical retrieval `available_at` 与 decision-time visibility 语义可能混用 | **M5-1 已冻结 adapter contract**：raw historical `available_at` 只作 provenance，runtime completed-bar visibility=`bar_end`；但 M5 pipeline 尚未实现/验收 | 在 M5-2 loader/pipeline 中强制该语义并回归测试 | M5-2 |

## 4. M5-1 的关键裁决

### 4.1 当前可用的 exact current source

DataHub `factorlab_unified_index_kline_v3_20260824` 的 active cross-index archive 对 `000852.SH` 与 `000688.SH` 都提供：

- `1m_official`：ADMITTED；
- `5m_offset_0`：ADMITTED；
- 完整覆盖 M4 公共窗口 `2020-07-23`–`2025-12-31`；
- identity lineage 保留 `dataset_version/export_view_id/export_frequency/data_contract`。

### 4.2 当前不能准入的 profile

- `15m_offset_5 / 60m_offset_30` anchors：NOT_ADMITTED；
- 其余 M4 phase-sensitivity profiles：NOT_ADMITTED。

原因不是结果表现，而是 current source Gate：STAR50 exact 15m/60m 只存在于被明确标成非当前 research input 的 legacy `development/`；CSI1000 two-wave exact multi-view shipped rows截止 2020-12-31。M4 禁止通过本地 resampling/substitution 解决。

### 4.3 时钟语义

归档 `available_at` 是 historical retrieval availability，不是盘中 feed latency。M5-1 冻结：

```text
bar_end = exact export-view timestamp
runtime_available_at = bar_end
raw historical available_at = provenance only
```

该规则将在 M5-2 pipeline 中被代码化；不声称测得真实 feed latency。

## 5. 唯一下一任务

**M5-2 — Development pipeline + sample-adequacy checks，仅限 admitted 1m/5m anchors。**

M5-2 可以读取 M4 Development split 并计算 development 样本充足性，但不得读取 Validation outcome；必须封存 code/config/development receipt 后才能进入一次性的 primary Validation。15m/60m 继续 fail closed，除非未来出现符合 M4 的 current active exact-view receipt。

M5 完成前不得进入 M6。
