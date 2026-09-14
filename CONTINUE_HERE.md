# 从这里接管

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 当前产品口径

本仓工程定位：**供策略调用的趋势状态识别组件**，不是独立交易策略，不直接输出买卖、仓位、订单或 Layer 4 指令。三桶基线已经在 M2 冻结；五桶“极端斜率可能更易耗竭”仍只是待验证假设。

接管顺序：先读 [执行路线图](docs/ROADMAP.md)、[M1 API 合同](docs/API_CONTRACT.md)、[M1/M2 Gap 审计](docs/API_GAP_ANALYSIS.md) 与 [M2 三桶基线](docs/THREE_BUCKET_BASELINE.md)，再读 [当前组件白皮书](docs/WHITEPAPER.md)。

## 已完成：M2 三桶基线冻结与可复现性

M2 已落地 `src/factor_lab/market_state/trend_regime_baseline.py`，冻结 `trend_regime_three_bucket_baseline@1.0`：

- 主状态 authority：20 根已完成/已可用 K 线上的 log-close OLS signed slope t-score；
- `T1=2.0`；`s<-2` 为 DOWN，`-2<=s<=2` 为 SIDEWAYS，`s>2` 为 UP；
- `bar_end <= as_of` 且 `available_at <= as_of` 才可参与计算；
- 少于 20 根、坏/非正 close 均 fail closed，不跳过、不回填、不插值；
- 未来或尚未发布的 bar 不得改变较早 `as_of`；
- BDCI/DII 等仍是辅助诊断，不参与三桶主状态投票；
- 20-bar 与 `T1=2.0` 在 `@1.0` 中禁止静默修改。

这是一项**新冻结基线**，不是伪称恢复本仓无法取回的旧 `trend_continuity_regime.py`。M2 没有做收益优化，也没有给五桶任何新证据或 production authority。

对应回归位于 `tests/test_trend_regime_baseline.py`，覆盖边界、涨/平/跌、价格尺度不变性、future/unpublished bar 隔离、缺失 fail-closed、输入顺序、timezone/重复 bar 以及参数冻结。

## 唯一下一步：M3 多 K 线级别参数化

下一次会话只推进路线图 **M3**。

M3 要解决：

1. `bar_interval` 与 versioned `profile` 的绑定方式；
2. 首批实际可 admission 的周期集合，而不是先验承诺全部 `1m/5m/15m/60m`；
3. 各周期 completed-bar / session / cadence-gap 规则；
4. `T1=2.0` 的无量纲 slope t-score 在不同周期下是否可直接共用，还是需要不同 profile/version；
5. 同一 `as_of` 下不同周期状态并存的稳定表示；
6. provider/data admission 与 fail-closed 行为。

M3 Gate：每个正式支持的周期都能独立、因果、可复现地产生状态；组件不把多个周期擅自合成为一个“总趋势”。

**M3 不设计 `T2`，不运行五桶极端斜率实证，不进入 M4/M5。**

最近完成的历史字段对账和受限读取证据仍保持原状态；M2/M3 工程工作不自动改变 `production_authority=false`、`fresh_oos=false` 或既有科学证据状态。历史研究报告、冻结文件和原始数据保持原路径与原字节。

修改当前证据状态时只编辑 [状态源](docs/REPOSITORY_STATE.json)，再运行 `python scripts/repository_consistency.py --render` 和 `--check`。产品路线图/API/基线正文可随里程碑演进，但生成的科学状态块仍由状态源统一管理。
