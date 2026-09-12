# 时间字段与量纲（本产品自己的代码，不继承 1m Z 例外）

DataHub commit：`4b4d36a16076c347ed7810eeed37391571a3cc3d`。
不得把 `cn_a_1m_4ceca` 的 Z=上海墙钟规则套到本包 L2 / tick / 指数 3s。

## ETF 报价 / 成交

导入器：`scripts/materialize_fund_cb_l2_recent_1y.py`（SHA256 `faf8eb738e02abadce193f363aeed208011946790de8434f28baaba0599285c7`）。
准入规格：`docs/planning/fund_cb_l2_quote_change_recent_1y_onboarding_20260901.md`（SHA256 `ef72962296eafd4e7a0fc218434558f26659559b4d61445c203276d869e9a8e7`）。

| 字段 | 类别 | 本产品实际赋值 | 时区 / 精度 |
|---|---|---|---|
| `time_raw` | 源观察墙钟标签 | 源 `时间` 列，格式 `HHmmssSSS`（可见无前导零，如 `84505000`） | 规格写 Asia/Shanghai；毫秒 |
| `自然日` / `source_day` / `trading_day` | 源交易日 | 本提取为 `20251201` / `2025-12-01` | 日历日，不是发布时间 |
| `market_observed_at` | 由源观察标签构造的时刻 | `_time_raw_to_ns`：`Timestamp(年,月,日).value`（UTC 日历日 00:00 的 epoch ns）加上墙钟时分秒毫秒，再 `to_datetime(..., unit='ns')` 写成 **无时区** timestamp | 钟面数字等于 `time_raw` 的上海墙钟；**不是**带 Z 的 UTC 字符串，也不能当已认证的交易所/供应商发布时刻 |
| `valid_from` / `valid_until` | 产品事件有效区间 | `valid_from = market_observed_at`；`valid_until` = 下一事件时刻，末日收成当天 15:00:00 | 左闭右开；跨 session 不延续 |
| `ingested_at` | 入库 / 取得时间 | 本日本提取常量 `2026-09-01T19:38:51+08:00`（报价）与 `2026-09-01T19:39:09+08:00`（成交） | DataHub 处理日，不是 2025-12-01 的交易所发布时间 |
| `source_available_at` | 供应商发布 | 规格写 `null`（源不可证明） | **本产品 schema 无此列** |
| `time_authority` | 合同标签 | `historical_market_replay` | 不是实时 as-of |
| `receipt_exact_pit` | 合同标签 | `false` | 不得当精确 PIT |

3s 量化：源是 3s 十档快照流；入湖后变成 checkpoint+delta 事件，**不是**每 3s 一行。只累计量变化的源快照不单独成事件。本提取未做去重、未做时钟平移。

## 指数 3s

导入器：`src/datahub/core/services/market_indices/transactions_service.py`（SHA256 `e8282d00bfa0c67c9515ed49e120ba15de9a0723257f0dc50887b2401f435b66`）。
源列：`时间,价位,成交额`。`timestamp_mode` 本日本提取全部为 `source_exact_3s`。

| 字段 | 类别 | 本产品实际赋值 |
|---|---|---|
| 源 `时间` | 源观察字符串 | 按 `"%Y-%m-%d %H:%M:%S"` **naive** 解析 |
| `observation_datetime` | 导入器写出的标签 | `strftime("%Y-%m-%dT%H:%M:%SZ")`：在 naive 墙钟后面加了 `Z`。这是**本导入器自己的写法**，不是 1m 4ceca 合同，也不能单凭 `Z` 证明 UTC 或交易所发布时间 |
| `observation_time` | 源观察钟面 | `HH:MM:SS`，与上面 naive 解析一致 |
| `trading_day` | 源日期部分 | `value.date().isoformat()` |
| `volume` | 导入器常量 | `_normalize_observation` 写 `None`；本日本提取两只指数全部为 null |
| `source_kind` | 产品常量 | `baidu_netdisk_market_index_transaction_3s` |
| 供应商/交易所发布时间 | 未取得 | UNKNOWN |

本提取 000852/000688 相邻间隔多数为 3 秒；另有约 300s 与约 5394–5397s 间隔，后者与午休量级一致。间隔统计不是完整性证明，也不授权填行。

## 价格 / 数量 / 金额

字段名不是独立证明。本包**不换算**。

| 对象 | 产品表示 | 已有依据 | 对本日两只 ETF / 两只指数 |
|---|---|---|---|
| 报价/成交价格 | `*_x10000` int64，原样保留 | 规格：源整数 ×10000；目录对其他样本测过 `91600=9.16` | 量纲标签是源 ×10000。是否对这两只当日也是人民币元/10000：**未用交易所文件独立核证**，不先除 10000 |
| 报价 `volume` / 档位 `*_size_*` / `cum_volume` | float64 | 规格：源数量按股读入 float；目录 4.1 对其他样本写「股」 | 股 vs 手：**UNKNOWN**。目录抽样不是本日 512100/588000 证明 |
| 报价 `amount` / `cum_amount` | float64 | 目录 4.1 对其他样本写「元」 | 是否本日这两只也是人民币元：**UNKNOWN**，不换算 |
| 成交 `volume` | float64 | 目录 4.2 对其他样本写「股」 | 同上，**UNKNOWN** |
| 成交成交额 | **无此列** | 源 `逐笔成交.csv` 表头本身无成交额 | 缺失，不编造 |
| 指数 `price` / `amount` | float64 | 源 `价位`/`成交额` 直接 `float()` | 指数点位与成交额单位未在本包另证 |
| 指数 `volume` | 全 null | 导入器写 `None` | 不是「成交量为 0」 |

## IOPV / iNAV

报价有 `iopv_raw`。2025-12-01 两只 ETF 全日均为字符串 `"0"`。规格已登记源侧 IOPV 常为空，iNAV 不可得。本包不为 IOPV 采购新产品。没有非零 IOPV，不能声称算出真实 NAV 折溢价。
