# 2025-12-01 一天原始记录

把这一天的实际报价、成交和指数 3s 交到云端核验，看它是否补上观测缺口。
不是策略研究，不是收益回测，不重开 R1_A，不改旧行情/信号/配对/阈值，不重传上一包白皮书或五年分钟 CSV。

选日依据是上次盘点的同窗可得性，不是价差或波动。一天样本不是代表性验证集。

公开仓交付的是 DataHub **已 serving 的固定版本研究产品**按日、按品种过滤后的原字段文件，不是供应商 7z，不含账号/token/cookie。研究使用权限不等于交易所授权或生产授权；`production_granted=false`。

## 六个逻辑文件

行数与上次盘点声明一致，不是凑数删行的结果。指数当天有行，已实查，不是用产品全区间代替。

| 文件 | 行数 | 字节 | SHA256 | 源产品 |
|---|---:|---:|---|---|
| `quotes/512100_20251201.parquet` | 4823 | 483080 | `ecf988184326b719ad614765ccf14523cc8feaac6fb3b39e65648555891fa5e8` | `fund_cb_l2_quote_change_cn_a_3s_baidu_shidang_20250901_20260828_v1_20260902` |
| `quotes/588000_20251201.parquet` | 4975 | 678007 | `c096743553b5009e15dc53c5cdcb324017e5361e5d19c5a64308f55f0ae00387` | 同上 |
| `trades/512100_20251201.parquet` | 10376 | 260472 | `44efaef888630a7ef07d8506b3d27d1adf12824d83ff00a2099b447d2570b704` | `fund_cb_tick_trades_cn_a_baidu_shidang_20250901_20260828_v1_20260902` |
| `trades/588000_20251201.parquet` | 93639 | 1990362 | `4ca92dbe626eaaf7fcc1ed9c20b9645a7485262da85f1bbee1233ed51bca7dad` | 同上 |
| `index_3s/000852_20251201.parquet` | 4748 | 81666 | `ae8f72b56cc92f0c6d9b94c870a366a696b707ac14f7dda3e06d984f23da4c99` | `market_index_baidu_3s_20000714_20260821_cffex_underlyings_alias_repaired_v4_20260823` |
| `index_3s/000688_20251201.parquet` | 4746 | 76128 | `7007e8dc9bbd8815109dc795e9826fcc91174da408ab8676fdd8173c61bd280d` | 同上 |

湖根相对路径与源分区 SHA256：

| 逻辑文件 | 源分区（相对 `unified_datahub/.runtime/live/lake/`） | 源文件 SHA256 | 源字节 |
|---|---|---|---:|
| 两只 ETF 报价 | `fund_cb_l2_quote_change_recent_1y/dataset_version=fund_cb_l2_quote_change_cn_a_3s_baidu_shidang_20250901_20260828_v1_20260902/trading_month=2025-12/trading_day=2025-12-01.parquet` | `cf834a8f65b123fddc450c1c20104353b2bf579351922b514efa7588d8adfe64` | 302106108 |
| 两只 ETF 成交 | `fund_cb_tick_trades_recent_1y/dataset_version=fund_cb_tick_trades_cn_a_baidu_shidang_20250901_20260828_v1_20260902/trading_month=2025-12/trading_day=2025-12-01.parquet` | `8264dc516cde7ecb5542a9d10b1b5ddeaa310fae1dad89d035f4aac58a8c5c75` | 427233729 |
| 两只指数 3s | `market_index_transactions/dataset_version=market_index_baidu_3s_20000714_20260821_cffex_underlyings_alias_repaired_v4_20260823/observations.parquet` | `a2abc93ef0975490aae73c606ca8157a15c44cd182626c7537a9a62494310540` | 1047166337 |

供应商日包 SHA（产品列 `source_file_sha256`，两只 ETF 报价与成交相同）：`f05a329a65e5e8b1142c83bbb8bdadfa3fc68b78effb7bb36768f41585902306`。
指数源归档 SHA（`source_archive_sha256`）：`febdd4e2fd7717e1a7650c8147d962989b4dd6fdfaba9b2f15392b397c0ab2d8`。
本地未再找到该供应商 7z 日包本身。

过滤：ETF 仅 `code IN ('512100','588000')`；指数仅 `trading_day='2025-12-01' AND symbol IN ('000852.SH','000688.SH')`。不按分钟、价差、成交量、价格有效性筛行。不去重、不填价、不改 quantity=0、不换算 x10000、不把入库时刻改名为交易所发布时间。`read_parquet(..., hive_partitioning=false)`，schema 与源文件列一致（报价 77 列，成交 24 列，指数 19 列）。导出脚本：`export_one_day.py`。

## 源时间字段首末值

| 文件 | 源时间字段首 | 源时间字段末 |
|---|---|---|
| 512100 报价 `time_raw` / `market_observed_at` | `84505000` / `2025-12-01 08:45:05` | `150002000` / `2025-12-01 15:00:02` |
| 588000 报价 | `84500000` / `2025-12-01 08:45:00` | `150003000` / `2025-12-01 15:00:03` |
| 512100 成交 | `92500650` / `2025-12-01 09:25:00.650000` | `145959150` / `2025-12-01 14:59:59.150000` |
| 588000 成交 | `92501090` / `2025-12-01 09:25:01.090000` | `145959950` / `2025-12-01 14:59:59.950000` |
| 000852 指数 `observation_datetime` | `2025-12-01T09:25:00Z` | `2025-12-01T15:00:06Z` |
| 000688 指数 | `2025-12-01T09:25:00Z` | `2025-12-01T15:00:06Z` |

这些钟面值按各产品自己的导入器解释，见 `dictionaries/TIME_AND_UNITS.md`。指数标签上的 `Z` 是该导入器给 naive 墙钟加的后缀，不是 1m 4ceca 例外的继承。

## 13:26 附近（不宣称已找到那根 1m bar 的逐笔真值）

零量样例里有 `512100.SH 2025-12-01 13:26:00+08:00`。本包只交整天。同日存在记录 ≠ 已还原那根 1m bar。

| 文件 | `time_raw`/`observation_time` 落在 13:26 的行数 | 补充 |
|---|---:|---|
| 512100 报价 | 20 | 该分钟首条事件 `132602000`；13:26:00 由 `valid_from=13:25:59` 的前一条 delta 覆盖 |
| 588000 报价 | 20 | 含 `132600000` |
| 512100 成交 | 22 | 同刻可有多笔 |
| 588000 成交 | 134 | 同刻可有多笔 |
| 000852 / 000688 指数 | 各 20 | `13:26:00` 起每 3s 到 `13:26:57` |

## 必须一起读的说明

1. 源路径 / SHA / schema / 导出条件：本 README + `export_receipt.json` + `manifest.json`
2. 时间字段类别、时区、3s 规则、量纲：`dictionaries/TIME_AND_UNITS.md` 与代码摘录
3. 快照 vs 增量、checkpoint、同刻排序：`dictionaries/SNAPSHOT_VS_DELTA.md`
4. 同日行动：`actions_20251201/KNOWN_ACTIONS.md`
5. IOPV：两只报价全日 `iopv_raw="0"`。不能据此算真实 NAV 折溢价

## 尚未知 / 未取得

- 供应商 7z 日包原文件（只有产品列里的 archive SHA）
- 成交额（tick 源表头与产品均无）
- `source_available_at` / 交易所或供应商发布时间（列不存在或不可证明）
- 成交量股 vs 手；报价金额是否确定为人民币元
- 完整 2025-12-01 停牌/公告日历
- 非零 IOPV / iNAV
- 指数 `volume`（导入器写 null）

## 读取

```bash
python -c "import pyarrow.parquet as pq; t=pq.read_table('data/etf_microstructure_sample_20251201_v1/quotes/512100_20251201.parquet'); print(t.num_rows, t.schema)"
```

不要用 1m/日线替代本包。本地到此结束；云端做后续验收。
