# 报价是 checkpoint + delta，不是完整 3s 快照流

依据：准入规格 §4.A 与 `process_symbol_full` 事件化代码（见同目录摘录）。

## 语义

源 `行情.csv` 是 3s 十档快照。入湖产品 `l2_quote_change_state` 只在下列情况写一行：

1. session 分段起点或源内结构断点 → `update_type=checkpoint`，`is_checkpoint=true`，该行带**当时完整十档**；
2. 同一 session 内，十档任一价/量或 `last_price_x10000` 变化 → `update_type=delta`，该行仍带完整十档列，但是**状态变化采样**，不是「每 3s 必有一行」。

仅累计量（`volume`/`amount`/`cum_*`）变化、十档与末价未变的源快照**不单独成事件**。因此不能把本文件当成均匀 3s 快照，也不能只看买一卖一。

`valid_from`/`valid_until` 是左闭右开。任意时刻的盘口应取覆盖该时刻的最后一条事件，而不是要求该秒必须有一行。

## 当日初始化状态

checkpoint 已写在各品种当天文件里，没有另造一份「开盘快照」。2025-12-01 两只 ETF 各 8 条 checkpoint，对应代码里的 8 个 `session_phase`（注意：实现名与规格草案不完全相同，以下以**落地代码/本文件**为准）：

| session_phase | 512100 `time_raw` | 588000 `time_raw` |
|---|---|---|
| pre_open | 84505000 | 84500000 |
| opening_auction | 91502000 | 91500000 |
| pre_open_break | 92502000 | 92500000 |
| continuous_am | 93002000 | 93000000 |
| midday_break | 113008000 | 113000000 |
| continuous_pm | 130002000 | 130000000 |
| closing_auction | 145702000 | 145700000 |
| post_close | 150002000 | 150003000 |

还原盘口：从该 session 的 checkpoint 起，按 `event_seq` 顺序应用后续 delta。不要跨午休或竞价段沿用上一段状态。

## 同刻多条与更正

- 报价：本日本提取两只 ETF 的 `market_observed_at` 均无重复。排序键是 `event_seq`，再 `market_observed_at`。
- 成交：同刻多条是正常的。512100 最大同刻 100 条，588000 最大同刻 403 条。排序键是 `trade_seq`，再 `market_observed_at`。`trade_seq` 是导入器按稳定时间排序后生成的 0..n-1，不是交易所成交编号；交易所编号在 `trade_seq_raw`。
- 本产品没有单独的「更正/重置」标记。`update_type` 只有 `checkpoint`/`delta`。
- 成交 `trade_code`：规格说深市 `C`/`D` 为撤单。本日本提取两只均为空字符串；它们是沪市 ETF，不能用深市撤单语义填进去。

## 源 CSV 有、湖产品没有的列

`行情.csv` 还有万得代码、加权平均叫卖/叫买价、不加权指数、品种总数、涨跌平家数等。导入器 `HQ_COLS` 未映射这些列，湖分区和本提取都没有。不是本次删列。
`逐笔成交.csv` 源表头本身无成交额；本提取也就没有成交额。
`逐笔委托.csv` / `委托队列.csv` 未产品化。
