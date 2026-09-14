# 趋势状态 Consumer：当前 Gap List（已吸收 M2–M5-5）

> M5-4 primary `T2=4` Validation 在全部可执行 CSI1000 primary contrasts 上反驳预注册 exhaustion H1；M5-5 的预注册 `T2=3/5` sensitivity 又在 8/8 可执行 sensitivity contrasts 上得到同方向反证。Holdout 未读取且继续关闭。

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
        +
M5-5 T2=3/5 sensitivity: 8/8 CONTRADICTED
        ↓
M5-6 cross-carrier replication / remaining robustness
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
| G22 | primary `T2=4` Validation 尚未执行/裁决 | **M5-4 RESOLVED**：四个可执行 primary contrasts 全部 `H1_CONTRADICTED`；execution consumed，禁止 rerun |
| G23 | 预注册阈值敏感性尚未执行 | **M5-5 RESOLVED**：T2=3/5 共 8 个可执行 sensitivity contrasts 全部 `SENSITIVITY_H1_CONTRADICTED`；0 个朝 H1 方向；one-shot execution consumed |

## 3. 当前市场证据

M5-4 机器 authority：`docs/governance/TREND_M5_PRIMARY_VALIDATION_V1.json`。

CSI1000 primary `T2=4` 的 survival Strong-Moderate 为 `+0.3673` 至 `+0.3853`，95% CI 全部大于 0；10-bar reversal contrast 为 `-0.2360` 至 `-0.2507`，CI 全部小于 0。因此正式 headline 为 **`H1_CONTRADICTED_ON_ALL_EXECUTABLE_PRIMARY_CONTRASTS`**。

M5-5 机器 authority：`docs/governance/TREND_M5_T2_SENSITIVITY_V1.json`。

- `T2=3`：四个 survival contrasts `+0.4045 / +0.4110 / +0.4095 / +0.4147`，CI 全部严格大于 0；
- `T2=5`：四个 contrasts `+0.3572 / +0.3459 / +0.3477 / +0.3382`，CI 全部严格大于 0；
- 两个 threshold 下 10-bar reversal Strong-Moderate 也全部为负约 `-0.200` 至 `-0.285`。

所以当前 evidence 指向：**extreme slope state 的更高短期持续性/更低反转率对 T2=3/4/5 都稳健**。这仍不是交易动作结论，也不自动决定正式五桶产品语义。

15m/60m 与 phase-offset profiles 仍 `NOT_ADMITTED`；没有通过 source admission 后缩小 primary family，也没有本地 resample 补造数据。

## 4. 仍未解决的核心 Gap

| ID | Gap | 当前证据 | 目标 | 归属 |
|---|---|---|---|---|
| G01 | 无正式公开 trend consumer entrypoint | measurement/research primitives | `query_regime/as_of` facade | M7 |
| G02 | `regime_state_consumer_v1` 未代码实现 | contract 已冻结 | stable envelope | M7 |
| G03 | 无 snapshot lifecycle/store | measurement clocks 有 | immutable snapshot + expiry/no-fallback | M7 |
| G04 | consumer unavailable/expiry 未代码化 | 文档合同 | runtime semantics | M7 |
| G09 | 五桶最终产品证据尚未收口 | CSI1000 primary + T2 sensitivity 均强烈反驳 exhaustion H1；replication 尚未完成 | 完成 M5 后由 M6 裁决 3-bucket/5-bucket/continuous representation | M5–M6 |
| G10 | source admission 不完整 | 1m/5m admitted；15m/60m、phase sensitivity NOT_ADMITTED | exact current receipts 或继续 fail closed | M5/M7/M9 |
| G11 | 无 trend snapshot identity/history | measurement 不是发布事件 | stable snapshot ID | M7 |
| G12 | 无 consumer conformance suite | 当前为底层/研究治理 tests | expiry/no-fallback/compatibility tests | M7 |
| G13 | callable consumer 生命周期未登记 | support/measurement 工程 | owner/version/status/migration | M7/M9 |
| G14 | strategy integration 未证明 | 无两个独立 caller | 多调用者集成 | M8 |
| G17 | 完整交易日 completeness authority 不在 Layer-2 | session grid 可验 | Layer-1 calendar/provider receipt | M5/M7/M9 |
| G24 | cross-carrier replication 尚未执行 | CSI1000 已完成 primary+sensitivity；STAR50 1m/5m 已 admitted | 独立运行/报告 STAR50 replication，不池化、不 rescue headline；phase profiles继续 fail closed | **M5-6** |

## 5. 当前唯一任务

**M5-6 — cross-carrier replication / remaining robustness reporting。**

只允许对 STAR50 `000688.SH` 的 admitted 1m official / 5m offset0 做独立 replication；不能与 CSI1000 pooling，不能改写 `T2=4` headline，不能用 replication rescue 原 exhaustion H1，不能读取 2025 Holdout。Phase-sensitivity profiles 没有 current active exact-view receipt 时继续 `NOT_ADMITTED`。

M5 完成前不得进入 M6。
