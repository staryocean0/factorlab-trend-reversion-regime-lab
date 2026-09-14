# FactorLab 趋势反转与均值回归研究

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 新产品定位

未来工程收敛为**可被策略调用的趋势状态识别组件**，不是独立交易策略，也不直接输出买卖、仓位或 Layer 4 指令。

M0–M4 已完成；**M5 正在进行中，M5-1 source/profile admission 与 M5-2 Development sample adequacy 均已完成。** 当前 exact current source 只准入两指数的 `1m_official` 与 `5m_offset_0`；15m/60m anchors 继续 `NOT_ADMITTED`。

M5-2 只读取 `2020-07-23`–`2022-12-30` Development。四个 admitted carrier/profile 组合的上涨/下跌 strong/moderate 完整 5-bar episode-entry 数全部高于 M4 预注册门槛 100，10/20-bar secondary 可用量也全部高于 50。因此目前只能确认：**Development 样本量没有阻塞 1m/5m 后续正式检验。** 这不是 H1 支持证据。

本轮仍未读取 Validation/Holdout，也未计算 directional survival、reversal、forward return、transition probability、MFE/MAE 或显著性检验。

## 当前唯一下一步

**M5-3 — 封存 code/config/Development identity 与 receipt。** 完成封存 Gate 前不得读取 Validation。M5-3 也不运行 primary `T2=4` Validation。

## 入口

[当前状态与下一步边界](CONTINUE_HERE.md) · [执行路线图](docs/ROADMAP.md) · [M4 冻结协议](docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.md) · [M5-1 source admission](docs/governance/TREND_M5_SOURCE_PROFILE_ADMISSION_V1.md) · [M5-2 Development adequacy](docs/governance/TREND_M5_DEVELOPMENT_ADEQUACY_V1.md) · [M5-2 machine receipt](docs/governance/TREND_M5_DEVELOPMENT_ADEQUACY_V1.json) · [当前组件白皮书](docs/WHITEPAPER.md) · [Gap 审计](docs/API_GAP_ANALYSIS.md)

当前没有已确认交易策略。M5 必须继续遵循冻结协议，不能根据后续结果修改 primary T2、split、profile、horizon 或样本门槛。工程/准入/样本量通过不自动改变 `production_authority=false`、`fresh_oos=false` 或既有 scientific status。

## 本地环境

```bash
bash .codex/cloud_setup.sh
```

默认只安装依赖并检查组件一致性，不自动回放历史拟合。
