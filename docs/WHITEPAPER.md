# 趋势状态识别组件：当前研究与工程白皮书

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](REPOSITORY_STATE.json) · [最新研究解释](research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

> 本白皮书定义**产品定位与工程边界**；上方状态块定义当前证据/数据 authority。完成工程、准入、样本量或 seal Gate 都不等于获得新的市场证据或 production authority。

## 1. 产品定位：Layer 2 状态组件，不是交易策略

本仓核心交付是供多个策略调用的**趋势状态识别组件**。它回答：在指定证券、`as_of`、K 线级别和 versioned profile 下，当前可见价格序列属于什么趋势状态、趋势强度是多少、该测量来自哪个时间/数据坐标？

它不回答买卖方向、仓位、订单、策略选择或 Layer 4 动作。状态到交易动作的映射始终属于策略层。

## 2. 当前完成状态

- **M0 PASS**：产品定位与路线图；
- **M1 PASS**：consumer/as-of/schema/availability 合同；
- **M2 PASS**：三桶数学与因果基线；
- **M3 PASS**：多 K 线级别/profile 参数化与 cadence admission；
- **M4 PASS**：五桶 H1 实验协议在结果前冻结；
- **M5 IN PROGRESS**：M5-1 source/profile admission PASS（partial）、M5-2 Development sample adequacy PASS、**M5-3 Code/Config/Development Seal PASS**；
- **唯一下一步：M5-4 one-shot primary `T2=4` Validation**。

详细状态见 [ROADMAP.md](ROADMAP.md)。M5-3 seal 见 [TREND_M5_DEVELOPMENT_SEAL_V1.md](governance/TREND_M5_DEVELOPMENT_SEAL_V1.md) 与 [机器 seal](governance/TREND_M5_DEVELOPMENT_SEAL_V1.json)。

## 3. M2 三桶基线

`trend_regime_three_bucket_baseline@1.0`：最近 20 根 completed/available K 线，`log(close)`，OLS signed slope t-score，`T1=2.0`。`DOWN: s<-2`；`SIDEWAYS: -2<=s<=2`；`UP: s>2`。坏值、缺失、少于 20 根均 fail closed；future/unpublished bar 不得影响更早 `as_of`。

`slope_t` 是无量纲趋势几何强度分数，不直接解释为 IID 假设下的正式 p-value。

## 4. M3：时间尺度与 profile 分离

稳定 measurement 坐标是 `bar_interval + profile_id + as_of`。Registry 包含 1m×1、5m×5、15m×2、60m×2 共 10 个 versioned profiles，直接绑定 DataHub Layer-1 V3 immutable wall-clock views。FactorLab 不拥有本地 bar construction authority，也不自动聚合成 global trend。

所有 M3 profiles 继续复用 M2 `lookback=20 / T1=2.0 / log_close_ols_slope_t@1.0`。

## 5. M4：五桶协议

H1：相同 interval/profile、相同方向内，极端绝对斜率状态可能比中等趋势状态更难持续、更容易衰减或反转。

冻结：

- `T1=2.0`；primary `T2=4.0`；sensitivity `T2=3.0/5.0`；
- primary carrier=`000852.SH`；replication=`000688.SH`；
- Development=`2020-07-23`–`2022-12-30`；Validation=`2023-01-03`–`2024-12-31`；holdout=`2025-01-02`–`2025-12-31`；
- anchors：1m official、5m offset0、15m offset5、60m offset30；
- exact source/profile admission 不通过即 `NOT_ADMITTED`，禁止 resample/substitution；
- episode-entry 为统计单位；horizons 1/3/5/10/20；
- primary endpoint=`5-bar directional survival`，Strong-Moderate，H1 预测负；
- secondary confirmatory=`10-bar reversal probability`、`5-bar direction-adjusted return`；
- validation primary 每组至少 100 episodes，secondary 每组至少 50；
- ISO-week cluster bootstrap 5000、seed=`20260914`、95% CI；
- primary family=`4 intervals × 2 directions = 8`，Holm FWER `alpha=0.05`；
- unavailable/underpowered planned primary hypothesis `p=1.0`；
- primary survival contrast还必须 `<=-5pp`；
- validation 不支持时不得打开 holdout；sensitivity 不能替代 primary。

## 6. M5-1：Source / Profile Admission

当前 active exact cross-index archive 只准入两指数的 `1m_official` 与 `5m_offset_0`。15m/60m anchors 和 phase-sensitivity profiles 因缺少 current active exact-view receipt 保持 `NOT_ADMITTED`。

历史 raw `available_at` 只表示 historical retrieval availability；M5 replay 冻结为 `runtime_available_at=bar_end`，同时保留 raw historical `available_at` 作 provenance，不声称测得真实 feed latency。

## 7. M5-2：Development Sample Adequacy

真实 run `34812469153` 只读取 Development，并只运行 admitted 1m/5m。四个 carrier/profile 的 strong/moderate 5-bar episode-entry 数全部远高于 100，10/20-bar secondary 可用量全部高于 50。

这只回答“Development 样本够不够”，没有计算 directional survival、reversal、return、transition、MFE/MAE、bootstrap/p-value，也没有 adjudicate H1。

## 8. M5-3：Code / Config / Development Seal

在任何 Validation outcome 出现前，`trend_m5_development_seal@1.0` 已固定：

- M4 protocol、M5-1 admission、M5-2 Development receipt 的 Git blob；
- M5-2 entrypoint/core；
- M2 slope baseline；
- M3 profile registry；
- Layer-1 clock contract；
- market-data reader；
- `data/manifest.json`；
- DataHub export identity、1m/5m source SHA256；
- Development run/head/artifact digest；
- replay clock contract。

默认 CI 通过 `git hash-object` 验证 sealed paths。任何 byte drift 都必须显式建立新版本，不能继续冒充本次预注册研究。

M5-3 没有读取 Validation/Holdout，也没有计算任何 H1 outcome。

## 9. Admission 不允许缩小 primary family

M4 预注册的 primary family 始终是 8 个 contrasts。M5-1 只使其中 1m/5m 的 4 个 contrasts 可执行；15m/60m 的 4 个 planned contrasts 仍保留在 Holm family 中，并按预注册 `p=1.0` 处理。不得因为 source Gate 失败而把 family 从 8 缩成 4。

## 10. 唯一下一步：M5-4 Primary Validation

M5-4 只允许：

1. 使用 M5-3 sealed identities；
2. 读取 Validation `2023-01-03`–`2024-12-31`；
3. primary `T2=4.0` 只运行一次；
4. 只执行 admitted 1m/5m anchors；
5. 15m/60m 继续 NOT_ADMITTED，planned p-value=1.0；
6. Holm family size 保持 8；
7. Holdout 继续 locked；
8. 不同轮才运行 `T2=3/5` sensitivity。

M5-4 后必须先封存 Validation artifact/receipt 并裁决 support rule，不得自动进入 holdout。

## 11. M6 以后

M6 才裁决最终表示：三桶+连续强度、正式五桶、或三桶主状态+五桶诊断扩展。M7 才实现正式 `regime_state_consumer_v1` facade、snapshot store、expiry/no-fallback 与 conformance tests；M8 才做策略层集成；M9 做发布与治理。

## 12. 不变边界

- `production_authority=false`
- `fresh_oos=false`
- 组件不是策略
- 五桶尚未获得产品语义
- 负结果允许
- 禁止看到结果后改 T2、split、profile、horizon、sample floor 或 multiplicity family

## 13. 路线图

`M0 定位 → M1 接口 → M2 三桶 → M3 多周期 → M4 五桶协议 → M5 实证 → M6 架构裁决 → M7 Consumer API → M8 策略集成 → M9 发布治理`
