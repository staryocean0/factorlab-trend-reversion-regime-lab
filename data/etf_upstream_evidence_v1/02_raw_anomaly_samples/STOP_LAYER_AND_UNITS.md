# 异常样例上游止层与单位

冻结样例：`docs/ops/evidence/etf_index_measurability_source_20260912/earliest_nonflat_zero_volume_examples.csv`（20 行）。本目录不是重传五年 ETF CSV。

## 找到的层

| 层 | 结果 |
|---|---|
| 已上传最终 CSV | 禁止当作更上游。OHLC/volume 与湖一致，但无 `amount`/`source_kind`/`available_at`。 |
| 4ceca canonical ETF 湖 | 20/20 命中。原字段见 `lake_4ceca_upstream_rows.csv`。`volume=0` 且 `amount=0`，OHLC 有宽度。 |
| Baidu fund 1m 史源 `bars_cn_a_1m_baidu_netdisk_history_baidu_fund_1m_fund_1m_20080101_20260625_partitioned` | 20/20 命中。OHLC/volume/amount/available_at/ingested_at/source_kind 与 4ceca 相同，仅 `dataset_version` 不同。4ceca ETF 分区是该史源的发布/硬链层，不是第二次计算。 |
| 供应商 zip/CSV 原始成员（`时间,成交量,成交额` 等） | **未找到**。本地 `/home/starryocean/下载/基金_分钟数据`、`/ETF历史数据`、`unified_datahub/.runtime/live/import_staging/baidu_netdisk` 均不存在。未解包 2026 peek。 |
| 成交明细 / 3s / 买一卖一 对应这 20 个时间戳 | **未找到**。见 `05_microstructure_inventory`。 |

**止层：已导入的 Baidu 1m bar（`source_kind=baidu_netdisk_etf_archive`）。** 没有更上游 vendor 字节，也没有这些分钟的逐笔。

## 这不是分钟聚合链

`import_local_minute_archives.py` 把供应商已经提供的 1m 表映入湖：`时间` → `YYYY-MM-DDTHH:MM:SS` + `Z`；`开盘价/最高价/最低价/收盘价/成交量/成交额` 原样转 float。没有从 tick 再聚合成这 20 根 1m。`derive_baidu_netdisk_bars_from_1m.py` 只从 1m 派生更高周期，不生成这些 1m。

## 单位

- 供应商目录实测（基金按日分钟 zip / 股票ETF历史月包）：成交量=**手**，成交额=**元**。见 `baidu-netdisk-data-catalog_etf_1m_units.md`。
- 导入器不乘 100，不改量纲。
- 目标仓导出清单曾写 `volume_unit=shares`。这与目录“手”不一致，**单位未核证**。对这 20 行 volume 与 amount 都是 0，换算不改变 0。
- 零量但 OHLC 有宽度的交易所原因：**UNKNOWN**。不能补造交易。

## available_at

这 20 行 `available_at=ingested_at=2026-06-26T15:00:39.908240+00:00`。这是 2026-06-26 UTC 入库时刻，不是 2021–2025 交易所或供应商发布时点。
