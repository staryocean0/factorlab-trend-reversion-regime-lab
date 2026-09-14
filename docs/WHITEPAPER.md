# 趋势状态识别组件：当前研究与工程白皮书

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](REPOSITORY_STATE.json) · [最新研究解释](research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

> 本白皮书定义**产品定位与工程边界**；上方状态块定义当前证据/数据 authority。二者不能混写：完成工程或协议里程碑不等于获得新的市场证据或 production authority。

## 1. 产品定位：Layer 2 状态组件，不是交易策略

本仓核心交付是供多个策略调用的**趋势状态识别组件**。它回答：

> 在指定证券、`as_of`、K 线级别和 versioned profile 下，当前可见价格序列属于什么趋势状态、趋势强度是多少、该测量来自哪个时间/数据坐标？

它不回答买卖方向、仓位、订单、策略选择或 Layer 4 动作。状态到交易动作的映射始终属于策略层。

## 2. 当前完成状态

- **M0 PASS**：产品定位与路线图；
- **M1 PASS**：consumer/as-of/schema/availability 合同；
- **M2 PASS**：三桶数学与因果基线；
- **M3 PASS**：多 K 线级别/profile 参数化与 cadence admission；
- **M4 PASS**：五桶 H1 实验协议已在任何 M5 outcome 被计算之前冻结；
- **下一唯一里程碑：M5**，严格按 M4 协议执行极端斜率持续性实证。

详细状态见 [ROADMAP.md](ROADMAP.md)。M4 协议见 [TREND_FIVE_BUCKET_PROTOCOL_M4_V1.md](governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.md) 和 [机器合同](governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json)。

## 3. M2 已冻结的三桶基线

`trend_regime_three_bucket_baseline@1.0`：

- 最近 20 根 `bar_end <= as_of` 且 `available_at <= as_of` 的已完成/已可用 K 线；
- `y_i = ln(close_i)`；
- `x_i = 0,...,19` 上的 OLS signed slope t-score 作为唯一三桶 authority；
- `T1 = 2.0`；
- `DOWN: s < -2`；`SIDEWAYS: -2 <= s <= 2`；`UP: s > 2`；
- 少于 20 根、坏/非正 close 均 fail closed，不跳过、不回填、不插值；
- future/unpublished bar 不能改变更早 `as_of`；
- BDCI/DII/signed efficiency 等只作为辅助诊断，不参与主状态投票。

`slope_t` 是无量纲趋势几何强度分数，不应直接解释为 IID 假设下的正式显著性检验。

## 4. M3：时间尺度与 profile 分离

M3 把调用坐标冻结为：

```text
bar_interval + profile_id + as_of
```

首批 admission：

- `1m`：1 个 official view；
- `5m`：offset 0/1/2/3/4，共 5 个 view；
- `15m`：offset 5/10，共 2 个 view；
- `60m`：offset 30/45，共 2 个 view。

合计 10 个 versioned profiles。只有 `1m` 因为唯一 view 可以省略 `profile_id`；`5m/15m/60m` 必须显式指定 profile。组件禁止暗选默认相位。

这些 profile 直接绑定 DataHub Layer-1 V3 immutable `close_times`。FactorLab 本层不自行把 1m 拼成更高周期，也不拥有 bar construction authority。

所有 profiles 继续复用 M2 `lookback_bars=20 / T1=2.0 / log_close_ols_slope_t@1.0`。这不是证明阈值对所有周期最优，而是避免未经研究 Gate 就按周期调参。

## 5. M3 cadence / view / as-of admission

- visible row 必须匹配 profile `view_id`；
- selected 20-bar window 必须落在 profile immutable clock grid；
- cadence 缺口返回 `CADENCE_GAP`；错误时钟返回 `OFF_PROFILE_GRID`；
- 不插值、不 forward-fill、不本地 resample；
- future wrong-view row 不污染更早 `as_of`；
- 多周期结果独立并存，顶层没有 `global_state`。

完整交易日缺失是否属于节假日还是 source 丢失，最终仍由 Layer-1 provider/receipt admission 负责。

## 6. M4：五桶协议已经冻结，但五桶尚未被验证

H1：在相同 interval/profile 和相同方向内，极端绝对斜率状态可能比中等趋势状态更难持续、更容易衰减、横盘或进入反向趋势。

M4 沿用 `T1=2.0`，冻结：

- primary `T2=4.0`；
- sensitivity 仅 `T2=3.0/5.0`；
- 五桶边界：`STRONG_DOWN / DOWN / SIDEWAYS / UP / STRONG_UP`；
- primary carrier=`000852.SH`，replication=`000688.SH`，禁止池化 rescue；
- 公共历史窗口 `2020-07-23`–`2025-12-31`；
- Development=`2020-07-23`–`2022-12-30`；
- Validation=`2023-01-03`–`2024-12-31`；
- locked historical holdout=`2025-01-02`–`2025-12-31`，明确不是 fresh OOS；
- 研究 anchor profiles：1m official、5m offset0、15m offset5、60m offset30；其他 M3 profiles 只做 phase sensitivity；
- source/profile 没有 exact Layer-1 view/clock/receipt 时必须 `NOT_ADMITTED`，禁止本地 resample 或换相位替代；
- 主统计单位是五桶 state episode entry，不把每根 bar 当 IID 事件；
- horizons=`1/3/5/10/20 bars`，primary horizon=5，primary reversal horizon=10；
- primary endpoint=`5-bar directional survival`，Strong-Moderate，H1 预测负值；
- secondary confirmatory=`10-bar reversal probability` 与 `5-bar direction-adjusted return`；
- duration、transition、time-to-first-reversal、MFE/MAE 均预注册；
- validation 主指标每组至少 100 episodes，holdout 每组至少 50；
- ISO-week cluster bootstrap 5000 次，seed=`20260914`，95% CI；
- primary family=`4 intervals × 2 directions = 8`，Holm FWER `alpha=0.05`；
- practical guard：primary survival contrast 必须 `<=-5pp`；
- validation 未通过不得解锁 holdout；
- `T2=3/5` 不能替代 `T2=4` headline；
- 负结果明确允许 `H1_NOT_SUPPORTED / INCONCLUSIVE_UNDERPOWERED / H1_CONTRADICTED / NOT_ADMITTED`。

这些规则由 `docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json` 和 `tests/test_five_bucket_protocol.py` 固定。

## 7. M4 没有产生新的市场证据

M4 明确没有：

- 计算五桶 episode 数；
- 计算 forward return；
- 计算 transition/reversal probability；
- 计算 time-to-first-reversal；
- 计算 MFE/MAE；
- 读取 locked holdout outcome；
- 根据 observed distribution 调 T2。

所以 M4 的 PASS 只表示**研究协议已在结果之前冻结**，不表示 H1 已获得支持。

## 8. M5 的固定执行纪律

M5 必须按协议顺序：

1. source/profile admission，不算 outcome；
2. development 管线与样本量检查，协议字段不变；
3. 封存代码/config/development receipt；
4. `T2=4` validation 一次；
5. `T2=3/5` validation sensitivity，但不改 primary；
6. 只有 validation 达到 support rule 才解锁 `T2=4` holdout；
7. 最后报告 STAR50 replication 与 phase sensitivity，不用它们改写 CSI1000 primary。

若 source 不足、样本不足或 H1 不成立，必须按冻结负结果规则停止，不能通过改 T2、horizon、split 或 profile 来补救。

## 9. 三桶、五桶与连续强度的最终架构仍由 M6 裁决

允许三种最终结果：

1. 三桶 + 连续强度；
2. 正式五桶；
3. 三桶主状态 + 五桶研究/诊断扩展。

即使 M5 发现统计差异，也不能直接推出任何交易动作。M6 只裁决状态表示是否值得进入正式组件语义。

## 10. M1 consumer 合同仍未被提前实现成生产 consumer

M1 已冻结 `regime_state_consumer_v1` 的安全语义：只读、as-of、显式 unavailable/expiry、最新状态过期不得回退旧状态、snapshot/provenance/version 不可被调用者改写。

M2–M4 仍属于 measurement/profile/research-protocol 层；M7 才实现正式 consumer facade、snapshot store/index、`valid_until` 和 conformance tests。

## 11. 证据与历史边界

M0–M4 不自动改变：

- `production_authority=false`
- `fresh_oos=false`
- 既有 scientific status
- 历史报告/冻结证据的结论

旧分钟、逐笔、报价、指数 3 秒数据的量纲、同步和可用性限制继续服从 [DATA.md](DATA.md) 与冻结研究报告。

## 12. 路线图与执行纪律

顺序固定：

`M0 定位 → M1 接口 → M2 三桶 → M3 多周期 → M4 五桶协议 → M5 实证 → M6 架构裁决 → M7 Consumer API → M8 策略集成 → M9 发布治理`

纪律：一次会话只推进当前里程碑；当前 Gate 没过不跳阶段；先冻结评价口径再看结果；负结果允许；不得为某个结果事后修改状态定义。

**当前唯一下一步：M5 极端斜率持续性实证，且必须严格执行 M4 protocol v1。**

## 13. 维护规范

[状态源](REPOSITORY_STATE.json)统一管理科学状态块；产品路线图/API/基线正文可以按里程碑演进，但 evidence authority 变化必须通过正式状态源、裁决和测试，不能靠修改白皮书文字制造新证据。
