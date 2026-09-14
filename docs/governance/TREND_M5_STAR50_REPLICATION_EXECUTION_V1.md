# M5-6 STAR50 Cross-Carrier Replication — Consumed

状态：**CONSUMED AFTER ONE STAR50 REPLICATION**。机器 authority 为 `TREND_M5_STAR50_REPLICATION_EXECUTION_V1.json`，结果 authority 为 `TREND_M5_STAR50_REPLICATION_V1.json`。

M5-6 已按冻结边界执行一次：STAR50 `000688.SH`、primary `T2=4.0`、Validation `2023-01-03`–`2024-12-31`，仅使用 M5-1 已准入的 `1m_official / 5m_offset_0`。`2022-12-30` 仅作为因果上下文；2025 Holdout 未进入运行环境。

四个可执行 replication contrasts 全部为 `REPLICATION_H1_CONTRADICTED`：5-bar directional-survival Strong-Moderate 分别约 `+0.3735 / +0.3727 / +0.3730 / +0.3394`，95% CI 均严格大于 0；10-bar reversal Strong-Moderate 分别约 `-0.2504 / -0.2090 / -0.2620 / -0.1923`，95% CI 均严格小于 0。

因此 replication 结论冻结为：**`CLEAR_QUALITATIVE_REPLICATION_OF_PRIMARY_CONTRADICTION`**。STAR50 与 CSI1000 未池化，也未建立新的 primary multiplicity family；复制结果不能改写或 rescue CSI1000 `T2=4` headline。

15m/60m anchors 与 phase profiles 仍为 `NOT_ADMITTED_NOT_EXECUTED`；没有 local resampling、offset substitution 或 legacy promotion。Primary、T2 sensitivity、STAR50 replication 三个 one-shot outcome job 均已 consumed，禁止 rerun。2025 Holdout 从未打开，且继续被 primary support rule 阻断。

M5 已收口。唯一后续里程碑是 **M6 representation decision**；本文件不授权重新打开 M5 outcome，也不产生 BUY/SELL、仓位、订单或其他交易动作语义。
