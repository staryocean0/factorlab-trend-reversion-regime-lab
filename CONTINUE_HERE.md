# 从这里接管

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 当前产品口径

本仓工程定位：**供策略调用的趋势状态识别组件**，不是独立交易策略，不直接输出买卖、仓位、订单或 Layer 4 指令。M2 三桶基线和 M3 多周期 profile 均已冻结；五桶“极端斜率可能更易耗竭”仍只是待验证假设。

接管顺序：先读 [执行路线图](docs/ROADMAP.md)、[M1 API 合同](docs/API_CONTRACT.md)、[M1/M2 Gap 审计](docs/API_GAP_ANALYSIS.md) 与 [M2 三桶基线](docs/THREE_BUCKET_BASELINE.md)，再读当前源码 `src/factor_lab/market_state/trend_regime_profiles.py`。

## 已完成：M3 多 K 线级别参数化

M3 已落地 `src/factor_lab/market_state/trend_regime_profiles.py`，将 M2 的 20-bar / `T1=2.0` 三桶 measurement 绑定到 DataHub Layer-1 V3 wall-clock views。

首批 engineering admission：

- `1m`：1 个 profile，`trend_1m_official_v1`；
- `5m`：5 个 offset profiles；
- `15m`：2 个 offset profiles；
- `60m`：2 个 offset profiles；
- 合计 10 个 versioned profiles。

关键规则：

- `1m` 当前只有唯一 admitted view，可只传 `bar_interval=1m`；
- `5m/15m/60m` 有多个合法 view，必须显式给 `profile_id`，组件不暗选相位；
- FactorLab 不在本层 local-resample K 线；profile 直接绑定 Layer-1 immutable `close_times`；
- visible row 必须满足 `bar_end <= as_of` 与 `available_at <= as_of`；
- selected 20-bar window 若偏离 profile grid，返回 `OFF_PROFILE_GRID`；cadence 缺口返回 `CADENCE_GAP`；不插值、不回填；
- future wrong-view row 对更早 `as_of` 不可见；当前 visible wrong-view row 则拒绝；
- 所有 profile 继续使用 M2 `lookback=20` 与 `T1=2.0`，M3 没有按周期调参；
- 同一 `as_of` 不同周期可同时返回不同状态；multi-interval envelope 顶层没有 `state/global_state`，多周期聚合属于策略层。

对应回归：`tests/test_trend_regime_profiles.py`。

M3 是工程 admission，不是预测有效性、收益或生产认证；既有 `production_authority=false`、`fresh_oos=false` 不变。

## 唯一下一步：M4 五桶假设与实验协议冻结

下一次会话只推进路线图 **M4**，而且只做**预注册协议**，不运行 M5 实证。

M4 必须在读取结果之前冻结：

1. `T2` 的候选定义/选择方法；
2. 纳入哪些 M3 profiles；
3. development / validation / holdout 切分；
4. forward horizons；
5. `STRONG_UP vs UP`、`STRONG_DOWN vs DOWN` 的持续时间、转移概率、方向延续率；
6. reversal probability / time-to-first-reversal；
7. forward adverse / favorable excursion；
8. `T2` 稳健性与最小样本量；
9. 停止条件和负结果处理规则。

M4 Gate：协议在 M5 结果出现之前冻结，禁止看完结果再改 `T2`、horizon、样本切分或挑 profile。

**M4 不运行五桶实证，不把 `STRONG_UP/STRONG_DOWN` 写成正式产品状态，不进入 M5。**

历史字段对账和受限读取证据保持原状态；M2/M3/M4 工程与研究协议工作不自动改变既有科学 authority。历史报告、冻结文件和原始数据保持原路径与原字节。

修改当前证据状态时只编辑 [状态源](docs/REPOSITORY_STATE.json)，再运行 `python scripts/repository_consistency.py --render` 和 `--check`。产品路线图/API/基线正文可随里程碑演进，但生成的科学状态块仍由状态源统一管理。
