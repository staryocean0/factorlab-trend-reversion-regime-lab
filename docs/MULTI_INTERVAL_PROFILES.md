# 多 K 线级别 Profile 合同（M3）

> 状态：**M3 多周期参数化已冻结。**
>
> 本文只解决 `bar_interval`、Layer-1 wall-clock view、profile admission、cadence 与多周期并存表达。它不设计 `T2`、不验证五桶、不做收益优化，也不授予 production authority。

## 1. M3 的核心决定

M2 已冻结唯一三桶数学：20 根 completed/available K 线、log-close OLS signed slope t-score、`T1=2.0`。

M3 不为不同周期重新调公式，而是把 M2 测量绑定到**有版本的 Layer-1 K 线 view**。调用坐标因此变为：

```text
bar_interval + profile_id + as_of
```

其中：

- `bar_interval` 表示调用者需要的时间尺度；
- `profile_id` 表示该尺度下具体使用哪一个 Layer-1 wall-clock view/相位；
- profile 只能引用 DataHub 已登记的 K 线构造，FactorLab 不在本层本地 resample；
- 同一 `as_of` 可以同时返回多个周期/多个 profile 的独立状态；
- 组件不得把它们再合成为一个 `global_state`。

## 2. 为什么不能只有 `bar_interval`

当前 Layer-1 V3 对不同周期并不都存在唯一 view：

- `1m` 只有一个 official view；
- `5m` 有 offset 0/1/2/3/4 五个合法 view；
- `15m` 有 offset 5/10 两个合法 view；
- `60m` 有 offset 30/45 两个合法 view。

因此如果只传 `15m` 或 `60m`，组件若自行挑一个相位，就会制造上游不存在的“唯一默认”。M3 明确禁止这种隐式选择。

规则：

- 当某 interval 只有一个 admitted profile 时，可只传 `bar_interval`；
- 当某 interval 有多个 admitted profile 时，必须显式传 `profile_id`；
- profile 与 interval 不匹配直接拒绝；
- 未来若 profile 集合变化，调用语义通过 profile version 管理，不允许静默切换相位。

## 3. 首批 admitted intervals / profiles

首批工程 admission：

| bar_interval | profile_id | Layer-1 view |
|---|---|---|
| `1m` | `trend_1m_official_v1` | `1m_official` |
| `5m` | `trend_5m_offset0_v1` | `5m_offset_0` |
| `5m` | `trend_5m_offset1_v1` | `5m_offset_1` |
| `5m` | `trend_5m_offset2_v1` | `5m_offset_2` |
| `5m` | `trend_5m_offset3_v1` | `5m_offset_3` |
| `5m` | `trend_5m_offset4_v1` | `5m_offset_4` |
| `15m` | `trend_15m_offset5_v1` | `15m_offset_5` |
| `15m` | `trend_15m_offset10_v1` | `15m_offset_10` |
| `60m` | `trend_60m_offset30_v1` | `60m_offset_30` |
| `60m` | `trend_60m_offset45_v1` | `60m_offset_45` |

这些 profile 直接从 `src/factor_lab/data/session_offset_defaults.py` 的 `unified_kline_variants_v3()` 读取 immutable `close_times` 与 offset/view identity。

这叫**工程 admission**，不等于这些周期已经获得预测有效性、策略收益或 production certification。

## 4. M2 数学在 M3 中如何处理

所有首批 profile 都保持：

- `lookback_bars=20`
- `T1=2.0`
- estimator=`log_close_ols_slope_t@1.0`
- price transform=`log_close`

M3 不按周期调阈值，也不按指数调阈值。

理由不是“已经证明所有周期最优阈值都等于 2”，而是：**在没有新的实证 Gate 之前，不能为了周期差异提前引入参数搜索。** slope t-score 本身是无量纲量，因此工程上可以先复用同一阈值作为可比较基线。

如果以后证据表明某周期需要不同定义，必须建立新的 versioned profile/estimator，而不是在 `@1.0` 中静默改变 `T1`。

## 5. completed-bar / cadence admission

M3 继续继承 M2 的可见性规则：

```text
bar_end <= as_of
available_at <= as_of
```

另外新增 profile grid admission：

1. visible row 必须声明 `view_id`；
2. `view_id` 必须与 profile 的 Layer-1 view 完全一致；
3. selected 20-bar window 中，每个 `bar_end` 的 Asia/Shanghai 本地时钟必须落在该 profile 的 immutable `close_times`；
4. 同一交易日内，selected bars 必须按 profile grid 连续；
5. 跨日时，上一根必须是该 profile 当日最后一个 close time，下一根必须是下一可见 session 的第一个 close time；
6. cadence 缺口返回 `UNAVAILABLE / CADENCE_GAP`；
7. bar 落在错误时钟返回 `UNAVAILABLE / OFF_PROFILE_GRID`；
8. 不为了修补缺口而插值、forward-fill 或本地 resample。

### 5.1 当前仍不声称解决的事情

仅凭时间戳无法知道某个完整日期究竟是法定休市、周末，还是数据源整日缺失。因此 M3 可以验证**已出现 session 内的 wall-clock 连续性与跨 session 边界**，但不会凭日历猜测缺失交易日。

完整跨交易日数据完整性最终仍应由 Layer-1 provider/receipt admission 提供，而不是 Layer-2 自己伪造交易日历 authority。

## 6. `as_of` 前缀一致性

未来或尚未发布的行对更早 `as_of` 不可见。

M3 wrapper 先按 `bar_end/available_at` 过滤 visible prefix，再做 profile/view/grid 检查。因此：

- 未来 row 即使属于另一个 view，也不能污染当前结果；
- 未来 close 不参与当前 slope；
- 当前可见 row 如果 view mismatch，则直接拒绝，因为调用者混入了错误 provider/view；
- visible window 的 cadence 不完整则 fail closed。

## 7. 多周期并存，而不是总趋势

实现提供 `measure_multi_interval_trend_regimes_as_of(...)`，其输出只有：

```text
as_of
measurements[]
```

每一项独立包含：

- `bar_interval`
- `profile_id`
- `layer1_view_id`
- `state`
- `slope_t`
- M2 provenance / availability

顶层故意**没有**：

- `state`
- `global_state`
- 多周期投票
- 多周期权重
- BUY/SELL/position

例如同一时刻：

```text
1m = DOWN
5m = SIDEWAYS
15m = UP
60m = UP
```

是完全合法的结果。如何组合这些状态属于调用策略。

## 8. 实现与 schema

实现：

`src/factor_lab/market_state/trend_regime_profiles.py`

M3 新增：

- profile registry schema：`trend_regime_profile_registry@1.0`
- profile measurement schema：`trend_regime_profile_measurement@1.0`
- multi-interval envelope：`trend_regime_multi_interval_measurement@1.0`

这些仍是 Layer-2 measurement-side 工程合同，不是 M7 最终 `regime_state_consumer_v1`。

## 9. 回归测试

`tests/test_trend_regime_profiles.py` 至少冻结：

- 1m/5m/15m/60m admission 集合；
- 10 个 profile 与 Layer-1 view 一致；
- ambiguous interval 不可暗选 profile；
- 所有 profile 保持 M2 `20 bars + T1=2.0`；
- 同一 `as_of` 不同周期可以得到不同状态；
- multi-interval envelope 不含 global state；
- cadence gap fail closed；
- off-grid fail closed；
- visible view mismatch 被拒绝；
- future wrong-view row 对更早 `as_of` 不可见。

## 10. M3 Gate

**PASS 条件：**

- 每个 admitted profile 都绑定真实 Layer-1 V3 view；
- 不存在未声明的本地 K 线重采样；
- interval/profile 歧义显式处理；
- selected window cadence 可验证且缺口 fail closed；
- 同一 `as_of` 多周期结果可并存且不自动聚合；
- M2 数学语义不因周期参数化静默漂移；
- 不引入交易动作或 production authority。

M3 Gate 通过后，下一唯一里程碑是 **M4 — 五桶假设与实验协议冻结**。

M4 只能先冻结 `T2` 候选、样本切分、评价指标和停止条件；在协议冻结前不得查看五桶实证结果，更不得提前把 `STRONG_UP/STRONG_DOWN` 写成产品状态。
