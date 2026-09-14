# 从这里接管

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 当前产品口径

本仓是**供策略调用的趋势状态识别组件**，不是独立交易策略，不直接输出买卖、仓位、订单或 Layer 4 指令。

当前里程碑：M0–M4 PASS；M5 **IN PROGRESS**。M5-1 source/profile admission、M5-2 Development sample adequacy、**M5-3 Code/Config/Development Seal 均已 PASS**。H1 尚未进入 Validation。

接管必读：[路线图](docs/ROADMAP.md)、[M4 协议](docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json)、[M5-1 admission](docs/governance/TREND_M5_SOURCE_PROFILE_ADMISSION_V1.json)、[M5-2 Development receipt](docs/governance/TREND_M5_DEVELOPMENT_ADEQUACY_V1.json)、[M5-3 seal](docs/governance/TREND_M5_DEVELOPMENT_SEAL_V1.json)。

## 已完成：M5-1 Source / Profile Admission

| carrier | 1m official | 5m offset0 | 15m offset5 | 60m offset30 |
|---|---|---|---|---|
| `000852.SH` | ADMITTED | ADMITTED | NOT_ADMITTED | NOT_ADMITTED |
| `000688.SH` | ADMITTED | ADMITTED | NOT_ADMITTED | NOT_ADMITTED |

15m/60m 继续 fail closed；禁止本地 resample、换 offset 或 legacy 近似替代。

## 已完成：M5-2 Development Sample Adequacy

只读取 `2020-07-23`–`2022-12-30`。四个 admitted carrier/profile 的 strong/moderate 5-bar episode-entry 数均明显超过 100，10/20-bar secondary 可用量均超过 50。该 Gate 只说明 Development 样本量无明显阻塞，不说明 H1 成立。

真实运行：Actions `34812469153`；head `7069d2afc1c2137c14a16003dcfd5ebf9c21376f`；artifact digest `sha256:95eb49298359959cd4ebf82fc21eca8d79e61e932f0d550fbb3c09efd56b3147`。

## 已完成：M5-3 Code / Config / Development Seal

机器 authority：`docs/governance/TREND_M5_DEVELOPMENT_SEAL_V1.json`。

Seal 已固定：

- M5-2 entrypoint/core；
- M2 slope baseline；
- M3 profile registry；
- Layer-1 clock contract；
- market-data reader；
- M4 protocol、M5-1 admission、M5-2 Development receipt；
- `data/manifest.json`；
- DataHub export/view SHA256；
- Development run/head/artifact digest；
- `runtime_available_at=bar_end` replay clock contract。

`tests/test_m5_development_seal.py` 用 Git blob identity 守护这些文件；修改 sealed code/config 会使默认 CI 失败。

M5-3 没有读取 Validation/Holdout，没有计算 survival、reversal、returns、bootstrap/p-value，也没有 adjudicate H1。

## 唯一下一步：M5-4 Primary T2=4 Validation

下一次会话只允许：

1. 使用 sealed code/config/source identities；
2. 读取 Validation `2023-01-03`–`2024-12-31`；
3. primary `T2=4.0` 只运行一次；
4. 只执行已 admitted 的 1m/5m anchors；15m/60m 继续 `NOT_ADMITTED`；
5. M4 planned primary family **仍为 8 contrasts**。15m/60m 对应的 4 个不可执行 contrasts 按预注册规则 `p=1.0`，Holm family size 不得缩小；
6. Holdout 继续锁定；
7. 本轮不得运行 `T2=3/5` sensitivity，那属于后续 M5-5。

M5-4 结束后必须先封存 Validation artifact/receipt 并按 M4 rule 裁决是否支持 H1；不得同轮自动打开 Holdout。

M5 完成前不得进入 M6。
