# 五桶极端斜率假设实验协议（M4）

> 状态：**M4 协议冻结；尚未运行 M5 实证。**
>
> 本文在任何五桶 forward outcome、转移概率、反转率或 excursion 结果被计算之前冻结。机器可读合同：[`docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json`](governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json)。

## 1. H1 与五桶定义

H1：在相同 `bar_interval/profile` 和相同方向内，绝对斜率极端状态可能比中等趋势状态更难持续、更容易衰减、横盘或进入反向趋势。

沿用 M2 `T1=2.0`，五桶为：

- `STRONG_DOWN`: `s < -T2`
- `DOWN`: `-T2 <= s < -2.0`
- `SIDEWAYS`: `-2.0 <= s <= 2.0`
- `UP`: `2.0 < s <= T2`
- `STRONG_UP`: `s > T2`

冻结阈值：主分析 `T2=4.0=2×T1`；敏感性仅允许 `T2=3.0` 与 `T2=5.0`。敏感性阈值不能因为主结果不理想而替代主阈值，也不允许根据样本分位数、未来收益、持续性或 bucket 数量重新调 T2。

## 2. 载体与样本切分

Primary carrier：`000852.SH`；replication carrier：`000688.SH`。禁止把两个载体池化来挽救主结果。

主协议只使用两者共同历史窗口 `2020-07-23`–`2025-12-31`：

| 段 | 日期 | 用途 |
|---|---|---|
| Development | `2020-07-23`–`2022-12-30` | 管线、source/profile admission、样本量检查 |
| Validation | `2023-01-03`–`2024-12-31` | 首次正式检验 H1 |
| Locked historical holdout | `2025-01-02`–`2025-12-31` | 仅在 validation 达到预注册支持条件后解锁一次 |

当前仓库 `fresh_oos=false`，所以 2025 段称“协议锁定历史 holdout”，不声称 fresh OOS。任何 forward outcome 不得跨 split 边界。

中证1000 在 `2020-07-23` 以前的历史不进入 M5 主推断。

## 3. M3 profile 预注册

每个 interval 用“最小 `session_offset_minutes`”这一事前机械规则选研究 anchor：

- `trend_1m_official_v1`
- `trend_5m_offset0_v1`
- `trend_15m_offset5_v1`
- `trend_60m_offset30_v1`

其余 M3 profiles 全部作为 phase sensitivity：5m offset1–4、15m offset10、60m offset45。

研究 anchor **不是产品默认 profile**，不改变 M3 的调用规则。

M5 只有在 profile 获得完全匹配的 Layer-1 view identity、causal clock 和 source receipt 时才允许运行；否则记录 `NOT_ADMITTED`。禁止本地重采样、换 offset 近似替代或因样本不足改用另一个 profile。

## 4. 事件定义

统计单位固定为**五桶状态 episode 的进入时点**，而不是每根 bar：

1. 每根已 admission 的 bar 先生成五桶状态；
2. 当前状态与紧邻上一根可用 bar 状态不同时记为 episode start；
3. 主比较只用 `UP/STRONG_UP/DOWN/STRONG_DOWN` episode starts；
4. `UNAVAILABLE` 或 source gap 会断开 episode，不跨缺失桥接；
5. forward 指标只在同一 split 内计算。

## 5. Forward horizons 与主指标

固定 horizons：`1/3/5/10/20 bars`；主 horizon = **5 bars**。反转概率固定看 `5/10/20 bars`，其中主 reversal horizon = **10 bars**。

### Primary endpoint：5-bar directional survival

Up family=`{UP,STRONG_UP}`，Down family=`{DOWN,STRONG_DOWN}`。

若 episode 起点之后 1–5 根状态全部仍属于同一方向 family，则 `directional_survival_5bar=1`。

主 contrast=`Strong - Moderate`，H1 预测 **<0**。

### Secondary confirmatory

- `reversal_probability_10bar`：10 根内首次进入相反方向 family 的概率；H1 预测 `Strong-Moderate>0`。
- `direction_adjusted_return_5bar = d × log(C[t+5]/C[t])`，上涨方向 `d=+1`、下跌方向 `d=-1`；H1 预测 strong 组更低。

### Secondary descriptive

固定报告：episode duration、directional-family duration、one-bar transition matrix、episode exit destination、各 horizon continuation rate / direction-adjusted return、5/10/20 bar reversal probability、20-bar 右删失的 time-to-first-reversal，以及 close-based MFE/MAE。

MFE/MAE 只用 close：`R_k=d×log(C[t+k]/C[t])`；`MFE=max(0,max R_k)`；`MAE=max(0,-min R_k)`。

## 6. Censoring 与最小样本

Episode 在 split 末端仍未结束则 duration 右删失；20 bars 内未出现相反方向则 reversal time 在 20 bars 右删失。forward 指标需要完整 horizon，否则该 horizon 不计入。

每个 `symbol × profile × direction × bucket` 最低要求：

- validation 主指标：strong 与 moderate 各至少 **100** 个完整 5-bar episode starts；
- holdout 主指标：各至少 **50** 个；
- 10/20-bar secondary：各至少 **50** 个；
- phase sensitivity validation：各至少 **50** 个。

不足即 `UNDERPOWERED`。不得通过降低 T2、缩短主 horizon、合并 offsets、合并两个指数或把 bar 当独立 episode 来制造 power。

## 7. 推断与多重检验

高频 episode 不按 IID 处理。冻结：

- bootstrap cluster：episode start 所在 **ISO calendar week**；
- 5000 replicates；
- seed=`20260914`；
- 95% CI。

Primary carrier 的 primary family 固定为 `4 anchor intervals × 2 directions = 8` 个 `directional_survival_5bar` contrasts，使用 Holm family-wise correction，`alpha=0.05`。

计划 hypothesis 若因 source 未 admission 或样本不足无法检验，在 primary family 中按 `p=1` 处理，不把剩余 alpha 重新分配。

Practical-effect guard：主 survival contrast 点估计必须 `<= -5 percentage points` 才算有实际量级支持。

## 8. Validation 与 holdout 规则

某 anchor interval × direction 只有同时满足以下条件才算 validation 支持 H1：

1. primary adjusted test 支持 H1；
2. survival contrast `<= -5pp`；
3. 两个 secondary confirmatory 至少一个方向符合 H1，且没有统计上清楚的反向 secondary 证据。

上涨与下跌分别判定，禁止平均后隐藏方向不对称。

Holdout 只有在 validation artifact、代码 hash、配置与 source receipts 封存，且 validation 达到预注册支持条件后才允许解锁。Validation 失败或 underpowered 时禁止打开 holdout 来补救。

Holdout confirmation 要求主 contrast 同方向、点估计 `<=-5pp`，且 95% week-block bootstrap CI 在 H1 方向排除 0。

## 9. T2 / phase / carrier 稳健性

`T2=3/5` 只做敏感性，不能替代 `T2=4`、不能决定 holdout unlock。

Anchor 主 contrast 应与同 interval 已 admission sensitivity profiles 的多数同号，且不能出现统计上清楚的相反 primary effect。Offsets 是稳健性检查，不作为更多独立样本加入主显著性检验。

`000688.SH` 完全使用同一协议并单独报告。它不能 rescue `000852.SH`。若最终声称五桶是通用组件语义，需要跨 carrier 定性一致，而不是 pooled significance。

## 10. M5 固定执行顺序

1. 只做 source/profile admission，不算 outcome；
2. 跑 development 管线与样本充足性，协议不变；
3. 封存代码/config/development receipt；
4. `T2=4` validation 运行一次；
5. 运行预注册 `T2=3/5` validation sensitivity，但不得改 primary；
6. 仅当 validation support rule 通过时解锁 `T2=4` holdout 一次；
7. 最后报告 carrier replication 与 phase sensitivity，不用它们改写 primary。

## 11. 停止条件与负结果

- `T2=4` 主结果为负：`H1_NOT_SUPPORTED`；
- 样本不足：`INCONCLUSIVE_UNDERPOWERED`；
- extreme 状态反而更持久：`H1_CONTRADICTED`；
- profile source 未 admission：`NOT_ADMITTED`；
- validation 未通过：holdout 保持关闭。

Validation outcome 一旦可见，T2、horizon、split、carrier、anchor profile、endpoint、样本门槛均不得修改。

## 12. M4 禁止事项与 Gate

M4 不计算 forward return、transition/reversal probability、五桶 episode 数量、MFE/MAE，也不读取 holdout outcome，更不建立任何交易动作映射。

M4 Gate：**协议必须在 M5 结果之前冻结，使 M5 无法通过换参数、换样本、换 profile 或换 horizon 来“救结论”。**

Gate 通过后唯一下一里程碑是 **M5 — 极端斜率持续性实证**。若未来确需改协议，必须创建新的 protocol version，不能覆盖本版。
