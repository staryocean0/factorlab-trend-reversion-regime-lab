# M5-1 Source / Profile Admission Receipt

> 状态：**M5-1 admission audit 完成；M5 整体尚未完成。**
>
> 本文只做 source/profile 准入与时钟语义封存，没有计算五桶 episode 数、forward return、survival、transition、reversal、MFE/MAE，也没有读取 Validation/Holdout outcome。机器合同见 [`TREND_M5_SOURCE_PROFILE_ADMISSION_V1.json`](TREND_M5_SOURCE_PROFILE_ADMISSION_V1.json)。

## 1. 准入原则

严格执行 M4：只有同时具备 **exact M3 Layer-1 view identity + causal clock semantics + current source receipt + 覆盖冻结样本窗口** 的 profile 才能进入 M5 后续计算。

本轮禁止：

- 用 1m 在 FactorLab 本地重采样 15m/60m；
- 用另一个 offset 替代冻结 anchor；
- 因文件“还存在”就把 legacy 数据提升为 current research input；
- 读取任何 Validation/Holdout 五桶结果。

## 2. 当前 active source authority

当前可用的跨指数 active minute catalog 来自 `staryocean0/factorlab-star50-filter-lab`：

- active manifest：`data/cross_index_risk_gate_v1/manifest.json`
- DataHub export：`factorlab_unified_index_kline_v3_20260824`
- export manifest SHA256：`c46f2da6c3df016ca054e183e37267dc472097450fcdd6644c22aa0084c15749`
- 两个载体：`000852.SH`、`000688.SH`
- 当前 active catalog 明确包含 1m 与 5m；其 5m 来源明确是 `5m_offset_0.parquet`。

趋势仓 `data/market/1m` 与 `data/market/5m` 是该 cross-index archive 的受限历史副本，`data/manifest.json` 保存逐年 hash/source path；它们仍然是 `fresh_oos=false` 的历史材料，本轮不会因此升级科学 authority。

## 3. 历史 `available_at` 的处理

M5 不把归档文件中的历史 retrieval `available_at` 当作盘中 bar 的真实接收延迟。

依据数据所有者已经冻结的澄清：

- 历史 `available_at` 表示“作为历史数据可被获取的时间”；
- 盘中实时数据的获取是实时的；
- 历史 retrieval timestamp 不能替代 decision-time bar visibility。

因此 M5 causal replay 的时钟适配冻结为：

```text
bar_end = exact export-view timestamp（按 Shanghai wall-clock contract 解释）
runtime_available_at = bar_end
raw historical available_at = provenance only
```

这表示“完成 bar 在 bar close 后可用于因果研究”的研究时钟合同，**不声称测得了真实 feed latency**。

## 4. Anchor admission 结果

M4 预注册 4 个 anchor interval × 2 carriers，共 8 个 carrier/profile pairs。

| carrier | profile | view | status | 说明 |
|---|---|---|---|---|
| `000852.SH` | `trend_1m_official_v1` | `1m_official` | **ADMITTED** | active cross-index archive，exact V3 view，完整覆盖冻结窗口 |
| `000852.SH` | `trend_5m_offset0_v1` | `5m_offset_0` | **ADMITTED** | active cross-index archive明确来自 `5m_offset_0.parquet`，完整覆盖冻结窗口 |
| `000852.SH` | `trend_15m_offset5_v1` | `15m_offset_5` | **NOT_ADMITTED** | exact shipped CSI1000 legacy/two-wave rows只到 2020-12-31；无 current active 2020–2025 exact receipt |
| `000852.SH` | `trend_60m_offset30_v1` | `60m_offset_30` | **NOT_ADMITTED** | 同上 |
| `000688.SH` | `trend_1m_official_v1` | `1m_official` | **ADMITTED** | active cross-index archive，exact V3 view，2020-07-23 起完整覆盖 |
| `000688.SH` | `trend_5m_offset0_v1` | `5m_offset_0` | **ADMITTED** | active cross-index archive，exact V3 view，2020-07-23 起完整覆盖 |
| `000688.SH` | `trend_15m_offset5_v1` | `15m_offset_5` | **NOT_ADMITTED** | exact legacy file存在，但 source repo 明确声明 legacy `development/` 不是 current research input |
| `000688.SH` | `trend_60m_offset30_v1` | `60m_offset_30` | **NOT_ADMITTED** | 同上 |

结论：**当前允许进入 M5-2 的主 interval 只有 `1m` 与 `5m`。** 15m/60m 不是“效果差”，而是 source/profile admission 尚未成立；本轮没有计算它们的任何市场结果。

## 5. Phase sensitivity admission

当前 active cross-index catalog 的 5m 是 `5m_offset_0`，不是 offset1–4。15m/60m 也没有 current active exact-view receipt。因此 M4 的 6 个 phase-sensitivity profiles 本轮全部保持 `NOT_ADMITTED`。

Legacy STAR50 manifest 虽保留完整 1m/5m/15m/60m view files；two-wave repo 也保留 CSI1000 exact multi-view development files，但：

- STAR50 source repo 明确说 legacy `development/` 不是当前 research input；
- two-wave shipped exact CSI1000 rows截止 2020-12-31，且其后外部 temporal evidence 已被消费、raw rows未随仓库提供，不能拿来补本协议的 2021–2025 source receipt。

所以这些材料只作为 provenance/reference，**没有被本轮提升为 M5 active source。**

## 6. 对 M4 primary family 的影响

M4 的 planned primary family 仍然保持原样，协议不修改：4 anchor intervals × 2 directions。

M5-1 不删除未准入 hypothesis，也不重新分配研究范围。15m/60m 如果在后续仍拿不到合规 source receipt，就继续按 M4 的 fail-closed 规则保持不可检验；不得通过换 profile、合并 carrier 或本地重采样来补齐。

## 7. M5-1 Gate

**PASS（admission audit complete, partial profile admission）。**

通过的含义是：

- 8 个 anchor carrier/profile pair 已全部得到明确的 `ADMITTED / NOT_ADMITTED` 裁决；
- `1m/5m` exact source lineage、覆盖与 causal clock adapter 已封存；
- `15m/60m` 因缺少 current active exact-view receipt 而 fail closed；
- 无 local resampling / profile substitution；
- 无五桶 outcome 被计算；
- Validation 与 Holdout 仍锁定。

## 8. 唯一下一步

下一轮只能进入 **M5-2：Development pipeline + sample-adequacy checks**，而且仅针对已经 admitted 的 `1m/5m` anchor。

M5-2 可以按 M4 计算 Development 中的管线完整性与样本充足性，但仍不得读取 Validation outcome。只有 Development code/config/receipt 完成封存后，才可能进入后续一次性的 Validation 阶段。
