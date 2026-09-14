# 从这里接管

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 当前产品口径

本仓未来工程定位已经校正为：**供策略调用的趋势状态识别组件**，不是独立交易策略，不直接输出买卖、仓位、订单或 Layer 4 指令。状态必须绑定 K 线级别/配置；三桶是基线，五桶“极端斜率可能更易耗竭”只是待验证假设。

先读 [当前组件白皮书](docs/WHITEPAPER.md)、[执行路线图](docs/ROADMAP.md)、[M1 API 合同](docs/API_CONTRACT.md) 与 [M1 Gap 审计](docs/API_GAP_ANALYSIS.md)，再读 [最新来源对账](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)、[组件生命周期](docs/COMPONENTS.md)。

## 已完成：M1 接口合同审计

M1 已核查本仓 `src/factor_lab/market_state/timing_layer2_measurement_plane.py` 与风险识别参考 consumer。

已确认：

- 现有 Layer 2 measurement plane 已有 measurement-only authority，并明确拒绝 strategy selection、parameter selection、routing、production authority；
- 当前真正缺的不是另一套 Layer 2，而是 measurement plane 上方稳定的 current-state snapshot / as-of consumer；
- `docs/API_CONTRACT.md` 已冻结 `regime_state_consumer_v1` 的调用边界、clock、availability、no-fallback、snapshot/provenance 与参数所有权；
- `docs/API_GAP_ANALYSIS.md` 已把当前实现到目标 consumer 的缺口分配给 M2–M9；
- capability registry 中存在当前裁剪 checkout 未物化的历史 `source_refs`，因此“注册过的 asset”不得直接等同于“当前可调用 provider”，未来必须 admission/fail-closed。

M1 **没有**修改状态算法、没有选择最终 slope 公式、没有调整 `T1/T2`、没有启动五桶实验，也没有授予 production authority。

## 唯一下一步：M2 三桶基线冻结与可复现性

下一次会话只推进路线图 **M2**。

M2 必须先审计当前已有趋势/方向原语（尤其 `core_kline_attribute_pool.py` 的 signed OLS、signed efficiency、direction-continuity 类测量），然后冻结一个可复现的三桶 authority：

1. 斜率/趋势强度的数学定义与价格变换；
2. lookback/window；
3. K 线完成规则与缺失处理；
4. normalization；
5. 横盘阈值 `T1` 的定义/尺度；
6. causality / as-of 约束；
7. 回归样例与前缀一致性验证方案。

M2 Gate：给定同一输入、同一配置、同一 `as_of`，`DOWN / SIDEWAYS / UP` 结果必须可重复且无未来信息泄漏。

**M2 不进入多周期 profile（M3），不设计 `T2` 实验（M4），不运行五桶实证（M5）。**

最近完成的历史工作仍是 2025-12-01 字段对账和受限读取层，不是新收益实验。现有五年分钟包、上游说明和六个单日 Parquet 已经交付，不再索取相同材料。已知份额合并遗漏已修正且旧样本/均值不受影响，不重复该任务。不同产品的同步、单位和原生分钟生成语义仍有限制；不得拟合时移或补造字段让数据通过。

当前没有已启动的新金融实证。路线图规定未来研究顺序，但不会把尚未执行的 M4/M5 自动写成已验证证据。历史研究报告、冻结文件和原始数据保持原路径与原字节。

修改当前证据状态时只编辑 [状态源](docs/REPOSITORY_STATE.json)，再运行 `python scripts/repository_consistency.py --render` 和 `--check`。不要分别手改生成状态块。
