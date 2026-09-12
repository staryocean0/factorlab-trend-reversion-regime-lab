# Excerpt of /home/starryocean/桌面/量化/unified_datahub/docs/modules/history/baidu-netdisk-data-catalog.md
# vendor volume lots / amount CNY

# ---- baidu-netdisk-data-catalog.md:394-426 ----
### 4.5 基金按日分钟 zip（中文表头）

`时间,代码,名称,开盘价,收盘价,最高价,最低价,成交量,成交额,涨幅,振幅`

| 字段 | 实测 |
|---|---|
| 时间 | `YYYY-MM-DD HH:MM:SS` |
| 代码 | `510050.SH` / `166006.SZ` |
| 成交量 | 手。`510050` 15:00 量 `89991`、额 `7884261` |
| 成交额 | 元 |
| 涨幅 / 振幅 | 百分数点，如 `0.11` |
| 开盘占位 | `09:30` 常见量额为 0、OHLC 同一价 |
| 根数 | 抽样日均为 241 根：有 `09:30`、`14:58`、`14:59`、`15:00`，无 `13:00` |

日 zip 成员是扁平 `{code}.csv`，不是按日子目录。

### 4.6 股票 / ETF 历史月包分钟线（英文表头）

`datetime,code,name,open,close,high,low,volume,amount,pct_chg,amplitude`

| 字段 | 实测 |
|---|---|
| datetime | `YYYY-MM-DD HH:MM:SS` |
| code | 沪深 `sz000001` / `sh600000`；ETF `510300.SH`；北证 `bj920906` |
| volume | 手。`sz000001` 2026-09-01 09:30 量 `3608`、额 `4214144`（3608×11.68×100） |
| amount | 元 |
| 根数 | 241；有 `09:30`/`14:58`/`14:59`/`15:00`，无 `13:00` |
| 零量 | `sz000001` 2026-09-01 **14:59** 量额为 0，其它分钟有成交 |
| 停牌占位 | `sz002969` 2026-06-04 全部 241 行量额 0、OHLC 全日同一价 |

成员布局：`{包前缀}/YYYYMMDD_1min/{code}.csv`。

2000–2025 年包内部表头是否同为英文：**未验证**（只验证了 2026-09 月包与基金按日 zip）。
