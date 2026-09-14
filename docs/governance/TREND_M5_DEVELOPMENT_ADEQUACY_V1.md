# M5-2 Development 样本充足性结果

状态：**PASS（仅样本充足性）**。Validation 与 Holdout 仍锁定，H1 尚未检验。

本轮只读取 `2020-07-23`–`2022-12-30`，且只运行 M5-1 已准入的 `trend_1m_official_v1` 与 `trend_5m_offset0_v1`。没有读取 2023–2025，也没有计算 directional survival、reversal、return、transition probability、MFE/MAE 或任何显著性检验。

主 5-bar 完整 episode-entry 数：

| carrier/profile | UP moderate | UP strong | DOWN moderate | DOWN strong |
|---|---:|---:|---:|---:|
| 000852.SH / 1m | 6012 | 3003 | 5912 | 2891 |
| 000852.SH / 5m | 1157 | 549 | 1202 | 587 |
| 000688.SH / 1m | 5805 | 2746 | 6319 | 3084 |
| 000688.SH / 5m | 1105 | 546 | 1267 | 631 |

四组 carrier/profile 的上下行 strong/moderate 均超过 M4 预注册的 validation primary 数量门槛 100；10/20-bar secondary 的 Development 可用量也全部超过门槛 50。因此当前结论只能是：**已准入的 1m/5m 在 Development 上不存在明显样本量阻塞，可以进入下一道封存 Gate。** 这不是 H1 支持证据，也不代表 Validation 一定有足够样本。

真实数据运行：GitHub Actions `34812469153`，head `7069d2afc1c2137c14a16003dcfd5ebf9c21376f`。原始结果 artifact id `10334954106`，digest `sha256:95eb49298359959cd4ebf82fc21eca8d79e61e932f0d550fbb3c09efd56b3147`。

下一步仅允许 **M5-3：封存 code/config/Development identity 与 receipt**。完成该 Gate 前不得读取 Validation。
