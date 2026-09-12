# Excerpt of /home/starryocean/桌面/量化/unified_datahub/docs/modules/history/canonical-bars-whitepaper.md
# section 5 / 5.1

# ---- canonical-bars-whitepaper.md:111-143 ----
## 5. 查询契约

`BarsQuery` / `/api/v1/history/bars` 的选择顺序：

1. `DatasetVersionRepository.get_latest_ready_by_dataset_id(bars_<market>_<frequency>_raw_canonical)`；
2. 若不存在 canonical，才使用旧兼容逻辑 `get_latest_ready(market, frequency)`；`bars_source` staging artifact 不是默认查询候选。

因此，一旦 canonical dataset READY，外部实际看到的就是融合后的单表。查询可选 `instrument_type`；若同一 symbol 对应多个类型，必须明确类型，不能静默合并。

查询同时受数据质量供应契约约束。`BarsQuery` / `/api/v1/history/bars` 默认 `quality_policy=fail_on_unresolved`：命中 `data_quality_events` 的 blocking known issue 时直接阻断；因子研究可显式传 `quality_policy=annotate` 获取 bars、`quality` 摘要与 `quality_issues` mask；人工排查可用 `allow_with_warning`；`ignore` 只允许临时调试。canonical 不伪造 bars，不 forward fill，不把 accepted known issue 静默包装成 clean dataset。详见 [`data-quality-supply-chain-whitepaper.md`](data-quality-supply-chain-whitepaper.md)。

### 5.1 高频按需派生契约（v87）

当请求频率/视图（5m/15m/30m/60m/1d 的 raw/qfq/hfq）的预存 READY 版本缺失，或最新 READY 版本 `time_range_end` 的交易日早于查询 `end_time` 的交易日时，`BarsQuery` 从最新 READY 1m raw canonical 按需派生，**无需预物化**；派生失败才回退旧预存版本查询。显式 `dataset_version` 钉死版本时永不派生（FactorLab 固定合同语义不受影响）。

2m/3m/10m/20m 不加入这个旧 fallback 集合；它们属于独立的固定父快照、严格 `as_of`、
逐棒完整性产品 `cn_a_on_demand_kline_offset_0.v1`，走
`GET /api/v1/history/on-demand-klines`。该分离保证本次扩展不改变 5m/30m/60m 的既有含义。

派生契约（实现：`src/datahub/storage/query/bars_deriver.py`）：

- **会话分桶**：`cn_a_session_end_label_no_noon_partial_v2` 端标签合同——每段会话首桶 `[session_start, session_start+period]` 标签为 `session_start+period`，后续桶 ceil 取整，末桶 cap 到 `session_end`；上午 [09:30, 11:30]、下午 [13:00, 15:00]（含端点分钟）。13:00 午间分钟并入下午首桶，**禁止产生独立 13:00 bar**（2026-06-27 Baylum 事故；README 第 144 行）。bar 时间戳为端标签 `trading_dayT<HH>:<MM>:00Z`，输出保持 `symbol/market/instrument_type/timestamp/trading_day/open/high/low/close/volume/amount/available_at/ingested_at/source_kind/dataset_version` 列序。
- **1d**：按 `trading_day` 分组聚合，`timestamp=trading_dayT15:00:00Z`，不按固定 1440 分钟桶（避免跨夜错桶）。

#### 5.1.1 加法产品：会话相位 / 收盘锚点（不改变默认）

官方 v2 仍是默认。`session_offset_minutes` / `close_anchor=11:30` 是加法合同 `cn_a_session_wall_clock_offset_v1`，不得原地改写 09:30 / 15:00 产品，也不得复用 FactorLab 钉死的 `bars_cn_a_1d_qfq_canonical_xdxr_v9_factorlab_2009_2025_20260814`。

这不是 Hilbert / IIR 滤波器相位，也不是 3s 分笔 `session_phase`。完整金样、适合/不适合边界和 `first_tradable_slot` 语义见 [`session-offset-bars-whitepaper.md`](session-offset-bars-whitepaper.md)。查询入口仍是 `GET /api/v1/history/bars`；不传新参数时，现有 `test_60m_session_end_labels` 必须继续成立。

- **复权语义（先聚合后复权）**：stock 用 XDXR multiplier 合同（`adjusted = raw * price_multiplier`）；etf/lof 用 Sina affine 合同（`adjusted = raw * scale_multiplier + price_offset`，来自复合因子 `adjust_factors_cn_a_combined_stock_xdxr_v10_fund_sina_p0_*`）。因子 carry-forward：取 `factor trading_day <= bar trading_day` 的最近因子行。缺因子行 raw 直通（fail-safe：不伪造因子、不静默错值）。`volume`/`amount` 不复权。
- 高频段（30m/15m/5m 及以下）调整后视图不预物化；60m（Baylum 交接门）与 1d 保持显式物化。
- **性能契约（2026-08-17）**：派生全管线在单个 duckdb 会话内完成——源扫描 `CREATE TABLE AS SELECT COLUMNS(*)::VARCHAR` 直建临时表（全 VARCHAR wire shape 不变），聚合结果落 `aggregated_bars` 临时表，因子 carry-forward 用单条 `ASOF LEFT JOIN`（语义等价旧的 arg_max + 回联 + UPDATE 三段式），因子文件列集带 TTL 缓存。禁止任何 `fetchall` → Python 循环 → `executemany` 回灌路径。实测 20 symbol × 6 个月 60m qfq 从 294.6s 降至 1.38s 且与旧管线值级 0 差异；判断口径与基准见 [`performance-optimization.md`](../../architecture/performance-optimization.md) §7。
