# 从这里接管

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 当前产品口径

本仓工程定位：**供策略调用的趋势状态识别组件**，不是独立交易策略，不直接输出买卖、仓位、订单或 Layer 4 指令。M2 三桶基线、M3 多周期 profile、M4 五桶实验协议均已冻结；五桶 H1 仍未被实证验证。

接管顺序：先读 [执行路线图](docs/ROADMAP.md)、[M2 三桶基线](docs/THREE_BUCKET_BASELINE.md)、M3 源码 `src/factor_lab/market_state/trend_regime_profiles.py`，再读 [M4 冻结协议](docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.md) 与 [机器合同](docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json)。

## 已完成：M4 五桶假设与实验协议冻结

M4 在任何五桶 forward outcome 被计算前，冻结 `trend_five_bucket_protocol_m4@1.0`：

- `T1=2.0` 保持；primary `T2=4.0`；只允许 `T2=3.0/5.0` 做预注册敏感性，不能替代 headline；
- primary carrier=`000852.SH`，replication=`000688.SH`，禁止池化 rescue；
- 公共窗口 `2020-07-23`–`2025-12-31`；development=`2020-07-23`–`2022-12-30`；validation=`2023-01-03`–`2024-12-31`；locked historical holdout=`2025-01-02`–`2025-12-31`；
- 2025 段称 protocol holdout，不冒充 fresh OOS；
- 研究 anchors：1m official、5m offset0、15m offset5、60m offset30；其余 M3 profiles 只做 phase sensitivity；
- profile 必须具有完全匹配的 Layer-1 view/clock/receipt；拿不到即 `NOT_ADMITTED`，禁止本地 resample 或换 offset；
- 统计单位固定为五桶 state episode entry；不把每根 bar 当独立样本；
- horizons=`1/3/5/10/20 bars`，primary horizon=5，primary reversal horizon=10；
- primary endpoint=`5-bar directional survival`，Strong-Moderate，H1 预测负值；
- secondary confirmatory=`10-bar reversal probability` 与 `5-bar direction-adjusted return`；
- duration / transition / time-to-first-reversal / MFE / MAE 均已预注册；
- validation 主指标每组最少 100 episodes，holdout 每组最少 50；不足即 `UNDERPOWERED`，不能降 T2 或池化造 power；
- week-cluster bootstrap 5000 次、seed=`20260914`、95% CI；primary family=4 intervals×2 directions=8，Holm FWER alpha=0.05；
- practical guard：primary directional-survival contrast 必须 `<=-5pp`；
- validation 未通过不得打开 holdout；负结果允许且有固定状态码。

`tests/test_five_bucket_protocol.py` 只验证这些冻结元数据，不计算任何 M5 outcome。

M4 **没有**计算五桶 episode 数、forward return、transition/reversal probability、MFE/MAE，也没有读取 holdout outcome。因此 M4 没有新增五桶市场证据，`production_authority=false`、`fresh_oos=false` 保持不变。

## 唯一下一步：M5 极端斜率持续性实证

下一次会话只推进 **M5**，且必须严格按冻结协议顺序：

1. 先做 source/profile admission，不能算 outcome；
2. 只在 development 做管线和样本量检查，协议字段不得修改；
3. 封存代码/config/development receipt；
4. primary `T2=4` validation 只运行一次；
5. 再运行 `T2=3/5` validation sensitivity，但不能改 primary；
6. 只有 validation 达到协议 support rule，才允许解锁对应 `T2=4` holdout 一次；
7. 最后报告 STAR50 replication 和 phase sensitivity，不能用它们改写中证1000 primary。

M5 不允许改变 `T2`、horizon、split、anchor profile、endpoint、样本门槛或 holdout unlock 规则。若 source 不足、样本不足或 H1 不成立，必须按协议记录负结果，不进入“调参救结论”。

**M5 完成前不得进入 M6 架构裁决。**

历史字段对账和受限读取证据保持原状态；本项目新工程/研究协议不自动改变既有科学 authority。历史报告、冻结文件和原始数据保持原路径与原字节。

修改当前证据状态时只编辑 [状态源](docs/REPOSITORY_STATE.json)，再运行 `python scripts/repository_consistency.py --render` 和 `--check`。产品路线图/API/基线正文可随里程碑演进，但生成的科学状态块仍由状态源统一管理。
