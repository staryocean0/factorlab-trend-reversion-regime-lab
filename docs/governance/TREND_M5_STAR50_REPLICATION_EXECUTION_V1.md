# M5-6 STAR50 Cross-Carrier Replication Freeze

状态：**FROZEN BEFORE REPLICATION READ**。机器 authority 为 `TREND_M5_STAR50_REPLICATION_EXECUTION_V1.json`。

本步骤只允许对 STAR50 `000688.SH` 执行一次独立 cross-carrier replication：使用 M4 primary `T2=4.0`、Validation `2023-01-03`–`2024-12-31`、已准入 `1m_official / 5m_offset_0`。`2022-12-30` 仅作因果上下文。

Replication 复用冻结的 5-bar directional survival、10-bar reversal probability、5-bar direction-adjusted return 与 ISO-week 5000 次 bootstrap。它不是新的 primary，不建立新的 multiplicity family，也不与 CSI1000 pooling。报告重点是方向与置信区间是否和已消费的 CSI1000 `H1_CONTRADICTED` headline 具有 qualitative consistency。

每个 contrast：primary survival CI 全部大于 0 标记 `REPLICATION_H1_CONTRADICTED`；全部小于 0 标记 `REPLICATION_H1_DIRECTION`；跨 0 标记 mixed/null；样本不足标记 underpowered。这些标签只用于独立复制报告，不能改写 CSI1000 headline、不能 rescue H1，也不能解锁 Holdout。

15m/60m 与 phase profiles 仍按 M5-1 `NOT_ADMITTED` 报告，不进行 local resampling、offset substitution 或 legacy promotion。2025 Holdout 不进入 checkout。
