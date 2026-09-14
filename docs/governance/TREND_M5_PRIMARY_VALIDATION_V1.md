# M5-4 Primary T2=4 Validation Result

状态：**PASS — EXECUTED ONCE; H1 CONTRADICTED**。机器 authority 为 `TREND_M5_PRIMARY_VALIDATION_V1.json`。

本次只读取中证1000 `000852.SH` 的冻结 Validation `2023-01-03`–`2024-12-31`，只执行已准入的 1m official 与 5m offset0。2025 Holdout、STAR50 replication、`T2=3/5` sensitivity 均未读取/运行。

## Primary 结果

| interval | direction | moderate survival5 | strong survival5 | Strong-Moderate | 95% CI | 裁决 |
|---|---|---:|---:|---:|---|---|
| 1m | UP | 0.5014 | 0.8867 | +0.3853 | [+0.3734,+0.3969] | H1_CONTRADICTED |
| 1m | DOWN | 0.5137 | 0.8932 | +0.3795 | [+0.3681,+0.3908] | H1_CONTRADICTED |
| 5m | UP | 0.5079 | 0.8901 | +0.3822 | [+0.3531,+0.4119] | H1_CONTRADICTED |
| 5m | DOWN | 0.5082 | 0.8755 | +0.3673 | [+0.3388,+0.3948] | H1_CONTRADICTED |

M4 的 H1 预期 Strong-Moderate **为负**（极端斜率更易耗竭）。实证却在所有可执行 interval/direction 上得到约 **+37–39 个百分点**，且 95% CI 全部严格大于 0。因此不是“未显著”，而是稳定、方向一致地反驳 H1。

10-bar reversal secondary 也给出同方向反证：Strong-Moderate 分别约 `-0.248 / -0.251 / -0.237 / -0.236`，各 95% CI 全部严格低于 0。换言之，在该冻结定义下，极端斜率状态不是更容易反转，而是明显更少反转。

5-bar direction-adjusted return 的差异很小且 CI 均跨 0，不改变 primary 裁决。

15m/60m 仍然 `NOT_ADMITTED`，按 M4 冻结规则 raw p=`1.0` 并保留在 8 项 Holm family 中；family 没有缩水。

## 含义与边界

这个结果只说明：**预注册的“极端斜率耗竭”假设 H1 被当前可执行 CSI1000 Validation 证据反驳；极端状态表现为更高的短期趋势持续性。** 它不自动证明五桶应进入最终产品语义，更不等于任何 BUY/SELL、仓位或订单规则。

Holdout 因 primary Validation 没有满足预注册 support rule 而继续锁定，不能为了寻找支持而打开。M5-5 仍可按协议运行预注册 `T2=3/5` Validation sensitivity，但只能作为敏感性说明，**不能替代或 rescue T2=4 headline 结论**。

真实运行：Actions `34814912150`，head `4aecd9b88a171eb51a63462bfe10eaa8168f34dc`，artifact `10335368583`，digest `sha256:acf170aab180478c73fb2dcc09ec5610c06e7276e566ee2fc7a134082e2dc045`。
