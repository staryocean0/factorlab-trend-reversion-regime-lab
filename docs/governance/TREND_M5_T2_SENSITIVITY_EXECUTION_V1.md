# M5-5 T2 Sensitivity Execution Freeze

状态：**FROZEN BEFORE SENSITIVITY READ**。机器 authority 为 `TREND_M5_T2_SENSITIVITY_EXECUTION_V1.json`。

本步骤只执行 M4 已预注册的 `T2=3.0` 与 `T2=5.0` Validation sensitivity。数据仍限定为 CSI1000 `000852.SH`、`2023-01-03`–`2024-12-31`，只使用已准入的 `1m_official` 与 `5m_offset_0`；`2022-12-30` 仅作为因果上下文。

Sensitivity 复用 frozen 5-bar directional survival、10-bar reversal probability、5-bar direction-adjusted return 与 ISO-week 5000 次 bootstrap。它不建立新的 primary family，不替换 `T2=4`，不重跑 M5-4，也不能改变已经冻结的 headline `H1_CONTRADICTED_ON_ALL_EXECUTABLE_PRIMARY_CONTRASTS`。

每个 sensitivity contrast 只按 primary survival 95% CI 方向标记：CI 全部大于 0 为 `SENSITIVITY_H1_CONTRADICTED`；CI 全部小于 0 为 `SENSITIVITY_H1_DIRECTION`；跨 0 为 `SENSITIVITY_MIXED_OR_NULL`；样本不足为 `SENSITIVITY_INCONCLUSIVE_UNDERPOWERED`。这些标签只描述阈值稳健性，不是新的正式支持裁决。

2025 Holdout 不在 checkout 中，`holdout_unlock_allowed=false`；STAR50 replication 也不在本步骤运行。

Execution trigger: one-shot sensitivity run under the frozen machine contract.
