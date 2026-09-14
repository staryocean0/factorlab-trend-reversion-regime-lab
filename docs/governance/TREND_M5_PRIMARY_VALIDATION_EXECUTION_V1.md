# M5-4 Primary Validation Execution Freeze

状态：**FROZEN BEFORE VALIDATION READ**。机器 authority 为 `TREND_M5_PRIMARY_VALIDATION_EXECUTION_V1.json`。

本轮只允许对 `000852.SH` 的已准入 `1m_official / 5m_offset_0` 执行一次 primary `T2=4.0` Validation，日期为 `2023-01-03`–`2024-12-31`。`2022-12-30` 只作为 20-bar 状态与 split 首个 episode 的因果上下文，不进入 Validation 统计。2025 Holdout、STAR50 replication、`T2=3/5` sensitivity 均不得读取。

Primary 为 5-bar directional survival 的 Strong-Moderate 差值，H1 方向为负，实际量级门槛 `<= -0.05`。ISO calendar week 为 cluster，5000 次 bootstrap，seed=`20260914`；每个 contrast/metric 独立重新初始化同一 seed。Primary 单侧 bootstrap p 定义为 `(1 + bootstrap差值>=0 的次数)/(有效重复数+1)`，95% CI 使用 percentile interval。

Holm family 始终保持 M4 的 8 个 planned contrasts：1m/5m/15m/60m × UP/DOWN。15m/60m 因 `NOT_ADMITTED` 固定 raw p=`1.0`，不得缩小 family。

每个可执行 interval/direction 只有在：primary sample floor 通过、Holm adjusted p<=0.05、primary contrast<=-0.05，且至少一个 adequate secondary point estimate 符合 H1 方向，同时没有 adequate secondary 的 95% CI 完全落在反方向时，才记为 `VALIDATION_SUPPORT`。Primary 95% CI 完全大于 0 才记 `H1_CONTRADICTED`；样本不足记 `INCONCLUSIVE_UNDERPOWERED`；其他情况记 `H1_NOT_SUPPORTED`。

同一次运行还输出 M4 预注册 descriptive metrics，但它们不改变上述 support rule。M5-4 完成后只允许进入 M5-5 预注册 `T2=3/5` Validation sensitivity；Holdout 仍锁定。
