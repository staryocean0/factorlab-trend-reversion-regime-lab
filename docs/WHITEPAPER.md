# 趋势状态识别组件：当前研究与工程白皮书

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](REPOSITORY_STATE.json) · [最新研究解释](research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

> 本白皮书定义**产品定位与工程边界**；上方状态块定义当前证据/数据 authority。二者不能混写：完成工程里程碑不等于获得新的市场证据或 production authority。

## 1. 产品定位：Layer 2 状态组件，不是交易策略

本仓核心交付是供多个策略调用的**趋势状态识别组件**。它回答：

> 在指定证券、`as_of`、K 线级别和 versioned profile 下，当前可见价格序列属于什么趋势状态、趋势强度是多少、该测量来自哪个时间/数据坐标？

它不回答买卖方向、仓位、订单、策略选择或 Layer 4 动作。上层策略可以把 `UP / SIDEWAYS / DOWN` 映射成完全不同的交易逻辑；这种映射始终属于策略层。

## 2. 当前完成状态

截至 M3：

- **M0 PASS**：产品定位与路线图；
- **M1 PASS**：consumer/as-of/schema/availability 合同；
- **M2 PASS**：三桶数学与因果基线；
- **M3 PASS**：多 K 线级别/profile 参数化与 cadence admission；
- **下一唯一里程碑：M4**，只冻结五桶实验协议，不运行 M5 实证。

详细执行状态见 [ROADMAP.md](ROADMAP.md)。

## 3. M2 已冻结的三桶基线

`trend_regime_three_bucket_baseline@1.0` 冻结：

- 最近 20 根 `bar_end <= as_of` 且 `available_at <= as_of` 的已完成/已可用 K 线；
- `y_i = ln(close_i)`；
- `x_i = 0,...,19` 上的 OLS signed slope t-score 作为唯一三桶 authority；
- `T1 = 2.0`；
- `DOWN: s < -2`；
- `SIDEWAYS: -2 <= s <= 2`；
- `UP: s > 2`；
- 少于 20 根、坏/非正 close 均 fail closed，不跳过、不回填、不插值；
- future/unpublished bar 不能改变更早 `as_of`；
- BDCI/DII/signed efficiency 等只作为辅助诊断，不参与主状态投票。

`slope_t` 在这里是无量纲趋势几何强度分数，不应直接解释为独立同分布误差假设下的正式显著性检验。

完整规格见 [THREE_BUCKET_BASELINE.md](THREE_BUCKET_BASELINE.md)。

## 4. M3：时间尺度与 profile 已正式分离

不存在脱离时间尺度的唯一趋势状态。同一 `as_of` 完全可能出现：

```text
1m = DOWN
5m = SIDEWAYS
15m = UP
60m = UP
```

M3 把调用坐标冻结为：

```text
bar_interval + profile_id + as_of
```

其中 `bar_interval` 表示策略需要的时间尺度，`profile_id` 表示该周期下具体使用的 Layer-1 wall-clock view/相位。

### 4.1 为什么不能只传 interval

当前 DataHub Layer-1 V3 并非每个周期都有唯一 view：

- `1m`：1 个 official view；
- `5m`：offset 0/1/2/3/4，共 5 个 view；
- `15m`：offset 5/10，共 2 个 view；
- `60m`：offset 30/45，共 2 个 view。

因此当前首批 admission 为 4 个 interval、10 个 versioned profiles。只有 `1m` 因为唯一 view 可以省略 `profile_id`；`5m/15m/60m` 必须显式指定 profile。组件禁止暗选“默认相位”。

### 4.2 不在 Layer 2 本地重采样

这些 profile 直接读取 `src/factor_lab/data/session_offset_defaults.py` 的 `unified_kline_variants_v3()`，绑定 DataHub 已登记的 immutable `close_times`。FactorLab 本层不自行把 1m 拼成 5m/15m/60m，也不拥有 bar construction authority。

### 4.3 M3 不按周期调 M2 参数

所有首批 profile 继续使用：

- `lookback_bars=20`
- `T1=2.0`
- `log_close_ols_slope_t@1.0`

这不等于已经证明 `2.0` 是每个周期的最优阈值；它表示在没有新的研究 Gate 前，不为了“看起来更合理”而先做按周期调参。未来如需不同阈值，必须升 profile/estimator 版本。

## 5. M3 cadence / view / as-of admission

M3 在 M2 可见性规则之外增加：

- visible row 必须声明与 profile 完全一致的 `view_id`；
- selected 20-bar window 的 `bar_end` 必须落在该 profile 的 Asia/Shanghai immutable `close_times`；
- 同 session 内必须连续；
- 跨 session 时必须从该 profile 当日最后 grid point 接到下一可见 session 的第一 grid point；
- 缺口：`UNAVAILABLE / CADENCE_GAP`；
- 错误时钟：`UNAVAILABLE / OFF_PROFILE_GRID`；
- 不插值、不 forward-fill、不本地 resample；
- future wrong-view row 不可污染较早 `as_of`；visible wrong-view row 则拒绝。

仅凭 bar 时间戳不能区分法定休市与整日数据源缺失，因此跨交易日完整性最终仍应由 Layer-1 provider/receipt admission 负责，而不是 Layer-2 自行伪造交易日历 authority。

实现位于：

- `src/factor_lab/market_state/trend_regime_baseline.py`
- `src/factor_lab/market_state/trend_regime_profiles.py`

回归位于：

- `tests/test_trend_regime_baseline.py`
- `tests/test_trend_regime_profiles.py`

## 6. 多周期输出不产生“总趋势”

`trend_regime_multi_interval_measurement@1.0` 只返回独立 `measurements[]`。顶层故意没有：

- `state`
- `global_state`
- timeframe voting
- timeframe weights
- BUY/SELL/position

多周期如何组合，必须由策略层决定。这一点与风险识别组件的架构边界一致：趋势组件描述趋势状态，风险组件描述风险属性，上层策略组合两者后再决定交易动作。

## 7. M1 consumer 合同仍未被提前实现成生产 consumer

M1 已冻结 `regime_state_consumer_v1` 的最终安全语义：只读、as-of、显式 unavailable/expiry、最新状态过期不得回退旧状态、snapshot/provenance/version 不可被调用者改写。

M2/M3 当前仍属于 measurement-side primitive/profile contract；M7 才实现正式 consumer facade、snapshot store/index、`valid_until` 和 conformance tests。不能把 M3 measurement wrapper 宣称成已经完成的生产 consumer。

## 8. 五桶仍只是研究假设

候选定义：

- `STRONG_DOWN: s < -T2`
- `DOWN: -T2 <= s < -T1`
- `SIDEWAYS: -T1 <= s <= T1`
- `UP: T1 < s <= T2`
- `STRONG_UP: s > T2`

核心 H1：极端绝对斜率可能比普通趋势斜率更容易耗竭、横盘或反转。

当前没有证据把 H1 当成事实，更不能把 `STRONG_UP = SELL` 或 `STRONG_DOWN = BUY` 写进组件。即使未来 H1 成立，交易映射仍属于策略层。

M4 只允许先冻结：`T2` 候选、纳入 profiles、样本切分、forward horizons、持续时间/转移概率/方向延续率、reversal probability、time-to-first-reversal、adverse/favorable excursion、稳健性、最小样本量和停止条件。**协议冻结前不得运行 M5。**

## 9. 三桶、五桶与连续强度的最终架构仍由证据决定

未来允许三种裁决：

1. 三桶 + 连续强度；
2. 正式五桶；
3. 三桶主状态 + 五桶研究/诊断扩展。

负结果是允许结果。五桶如果没有稳定增量，就保留三桶，不为了“更细”强行升级产品语义。

## 10. 证据与历史边界

本仓此前关于中证1000、科创50、趋势反转、均值回归、ETF/指数来源对账等研究继续保留，不能因为产品方向更新而回写旧结论。

M0–M3 的工程工作不会自动改变：

- `production_authority=false`
- `fresh_oos=false`
- 既有 scientific status
- 历史报告/冻结证据的字节内容与结论

旧分钟、逐笔、报价、指数 3 秒数据的量纲、同步和可用性限制继续服从 [DATA.md](DATA.md) 与冻结研究报告。

## 11. 路线图与执行纪律

顺序固定：

`M0 定位 → M1 接口 → M2 三桶 → M3 多周期 → M4 五桶协议 → M5 实证 → M6 架构裁决 → M7 Consumer API → M8 策略集成 → M9 发布治理`

纪律：

- 一次会话只推进当前里程碑；
- 当前 Gate 没过，不自动跳阶段；
- 先冻结评价口径，再看会影响结论的结果；
- 不为某个策略的回测收益修改状态定义后再反称组件“客观识别”了趋势。

**当前唯一下一步：M4 五桶假设与实验协议冻结。M4 不运行 M5 实证。**

## 12. 维护规范

[状态源](REPOSITORY_STATE.json)统一管理科学状态块；产品路线图/API/基线正文可以按里程碑演进，但 evidence authority 变化必须通过正式状态源、裁决和测试，不能靠修改白皮书文字制造新证据。
