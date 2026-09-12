# Excerpt of /home/starryocean/桌面/量化/unified_datahub/docs/planning/fund_cb_l2_quote_change_recent_1y_onboarding_20260901.md
# time fields, IOPV limit, checkpoint+delta semantics

# ---- fund_cb_l2_quote_change_recent_1y_onboarding_20260901.md:58-76 ----
## 2. 身份、时间和规则

- 标的分母主键：`exchange + 6 位代码 + instrument_type + 权威身份源条目`。
  **禁止凭文件名后缀判定市场**（源侧警告：非股票品种后缀不可靠；512100 在源中被标 `.SZ`）。
  交易所归属以治理身份（`config/instrument_lifecycle/nonstock_security_identities.v5r2.json`
  及其权威后继）与代码段规则联合判定；判不出的一律进当日 `identity_unresolved` 隔离桶，不入产品。
- 代码段提取规则（仅用于从日包内**粗筛候选**，非身份判定）：`11/12`（转债）、
  `15/16`（深市基金/LOF）、`50/51/56/58`（沪市基金）。`01/20/90` 等其他段不提取。
- 时间字段：`market_observed_at`（源 `时间` 列 HHMMSSmmm → ns, Asia/Shanghai）；
  `source_available_at=null`（源不可证明）；`ingested_at`（DataHub 实际取得时间）；
  `time_authority=historical_market_replay`；`receipt_exact_pit=false`；`production_granted=false`。
- 会话分类（按时间戳区间）：`pre_open_auction`(09:15–09:25)、`continuous_am`(09:30–11:30)、
  `midday_break`(11:30–13:00)、`continuous_pm`(13:00–14:57)、`close_auction`(14:57–15:00)、
  `post_close`(>15:00)。**盘口状态禁止跨交易日/午休/集合竞价段边界延续**；
  每交易日与每连续竞价 session 起点写 full checkpoint。
- 价格为源整数（×10000），入湖保持整数 tick（`price_x10000` int64）；数量为源股数 float→int64；
  单位/最小变动价位不作硬编码假设，逐符号在审计中记录**实测**最小价位与异常。
- denominator 规则：上市前/退市后/停牌日不产生期望行；期望交易日由交易日历给出，
  源缺日进 `source_not_delivered` ledger；标的级缺日进 `symbol_day_missing` ledger。

# ---- fund_cb_l2_quote_change_recent_1y_onboarding_20260901.md:98-107 ----
### 3.2 源侧硬限制（必须在 consumer contract 中显式）

1. **IOPV 列全为 0**（510500@2021-01-04、512100@2024-01-02/2026-01-05 实测）→ iNAV 不可得，
   对应 FactorLab `waiting_tracking_inav_and_fund_affine` 的 iNAV 子项保持 `source_side_limit`。
2. 厂商逐日漏采风险已观测（512100@2024-01-02 缺 09:30–09:41）→ 逐日 open-coverage 审计 +
   与权威 1m bars 对账归因，缺口登记为 `vendor_capture_gap`，**禁止插值补造**。
3. 年份间归档结构漂移（月目录命名 `01` vs `202401`、日包内有无日期子目录、solid/非 solid）→
   parser 按日包实测结构自适应并记录 `archive_layout`。
4. 沪深代码后缀不可靠 → 见 §2 身份规则。
5. 深交所基金/转债逐笔中 `成交代码=C/D` 为撤单记录 → 逐笔产品保留 `trade_code` 原值并附语义文档。

# ---- fund_cb_l2_quote_change_recent_1y_onboarding_20260901.md:115-137 ----
## 4. Schema、物理主键与 lineage

### A. quote-change（主产品）

必填：`instrument_id/exchange/instrument_type/trading_day/session_phase/event_seq/`
`market_observed_at/valid_from/valid_until/is_checkpoint/update_type/`
`bid_price_x10000_1..10/bid_size_1..10/ask_price_x10000_1..10/ask_size_1..10/`
`last_price_x10000/last_volume/cum_volume/cum_amount/trade_count/`
`source_kind/source_file_sha256/source_day/receipt_id/parent_dataset_version`。
`ingested_at/time_authority/receipt_exact_pit` 全产品常量列。

事件语义：同一 session 内，**十档任一价/量、末价或交易状态变化才写 delta**；
session 起点与源内结构断点写 full checkpoint；`valid_until` 由下一事件时间戳闭合成左闭右开区间。
快照中仅累计量变化的行不单独成事件，其累计值随下一事件与 session/day 末行保留（可精确重建盘口状态；
逐字段对账口径 = 任意 3s tick 的十档状态 + 事件时刻累计值 + 日终累计值）。

### B. 逐笔成交（成交侧参考）

必填：`instrument_id/exchange/instrument_type/trading_day/trade_seq/market_observed_at/`
`trade_price_x10000/trade_volume/bs_flag/trade_code/bid_order_id/ask_order_id/`
`source_kind/source_file_sha256/source_day/receipt_id/parent_dataset_version`。

物理主键：A=`instrument_id+trading_day+event_seq`；B=`instrument_id+trading_day+trade_seq`。
