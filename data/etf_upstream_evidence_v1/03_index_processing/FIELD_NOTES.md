# 指数 causal_flat_fill 与 available_at（实现摘录，不做前视裁决）

本地不判断是否存在前视。下列是代码与已有 2021 样例中的字段事实。

## 生成链

1. 指数 3s 观察：`market_index_transactions` / `market_index_baidu_3s_20000714_20260821_cffex_underlyings_alias_repaired_v4_20260823`。`source_kind=baidu_netdisk_market_index_transaction_3s`，`timestamp_mode=source_exact_3s`，`volume` 常为空，`amount` 有值。
2. `_derive_minute_rows` 按 `_minute_label(observation_time)` 分组：09:25–09:29→09:31；连续竞价多数为 `分钟+1` 端标签；11:29–11:30→11:30；15:00 秒→15:00。OHLC=组内首/高/低/末价；`volume=None`；`amount=sum`；**所有观察分钟** `available_at=f"{day}T15:30:00+08:00"`；`ingested_at=now()`（本批样例为 `2026-08-23T04:03:58.401461+00:00`）。
3. `export_factorlab_unified_index_kline_v3.densify_one_minute_rows`：期望钟 `09:31–11:30` 与 `13:01–15:00`。已观察行 `causal_flat_fill=False`，保留原 `available_at`（15:30+08:00）。缺钟用 **prior** close 填平 OHLC，volume/amount=0，`source_kind` 追加 `_causal_flat_missing_minute`，`causal_flat_fill=True`，**`available_at=f"{trading_day}T{clock}:00Z"`**（bar 标签，不是 15:30）。政策名 `prior_observed_point_flat_fill_non_circuit_breaker_v1`，代码写 `future_value_fill: False`。
4. FactorLab `unified_kline_v2._densify_official_one_minute_path` 是平行实现，填行不写 `available_at`。目标仓已有年 parquet 来自 v3 导出。

## 四类时间（按实现，不是推断发布时点）

| 通道 | 观察行样例 | 填行样例 |
|---|---|---|
| bar `timestamp` | `2021-01-04T09:31:00Z` 墙钟端标签 | `2021-01-04T14:59:00Z` 墙钟端标签 |
| 3s `observation_datetime` | `2021-01-04T09:30:00Z` 等源标签 | 无（填行无 3s） |
| `available_at` | `2021-01-04T15:30:00+08:00` 全日同一值 | `2021-01-04T14:59:00Z` 等于该 bar 标签 |
| `ingested_at` | `2026-08-23T04:03:58.401461+00:00` 湖写入 | 同左 |

交易所撮合时点、供应商对外发布时间、canonical 对研究“可交易/可知”时点，必须由云端对照上述字段核验。本地不宣布哪一列是 PIT 权威。

## 样例文件

- `index_3s_input_000852_20210104_0930.json`：2021-01-04 09:30:00–09:30:21 的 8 条 3s 输入（000852.SH）。
- `index_1m_observed_and_fill_samples.csv`：同指数 09:31/09:32 观察行，以及 14:59 填行（000852/000688，2021-01-04/05）。取自目标仓已有 `data/market/1m/*/2021.parquet`，未新造指数序列。
