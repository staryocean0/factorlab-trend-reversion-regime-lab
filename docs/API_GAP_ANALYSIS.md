# 趋势状态 Consumer：当前 Gap List（已吸收 M2–M5-4）

> M5-4 已完成一次性 primary `T2=4` Validation。结果在全部可执行 CSI1000 primary contrasts 上反驳预注册 exhaustion H1；Holdout 未读取且不得因该 H1 support 路径解锁。

## 1. 当前路径

```text
M2/M3 measurement + profiles
        +
M4 preregistered protocol
        +
M5-1 source admission
        +
M5-2 Development adequacy
        +
M5-3 pre-Validation seal
        +
M5-4 primary T2=4 Validation: H1 CONTRADICTED
        ↓
M5-5 predeclared T2=3/5 sensitivity (cannot rescue headline)
        ↓
remaining replication/reporting
        ↓
M6 representation decision → M7 consumer
```

## 2. 已解决项

| ID | Gap | 解决状态 |
|---|---|---|
| G05 | caller/component 参数所有权 | **M3 RESOLVED** |
| G06/G07 | 三桶数学/completed-bar/T1 未冻结 | **M2 RESOLVED** |
| G08 | 多周期 profile 未冻结 | **M3 RESOLVED** |
| G15 | interval cadence gap | **M3 RESOLVED** |
| G16 | 多周期总趋势歧义 | **M3 RESOLVED**：无 `global_state` |
| G18 | 五桶协议可事后改口 | **M4 RESOLVED** |
| G19 | 文件存在被误当 source admission | **M5-1 RESOLVED** |
| G20 | historical retrieval `available_at` 与 decision-time visibility 混用 | **M5-1/M5-2 RESOLVED** |
| G21 | Validation 前 code/config/data identity 未 seal | **M5-3 RESOLVED** |
| G22 | primary `T2=4` Validation 尚未执行/裁决 | **M5-4 RESOLVED**：one-shot Validation 已封存；四个可执行 primary contrasts 全部 `H1_CONTRADICTED`；execution consumed，禁止 rerun |

## 3. M5-4 新证据

机器 authority：`docs/governance/TREND_M5_PRIMARY_VALIDATION_V1.json`。

CSI1000 `2023-01-03`–`2024-12-31`：

| interval | direction | survival Strong-Moderate | 95% CI | reversal10 Strong-Moderate | 裁决 |
|---|---|---:|---|---:|---|
| 1m | UP | +0.3853 | [+0.3734,+0.3969] | -0.2476 | H1_CONTRADICTED |
| 1m | DOWN | +0.3795 | [+0.3681,+0.3908] | -0.2507 | H1_CONTRADICTED |
| 5m | UP | +0.3822 | [+0.3531,+0.4119] | -0.2371 | H1_CONTRADICTED |
| 5m | DOWN | +0.3673 | [+0.3388,+0.3948] | -0.2360 | H1_CONTRADICTED |

M4 H1 预测 extreme state 更易耗竭，因此 primary contrast 应为负、reversal contrast 应为正；实际两个方向都稳定相反。当前可执行证据指向：**extreme slope state 更持久且更少反转**。

这不自动决定正式五桶表示，更不产生交易动作语义。

15m/60m 仍 `NOT_ADMITTED`、raw p=`1.0`，完整 Holm family 仍为 8；没有通过 admission 后缩小 multiple-testing family。

## 4. 仍未解决的核心 Gap

| ID | Gap | 当前证据 | 目标 | 归属 |
|---|---|---|---|---|
| G01 | 无正式公开 trend consumer entrypoint | measurement/research primitives | `query_regime/as_of` facade | M7 |
| G02 | `regime_state_consumer_v1` 未代码实现 | contract 已冻结 | stable envelope | M7 |
| G03 | 无 snapshot lifecycle/store | measurement clocks 有 | immutable snapshot + expiry/no-fallback | M7 |
| G04 | consumer unavailable/expiry 未代码化 | 文档合同 | runtime semantics | M7 |
| G09 | 五桶最终产品证据尚未完成 | primary T2=4 已有强反证；sensitivity/replication 尚未完成 | 完成 M5 后由 M6 裁决 3-bucket/5-bucket/continuous representation | M5–M6 |
| G10 | source admission 不完整 | 1m/5m admitted；15m/60m、phase sensitivity NOT_ADMITTED | exact current receipts 或继续 fail closed | M5/M7/M9 |
| G11 | 无 trend snapshot identity/history | measurement 不是发布事件 | stable snapshot ID | M7 |
| G12 | 无 consumer conformance suite | 当前为底层/研究治理 tests | expiry/no-fallback/compatibility tests | M7 |
| G13 | callable consumer 生命周期未登记 | support/measurement 工程 | owner/version/status/migration | M7/M9 |
| G14 | strategy integration 未证明 | 无两个独立 caller | 多调用者集成 | M8 |
| G17 | 完整交易日 completeness authority 不在 Layer-2 | session grid 可验 | Layer-1 calendar/provider receipt | M5/M7/M9 |
| G23 | 预注册阈值敏感性尚未执行 | T2=4 headline 已反驳 H1 | 执行 T2=3/5 Validation sensitivity，但不得替代 headline 或解锁 Holdout | **M5-5** |

## 5. 当前唯一任务

**M5-5 — 预注册 `T2=3/5` Validation sensitivity。**

它只能回答 T2=4 反证对阈值是否敏感，不能用于 rescue 原 H1。2025 Holdout 继续关闭；STAR50 replication 单独报告；M5 完成前不得进入 M6。
