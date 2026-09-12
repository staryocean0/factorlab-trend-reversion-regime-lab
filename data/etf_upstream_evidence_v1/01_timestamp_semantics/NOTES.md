# 时间标签：实现事实，不是相关性平移

本目录交付 DataHub 合同原文与导出解码，供云端核验。

1. 固定 1m 身份是 `bars_cn_a_1m_raw_canonical_4ceca170a851`。
2. `timestamp` 形如 `2021-01-04T10:47:00Z`。`Z` 是上海墙钟标签载体，不是 UTC 瞬间。同一墙钟若写成真实 UTC 瞬间应是 `2021-01-04T02:47:00Z`，该 UTC 字符串不能直接当查询条件。
3. 合同 `cn_a_session_end_label_no_noon_partial_v2` / `bar_align=session_end_label_v2`。上午窗口分钟 `[570,690]` = `[09:30,11:30]`，下午 `[780,900]` = `[13:00,15:00]`，两端包含。13:00 并入下午首桶，禁止独立 13:00 更高周期 bar。
4. `frequency=1m` 不能加 `session_offset_minutes` 或非默认 `close_anchor`。已上传 ETF 分钟 CSV 不是用 ETF/指数相关性选平移得到的。
5. 目标仓导出把湖中 `...Z` 去掉后 `tz_localize("Asia/Shanghai")`，见 `export_datahub_lake_timestamp.py`。
6. `available_at` / `ingested_at` 是各生产者知识/导入通道。本批 ETF 1m 两列都是 `2026-06-26T15:00:39.908240+00:00`（UTC 入库），不是 2021 交易所发布时点。

不要用本说明替代原文件。哈希与行号见 `manifest.json`。
