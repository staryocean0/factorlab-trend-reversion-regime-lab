# 从这里接管

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 当前产品口径

本仓工程定位：**供策略调用的趋势状态识别组件**，不是独立交易策略，不直接输出买卖、仓位、订单或 Layer 4 指令。

当前里程碑状态：M0–M4 PASS；M5 **IN PROGRESS**。M5-1 source/profile admission 已完成，五桶 H1 仍没有 Validation 实证结论。

接管顺序：先读 [路线图](docs/ROADMAP.md)、[M4 冻结协议](docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.md)、[M5-1 admission receipt](docs/governance/TREND_M5_SOURCE_PROFILE_ADMISSION_V1.md) 与 [机器 receipt](docs/governance/TREND_M5_SOURCE_PROFILE_ADMISSION_V1.json)。

## 已完成：M5-1 Source / Profile Admission

本轮没有计算任何五桶市场 outcome。8 个 M4 anchor carrier/profile pairs 已全部裁决：

| carrier | 1m official | 5m offset0 | 15m offset5 | 60m offset30 |
|---|---|---|---|---|
| `000852.SH` | ADMITTED | ADMITTED | NOT_ADMITTED | NOT_ADMITTED |
| `000688.SH` | ADMITTED | ADMITTED | NOT_ADMITTED | NOT_ADMITTED |

### 为什么 1m / 5m 可以准入

当前 active cross-index archive 来自 DataHub `factorlab_unified_index_kline_v3_20260824`：

- exact `1m_official` source identity；
- exact `5m_offset_0` source identity；
- 两指数完整覆盖 M4 公共历史窗口 `2020-07-23`–`2025-12-31`；
- source manifest 保留 `dataset_version / export_view_id / export_frequency / data_contract` 等 identity 字段；
- 趋势仓 `data/market/1m`、`data/market/5m` 的逐年 hash/source path 已记录在 `data/manifest.json`。

### 为什么 15m / 60m 不准入

不是因为结果不好，而是 source Gate 没过：

- STAR50 的 exact 15m/60m legacy files 虽仍保留，但 source repo 明确声明 legacy `development/` **不是当前 active research input**；
- CSI1000 two-wave exact multi-view shipped rows只到 `2020-12-31`，无法覆盖 M4 的 Development/Validation/Holdout 冻结窗口；
- M4 禁止本地 resample、换 offset 或近似替代。

因此 15m/60m 必须 fail closed。当前 6 个 phase-sensitivity profiles 也全部保持 `NOT_ADMITTED`。

## 冻结的历史时钟适配

历史归档里的 raw `available_at` 是历史数据 retrieval availability，不是盘中 feed latency。依据已经冻结的数据所有者澄清，M5 causal replay 使用：

```text
bar_end = exact export-view timestamp（Shanghai wall-clock contract）
runtime_available_at = bar_end
raw historical available_at = provenance only
```

该规则不声称测得真实延迟；它只避免把历史入库时间错误当成盘中不可见时间。

## M5-1 Gate

**PASS：admission audit complete, partial profile admission。**

- `1m/5m`：两指数 source/profile ADMITTED；
- `15m/60m`：两指数 NOT_ADMITTED；
- no local resampling / no profile substitution；
- `outcomes_computed=false`；
- Validation outcome 未读取；
- Holdout outcome 未读取；
- `production_authority=false`、`fresh_oos=false` 不变。

## 唯一下一步：M5-2 Development Pipeline + Sample Adequacy

下一次会话只允许：

1. 对 admitted 的 `1m/5m` anchors 建立五桶 Development pipeline；
2. 只使用 M4 Development split：`2020-07-23`–`2022-12-30`；
3. 检查 source/profile/cadence/split 边界；
4. 计算 Development 样本充足性；
5. 封存 code/config/development receipt。

**M5-2 仍不得读取 Validation outcome，也不得打开 Holdout。**

只有 Development receipt 封存后，才可能按 M4 协议进入一次性的 primary `T2=4` Validation。15m/60m 不得为了凑齐研究范围而本地构造。

M5 完成前不得进入 M6。历史科学状态块仍由 [REPOSITORY_STATE.json](docs/REPOSITORY_STATE.json) 管理，本轮 source admission 不自动增加市场证据。
