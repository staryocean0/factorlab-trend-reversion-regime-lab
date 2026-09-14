# 趋势状态 Consumer：当前 Gap List（已吸收 M2–M5-6）

> **M5 已 COMPLETE。** CSI1000 primary `T2=4`、predeclared `T2=3/5` sensitivity 与 STAR50 independent replication 均一致反驳原 extreme-slope exhaustion H1。M5 outcome 不得重开，2025 Holdout 从未读取。当前唯一下一里程碑是 M6 representation decision。

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
M5-4 CSI1000 primary: H1 CONTRADICTED
        +
M5-5 T2=3/5 sensitivity: 8/8 CONTRADICTED
        +
M5-6 STAR50 replication: CLEAR QUALITATIVE REPLICATION
        ↓
M5 COMPLETE
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
| G22 | primary `T2=4` Validation 未执行/裁决 | **M5-4 RESOLVED**：四个 executable CSI1000 contrasts 全部 `H1_CONTRADICTED` |
| G23 | 预注册阈值敏感性未执行 | **M5-5 RESOLVED**：T2=3/5 共 8/8 executable contrasts 继续反驳 H1 |
| G24 | cross-carrier replication 未执行 | **M5-6 RESOLVED**：STAR50 四个 executable contrasts 全部清楚同方向，`CLEAR_QUALITATIVE_REPLICATION_OF_PRIMARY_CONTRADICTION` |
| G09 | 五桶市场证据未收口 | **M5 RESOLVED / M6 DECISION PENDING**：实证链已经收口，下一步是产品表示裁决而非继续 outcome probing |

## 3. M5 已封存证据

机器 closeout：`docs/governance/TREND_M5_CLOSEOUT_V1.json`。

CSI1000 primary `T2=4` survival Strong-Moderate：`+0.3673` 至 `+0.3853`，所有 95% CI 严格大于 0；reversal10 为 `-0.2360` 至 `-0.2507`，CI 严格小于 0。

CSI1000 `T2=3/5` sensitivity：8/8 executable contrasts 全部 survival CI > 0；0 个朝原 H1 方向。

STAR50 primary-T2 replication：

| interval | direction | survival Strong−Moderate | 95% CI | reversal10 Strong−Moderate |
|---|---|---:|---|---:|
| 1m | UP | +0.3735 | [+0.3621,+0.3850] | -0.2504 |
| 1m | DOWN | +0.3727 | [+0.3608,+0.3845] | -0.2090 |
| 5m | UP | +0.3730 | [+0.3416,+0.4042] | -0.2620 |
| 5m | DOWN | +0.3394 | [+0.3141,+0.3640] | -0.1923 |

综合科学结论：在 admitted 1m/5m exact views 上，extreme absolute slope state 稳定表现为更高的短期 persistence 与更低的 reversal probability；这**反驳**原 exhaustion H1，并支持把 absolute slope extremeness 视为 strength/persistence descriptor 候选。它不自动定义五桶产品语义，也不产生交易动作规则。

## 4. 仍未解决的核心 Gap

| ID | Gap | 当前证据 | 目标 | 归属 |
|---|---|---|---|---|
| G01 | 无正式公开 trend consumer entrypoint | measurement/research primitives | `query_regime/as_of` facade | M7 |
| G02 | `regime_state_consumer_v1` 未代码实现 | contract 已冻结 | stable envelope | M7 |
| G03 | 无 snapshot lifecycle/store | measurement clocks 有 | immutable snapshot + expiry/no-fallback | M7 |
| G04 | consumer unavailable/expiry 未代码化 | 文档合同 | runtime semantics | M7 |
| G10 | source admission 不完整 | 1m/5m admitted；15m/60m 与 phase profiles NOT_ADMITTED | exact current receipts 或继续 fail closed | M7/M9 |
| G11 | 无 trend snapshot identity/history | measurement 不是发布事件 | stable snapshot ID | M7 |
| G12 | 无 consumer conformance suite | 当前为底层/研究治理 tests | expiry/no-fallback/compatibility tests | M7 |
| G13 | callable consumer 生命周期未登记 | support/measurement 工程 | owner/version/status/migration | M7/M9 |
| G14 | strategy integration 未证明 | 无两个独立 caller | 多调用者集成 | M8 |
| G17 | 完整交易日 completeness authority 不在 Layer-2 | session grid 可验 | Layer-1 calendar/provider receipt | M7/M9 |
| G25 | 最终表示尚未裁决 | M5 已证明 exhaustion H1 失败，但 strength/persistence 信息稳健 | 在 3-bucket+continuous / formal 5-bucket / 3-bucket+5 diagnostic 中冻结一种产品表示 | **M6** |

## 5. M5 scope limits

15m/60m anchors 与 phase profiles 均 `NOT_ADMITTED_NOT_EXECUTED`；没有 local resampling、profile substitution、legacy promotion 或 carrier pooling。2025 Holdout 从未打开，primary support rule 失败后继续关闭。M5-4/M5-5/M5-6 one-shot jobs 均 consumed，`m5_outcome_work_reopen_allowed=false`。

5-bar direction-adjusted return 没有 persistence/reversal 那样稳定的方向证据，所以 M5 不支持把 state persistence 直接转换为收益、BUY/SELL 或 position 规则。

## 6. 当前唯一任务

**M6 — Representation Decision。**

只允许基于已经封存的 M5 证据裁决：

1. 三桶 + 连续 strength；
2. 正式五桶；
3. 三桶主状态 + 五桶诊断/研究扩展。

M6 不得重新打开 M5 outcome、调 T2、读取 Holdout 或映射交易动作。M6 完成后才进入 M7 consumer implementation。
