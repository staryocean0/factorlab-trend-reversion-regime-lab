# FactorLab 趋势反转与均值回归研究

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 新产品定位

本仓工程收敛为**可被策略调用的趋势状态识别组件**，不是独立交易策略，也不直接输出买卖、仓位或 Layer 4 指令。

M0–M4 已完成；**M5 正在进行中，M5-1 source/profile admission、M5-2 Development sample adequacy、M5-3 Code/Config/Development Seal 均已完成。** 当前 exact current source 只准入两指数的 `1m_official` 与 `5m_offset_0`；15m/60m anchors 继续 `NOT_ADMITTED`。

M5-2 只读取 `2020-07-23`–`2022-12-30` Development，并确认 admitted 1m/5m 的 Development episode 数量不构成明显样本阻塞。M5-3 随后把 M4/M5 contracts、M5 计算代码、M2/M3 依赖、Layer-1 clock、market-data reader、data manifest、DataHub source SHA256 与 Development run/artifact identity 全部封存。任何 sealed path 发生变化都会使默认 CI 失败。

到目前为止仍**没有读取 Validation/Holdout outcome**，也没有产生 directional survival、reversal、return、bootstrap/p-value 或 H1 结论。

## 当前唯一下一步

**M5-4 — primary `T2=4.0` Validation 一次。** 只执行已 admitted 的 1m/5m anchors；15m/60m 保持 `NOT_ADMITTED`。M4 的 planned primary family 仍固定为 8 contrasts，未准入的 4 个 contrasts 按预注册规则 `p=1.0`，Holm family 不得事后缩小。Holdout 继续锁定。

## 入口

[当前状态与下一步边界](CONTINUE_HERE.md) · [执行路线图](docs/ROADMAP.md) · [M4 冻结协议](docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.md) · [M5-1 source admission](docs/governance/TREND_M5_SOURCE_PROFILE_ADMISSION_V1.md) · [M5-2 Development adequacy](docs/governance/TREND_M5_DEVELOPMENT_ADEQUACY_V1.md) · [M5-3 Development seal](docs/governance/TREND_M5_DEVELOPMENT_SEAL_V1.md) · [M5-3 machine seal](docs/governance/TREND_M5_DEVELOPMENT_SEAL_V1.json) · [当前组件白皮书](docs/WHITEPAPER.md) · [Gap 审计](docs/API_GAP_ANALYSIS.md)

当前没有已确认交易策略。M5 必须继续遵循冻结协议和 seal；工程/准入/样本量/seal 通过不自动改变 `production_authority=false`、`fresh_oos=false` 或既有 scientific status。

## 本地环境

```bash
bash .codex/cloud_setup.sh
```

默认只安装依赖并检查组件一致性，不自动回放历史拟合。
