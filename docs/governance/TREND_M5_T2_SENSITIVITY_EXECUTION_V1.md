# M5-5 T2 Sensitivity Execution

状态：**CONSUMED AFTER ONE T2 SENSITIVITY RUN**。机器 execution authority 为 `TREND_M5_T2_SENSITIVITY_EXECUTION_V1.json`，机器结果 authority 为 `TREND_M5_T2_SENSITIVITY_V1.json`。

本步骤只执行了 M4 已预注册的 `T2=3.0` 与 `T2=5.0` Validation sensitivity。数据限定为 CSI1000 `000852.SH`、`2023-01-03`–`2024-12-31`，只使用已准入的 `1m_official` 与 `5m_offset_0`；`2022-12-30` 仅作为因果上下文。2025 Holdout 与 STAR50 replication 均未读取。

真实运行：Actions `34816576915`；head `9e622c653a5510e73444a00f76881050946ffd1a`；artifact `10336711547`；digest `sha256:4c654375daa971c9aa028dc29fea1f1facab889cb29104a1b740f7e34efc575c`。

Sensitivity 复用 frozen 5-bar directional survival、10-bar reversal probability、5-bar direction-adjusted return 与 ISO-week 5000 次 bootstrap。它没有建立新的 primary family，没有重跑 M5-4，也没有改变 headline `H1_CONTRADICTED_ON_ALL_EXECUTABLE_PRIMARY_CONTRASTS`。

结果：

- `T2=3`：4/4 可执行 contrasts 均为 `SENSITIVITY_H1_CONTRADICTED`；survival Strong-Moderate `+0.4045` 至 `+0.4147`，95% CI 全部严格大于 0；reversal10 Strong-Moderate `-0.2512` 至 `-0.2854`。
- `T2=5`：4/4 可执行 contrasts 均为 `SENSITIVITY_H1_CONTRADICTED`；survival Strong-Moderate `+0.3382` 至 `+0.3572`，95% CI 全部严格大于 0；reversal10 Strong-Moderate `-0.1996` 至 `-0.2247`。

因此 **8/8 sensitivity contrasts 继续反驳 exhaustion H1，0/8 朝 H1 方向**。这只说明 T2=4 的反证对预注册阈值 `3/5` 稳健；它不能替代或重新定义 primary headline，也不能产生交易动作语义。

`holdout_unlock_allowed=false` 且 primary support rule 已失败，所以 2025 Holdout 继续关闭。One-shot sensitivity execution 已 consumed，`sensitivity_rerun_allowed=false`，CI job 已禁用第二次运行。

唯一下一步：**M5-6 cross-carrier replication / remaining robustness reporting**。只允许对 STAR50 `000688.SH` 使用 admitted 1m/5m exact views 做独立 replication；不能池化、不能 rescue CSI1000 headline、不能补造未准入 phase profiles，也不能打开 Holdout。
