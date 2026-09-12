---
doc_id: MODULE-HISTORY-DH-001-CANONICAL_BARS_WHITEPAPER
truth_role: tech-asset
module_primary: history
module_related:
  - platform
  - tests
governed_surface: canonical multi-source bars materialization
---

# Canonical Bars 单表白皮书

## 2026-08-24 Serving 事实

`READY` 只表示存储生命周期，不表示研究能力授权。原
`cn_a_raw_canonical_bars` Serving 版本的不可变目录已经不存在，因此控制面已追加 revoke；
当前物理候选 `bars_cn_a_1d_raw_canonical_tdx_1m_daily_20260814_auto_20260817T064351`
虽然覆盖至 2026-08-14、质量分 100、重复键为 0，也不能自动继承旧授权。

旧 FactorLab 缺口重放仍有 `123251@2026-07-15..2026-07-23` 七个价格日：官方元数据证明
当日非停牌，腾讯/新浪 OHLCV 双源一致，但本轮没有取得免费可审计的历史成交额字段，深交所
官方历史接口在当前网络和浏览器会话均不可达。产品继续 fail closed，不用估算成交额补造 bar，
也不通过 latest READY 回退。完整审计见
`evidence/repository_semantic_audit_20260824/market_data_semantics.md`。

## 1. 结论

历史离线归档、TDX 联网 raw bars、百度网盘基金 1m bars 和复权因子不应该对消费者暴露成多张可选表。**股票/可转债/ETF/LOF 日更行情由 TDX 在线下载负责；ETF/LOF 长历史 backfill 由百度网盘 1m 归档负责**；百度网盘股票/可转债 bars 只作为用户不定期维护的离线归档/长历史旁路。**CN-A 股票复权因子的活跃 authority 是固定 TDX XDXR V10（V9/V8 仅历史对照）；Sina 与百度股票因子只保留 retired audit。ETF/LOF 不由该股票合同静默授权，需独立后继合同。**

DataHub 的生产口径固定为：

1. **source 层**：每个来源保持不可变数据集，用于审计、回放和重建。
2. **canonical 层**：按 `market + frequency + price_space` 物化一张消费者表，行级唯一键包含 `instrument_type`。
3. **对外查询**：`/api/v1/history/bars` 优先读取 canonical dataset；只有没有 canonical dataset 时才兼容回退到最新 READY source dataset。
4. **覆盖结论**：任何“无 gap / 100%”表述必须先经过交易日历 + instrument snapshot + lifecycle / 停复牌 / 退市权威归因。原始 `max(trading_day)`、`VALIDATED` 或 `quality_score=100` 只能证明入湖质量，不能替代覆盖结论。

当前 raw canonical 命名：

```text
dataset_id      = bars_<market>_<frequency>_raw_canonical
dataset_version = bars_<market>_<frequency>_raw_canonical_<suffix>
path            = /datahub/lake/bars/dataset_version=<dataset_version>/bars.parquet
```

## 1.1 FactorLab Research Handoff

FactorLab 因子研究消费 bars 时必须先锁定版本，再取数。支持两种合规路径：

1. 小样本 / smoke：先用 `/api/v1/history/datasets?dataset_kind=bars&market=<market>&frequency=<freq>` 或 `/api/v1/history/datasets/{dataset_version}` 发现 READY 版本，再把 `dataset_version` 传给 `/api/v1/history/bars`。
2. 大样本 / 批量研究：先读取 dataset detail 中的 manifest、quality report、storage URI 和 dataset hash，再由 FactorLab 记录到 research input package。

指定 `dataset_version` 后，DataHub 必须 fail closed：版本不存在、不是 READY、不是 bars、market/frequency 不匹配，均不得回退 latest。这个约束用于防止同一研究 run 在不同时间读到不同 bars 版本。

## 2. 分层职责

| 层 | 例子 | 职责 | 是否给消费者直接用 |
|---|---|---|---|
| TDX 在线 source | `bars_cn_a_*` 或 TDX 命名数据集 | 股票/可转债/ETF/LOF 日常增量主路径：有界短增量、单点修复和目标日补齐；日更不得因新版本全量重扫 | 否 |
| 本地/百度归档 source | `bars_cn_a_1m_local_history_*`、`bars_cn_a_1m_baidu_netdisk_history_*` | ETF/LOF **长历史 backfill** 主源是百度 1m；股票/可转债场景仍是用户不定期维护的离线归档、长历史回填、TDX 无法覆盖后的审计/补缺旁路 | 否 |
| canonical raw | `bars_cn_a_1m_raw_canonical_*` | 去重、归一化、一张表对外 | 是 |
| 派生 adjusted | `*_qfq_canonical_*` / `*_hfq_canonical_*` | 研究用复权价格空间 | 是，但 CN-A 股票默认从 raw canonical + 固定 XDXR V10 派生（ETF/LOF 走 Sina affine 独立合同） |

## 3. 合并规则

- 主键：`market, instrument_type, symbol, timestamp`。
- 输出 schema：保持 `bars.v1` 并增加类型判别与分区字段：`symbol/market/instrument_type/timestamp/trading_day/trading_month/open/high/low/close/volume/amount/available_at/ingested_at/source_kind/dataset_version`。
- 输出 `dataset_version`：统一改写为 canonical dataset_version。
- provenance：`source_kind` 保留 winning row 的来源，例如 `local_archive_stock`、`local_archive_etf`、`tdx_remote`。
- 重复冲突：按 source priority 决定 winner；默认本地历史 `10` 优先于 TDX 增量 `20`。
- 同优先级 tie-break：`available_at DESC`、`ingested_at DESC`、`source_dataset_version ASC`。
- 不重叠区间：直接并入 canonical；股票/可转债/ETF/LOF 日常新交易日和目标日补齐优先由 TDX 在线下载负责。ETF/LOF 长历史分区由百度网盘 1m 归档重建，5m/15m/30m/60m/1d 由 1m 派生，并以 `baidu_netdisk_fund_1m_primary` source label 发布 canonical patch 覆盖对应长历史分区。百度网盘股票/可转债 bars 只在长历史回填、TDX 多轮修复仍无法覆盖、或审计任务中进入 source workset。
- validated TDX commit：TDX source 先落 `paths.history_staging_dir`，校验通过后 `PartitionedCanonicalPublisher` 只重写受影响 `instrument_type/trading_month` 分区，未影响分区必须 hardlink/reflink 复用；复用失败不得静默全量复制。
- 物理入湖契约：validated source 发布不是“只登记逻辑路径”。发布器必须先写同设备 staging，再以新 immutable `lake/bars/dataset_version=<canonical_version>/` 根目录原子 rename 成功；该目录内必须存在 parquet 数据文件、`manifest.json`、`quality_report.json` 与 `publish_receipt.json`。metadata 只允许在物理根目录完成后指向新的 READY canonical。
- 物理修复硬约束：不允许 metadata-only、query overlay、view、运行时 union 或 delta sidecar 被称为“已修复”。被 source 影响到的分区必须重写成新的 parquet 数据文件；未受影响分区可硬链接复用旧 immutable parquet，因为那些分区没有被本次修复改变。
- immutable 约束：不会原地覆盖旧 canonical 文件；“合入已有数据湖”指物理生成 successor canonical 根目录，受影响分区重写、未影响分区 hardlink 复用，然后 READY 指针前移。

该规则保证：

- 同一个 `market + instrument_type + symbol + timestamp` 只出现一条 bar；
- 股票/可转债/ETF/LOF TDX 日更、ETF/LOF 百度 1m 长历史 backfill、离线归档补缺和固定 XDXR V10 股票因子派生形成可追溯 raw/qfq/hfq canonical 序列；
- source 层仍可追溯，但消费者不再自行选择来源。

百度网盘基金 1m bars 归档是 ETF/LOF 长历史 backfill 主源，不是 daily completion 主源；百度网盘股票/可转债 bars 归档仍由用户不定期维护并作为旁路；百度网盘因子已退役为审计旁路。如果 AI 发现 bars 归档全面落后，必须提示用户更新；如果只是部分缺失，必须提示用户知悉，并把缺失写入报告，不得把网盘缺失解释为“不应有行情”或“元数据已确认”。旧网盘/Sina 股票因子缺失或落后只进入审计报告，不得影响固定 XDXR V10 股票产品的选择。

## 4. 运行入口

显式指定来源：

```bash
python scripts/materialize_canonical_bars.py \
  --frequency 1m \
  --input-dataset-version bars_cn_a_1m_local_history_20260504T000000Z_repaired:10 \
  --input-dataset-version bars_cn_a_1m_tdx_increment_20260504T153000Z:20
```

自动发现最近 READY source：

```bash
python scripts/materialize_canonical_bars.py --frequency 1m --auto-discover-sources
```

默认 live 路径：

```text
lake = .runtime/live/lake
meta = .runtime/live/meta/metadata.sqlite3
```

生产建议按频率依次执行：`1m,5m,15m,30m,60m`。每次物化都是新的 immutable dataset_version；不原地覆盖旧 canonical。

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

## 6. 复权关系

当前 canonical raw 是价格空间基准，但项目对外必须同时提供三套价格空间：

- `bars_cn_a_<frequency>_raw_canonical`：不复权事实源，保留 TDX/本地 source 原始 OHLCV。
- `bars_cn_a_<frequency>_qfq_canonical`：前复权 canonical，由 raw canonical + 本地 qfq `price_multiplier` 派生。
- `bars_cn_a_<frequency>_hfq_canonical`：后复权 canonical，由 raw canonical + 本地 hfq `price_multiplier` 派生。

派生公式固定为 `adjusted_ohlc = raw_ohlc * price_multiplier`；`volume`、`amount` 不复权。adjusted canonical 保持标准 bars schema，因子来源、factor dataset_version、carry-forward 策略和缺失因子计数写入 `quality_report.json.adjusted_bars`。

carry-forward 是允许的连续性降级，不是静默成功条件。若 qfq/hfq canonical 的 `time_range.end_time` 对应交易日晚于固定 XDXR 因子的 `factor_time_range.end_day`，`quality_report.json.adjusted_bars.factor_lag_alert.enabled` 必须为 `true`，并且对外汇报必须说明“bars 已推进但因子滞后，使用了 carry-forward”。本次 FactorLab 合同只授权到 2025-12-31，不使用其后降级行。

通达信 TQ 官方 `get_market_data` 暴露 `dividend_type=none/front/back`（不复权/前复权/后复权）。后续直接从 TDX 下载复权数据时，只能进入对应 raw/qfq/hfq 价格空间，不得覆盖 raw canonical；生产适配层通过 `tdx_dividend_type_for_adjustment(raw|qfq|hfq)` 固定映射。

### 6.1 TDX XDXR V10 固定权威口径（V9/V8 仅历史对照）

标准 TDX 7709 K 线链路仍只负责 raw bars，不得把 category=9 当前/后复权价格。
复权是独立的“XDXR 事件→每日累积 factor→raw OHLC 物化”链路。当前只授权精确 V10
版本和其物理 hash；V9（仅历史对照，仍是 FactorLab 2009—2025 固定合同钉死的因子父版本）与
V8（fenhong 每股/每10股换算错误、分红比例方向颠倒，仅作历史对照保留）不被任何生产路径引用。
其他 gBBQ/XDXR 实验版、段重刷脚本和历史迁移产物不会因此自动获得生产权限。
未来更换 factor 或 raw parent 时必须新建后继合同，不原地改变 V10 语义。

历史退役回执 `tdx_xdxr_retirement_20260521T062235Z` 仅用于解释旧版路由；
它不得覆盖当前直接 XDXR 事件派生的 V10 合同。

## 7. 质量与审计

`quality_report.json` 增加 `canonical_bars` 段：

- `rule_version`；
- `merge_key`；
- source priority；
- source row counts；
- winner row counts；
- duplicate count；
- instrument_type row counts；
- duplicate/conflict count；
- ambiguous symbol count；
- coverage dataset_version；
- consumer contract。
- `physical_publish`：物理入湖 receipt，包含 `commit_operation=write_staging_then_atomic_directory_rename`、`dataset_root`、`staging_root`、parquet 文件数、分区数、影响分区数、复用分区数、source / previous dataset_version。

SQLite `dataset_versions` 注册 canonical dataset_id，API 因此能稳定优先 canonical。

`publish_receipt.json` 是物理提交旁证。排查“是否真的入湖”时，先看：

1. `dataset_versions.storage_uri` 指向的 `lake/bars/dataset_version=.../` 是否存在；
2. 该目录是否含 parquet 数据文件和 sidecars；
3. `publish_receipt.json.dataset_root` 是否等于该物理目录；
4. `quality_report.json.canonical_bars.physical_publish` 是否与 receipt 一致。
5. `publish_receipt.json.physical_repair_contract.metadata_pointer_only_allowed=false`；
6. `publish_receipt.json.physical_repair_contract.query_overlay_allowed=false`；
7. `publish_receipt.json.physical_repair_contract.affected_partitions_must_be_rewritten=true`；
8. `publish_receipt.json.affected_parquet_file_count > 0`。

如果只能在查询层 union 到新增 source，而没有新的 canonical dataset root 与受影响分区 parquet 文件，则不算 validated commit，也不算数据湖修复。

## 7.1 日线无 gap 的权威判断步骤

日线 `1d` 当前不走分钟 coverage index 的 `SUPPORTED_BAR_FREQUENCIES`，因此不能用分钟 coverage 的空结果判断“无 gap”。日线必须使用目标日权威验证：

```bash
python scripts/verify_daily_lake_authority.py \
  --dataset-version bars_cn_a_1d_raw_canonical_scrub_2a29a9d7d379 \
  --target-day 2026-04-30
```

默认 `--scope range`，含义是“从每个品种权威上市日起，到 `--target-day` 的每个交易日”。如只需要单日截面，必须显式传 `--scope target-day`。

该脚本按以下顺序出结论：

1. 读取最新或指定 `instrument snapshot`，确定 stock / ETF / LOF / 可转债目标 universe；
2. 为每个 symbol 找权威 `listed` 日期，构造上市日起到目标日的交易日区间；
3. 扫描指定 `1d` canonical 物理 parquet；
4. 对区间内缺 bar 的 symbol/day 调用 lifecycle / 停复牌 / 退市权威归因；
5. 只有 `true_gap_day_count=0` 且 `metadata_missing_symbol_count=0` 时，才允许说“经权威归因后 100% / 无 gap”。

任何未跑该步骤的“无 gap”表述都只是原始观测，不是本仓权威结论。

## 8. 验证入口

```bash
python -m py_compile \
  src/datahub/core/services/history/canonical_bars_materializer.py \
  src/datahub/core/services/history/partitioned_canonical_publisher.py \
  src/datahub/storage/query/bars_query.py \
  src/datahub/core/services/history/bar_coverage_index.py \
  src/datahub/storage/repositories/dataset_versions.py \
  scripts/materialize_canonical_bars.py \
  scripts/verify_daily_lake_authority.py \
  scripts/bar_coverage.py
pytest -q tests/unit/history/test_canonical_bars_materializer.py
pytest -q tests/unit/scripts/test_verify_daily_lake_authority.py
pytest -q tests/unit/history/test_bar_coverage_index.py
python scripts/verify_module_routing.py --mode workspace --repo-root . --workspace-docs docs --check dependencies
```
