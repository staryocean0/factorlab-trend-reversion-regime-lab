# 本地执行模型接管提示

你接管 `staryocean0/factorlab-trend-reversion-regime-lab`。先读 `CONTINUE_HERE.md`，不要重新打开已经关闭的研究身份。

## 当前 authority

- R1 / R2 仍是 certified mechanisms；
- `BLACKBOX_query_count=3`，禁止 query #4；
- `production_authority=false`。

已经完成两层价格研究：

1. 纯 cash-index price validity；
2. R1 matched-parent incremental-alpha attribution。

最新正式解释：

`R1_A_CSI1000_PULLBACK_SPECIFIC_INCREMENTAL_ALPHA_SUPPORTED_TRANSPORT_NOT_YET_STRONG`

`R1_B_RAW_DIRECTIONAL_EDGE_REINTERPRETED_AS_PARENT_TREND_CONTINUATION_NOT_DISTINCT_PULLBACK_ALPHA`

## 关键结果

R1_A / CSI1000：

- 15 bars：event `+4.80bp`，matched parent control `+0.95bp`，incremental `+3.85bp`，bootstrap 95% CI `[+0.80,+6.88]bp`，4/5 年增量均值为正，LONG/SHORT 都正；
- 30 bars：event `+6.80bp`，control `+0.72bp`，incremental `+6.07bp`，CI `[+1.38,+10.66]bp`，5/5 年为正，LONG/SHORT 都正。

这不等于选定 15/30 为交易持有期；只是 frozen horizon surface 中 pullback-specific information 最明确的位置。

R1_A / STAR50：短 horizon 增量均值方向一致，但没有通过完整 strong-incremental 条件，所以只是 supportive transport。

R1_B：不要再把 120/240 raw return 当作 pullback-specific alpha。CSI1000 240 bars event `+23.43bp`，matched control `+34.63bp`，incremental `-11.20bp`。它更像 parent-trend continuation 的状态标记，不是新增 entry alpha。

## 当前任务方向

下一层只做 **R1_A carrier price transport**。

顺序：

`R1 mechanism -> R1_A incremental index alpha -> ETF/index carrier price transport -> execution economics`

如果找到 ETF / carrier 分钟数据：

1. 先记录 instrument identity、数据来源、时间范围、复权/时间戳规则；
2. outcome 前冻结 transport contract；
3. 原样 replay 已冻结的 R1_A causal event timestamps/directions；
4. 全报 `1/5/15/30/60/120/240`，禁止先选 15/30；
5. 先做 zero-cost carrier price transport；
6. synthetic SHORT 可以用于 signal transport，但必须注明非实际可执行；
7. 只有 transport 成立后才单独研究 spread/fee/T+1/borrow/futures basis/inventory。

## 仍然关闭

- R1 structural economic translations v1/v2/v3；
- R2 direct directional economic identity；
- R1_B temporal impulse completion；
- R1_B ATM option / 1x2 backspread；
- probability/time-of-day/regime/horizon rescue；
- R3/R4/R5-B1/R5-C 等历史关闭 lanes。

不要用最新结果去救这些身份。

## 工程纪律

- empirical study 一律先 freeze 后 outcome；
- synthetic tests 先于真实回放；
- 不覆盖失败证据；
- 一次性 workflow 完成后删除；
- 不提交凭据、账号、非公开链接或本地原始 DataHub lake；
- 当前 authority 入口是 `CONTINUE_HERE.md`。
