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

先读 [当前组件白皮书](docs/WHITEPAPER.md) 与 [执行路线图](docs/ROADMAP.md)，再读 [最新来源对账](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)、[组件生命周期](docs/COMPONENTS.md)。

## 唯一下一步：M1 接口合同审计

下一次会话只推进路线图 **M1**：参考 `staryocean0/factorlab-star50-filter-lab` 的风险识别 consumer / as-of / schema / availability 范式，核查本仓现有代码并形成 `docs/API_CONTRACT.md` 与 gap list。

M1 **只定义调用合同，不修改状态算法，不跑五桶收益/持续性实验，不提前实现 M2–M9**。完成 M1 Gate 后再进入 M2。

最近完成的历史工作仍是 2025-12-01 字段对账和受限读取层，不是新收益实验。现有五年分钟包、上游说明和六个单日 Parquet 已经交付，不再索取相同材料。已知份额合并遗漏已修正且旧样本/均值不受影响，不重复该任务。不同产品的同步、单位和原生分钟生成语义仍有限制；不得拟合时移或补造字段让数据通过。

当前没有已启动的新金融实证。路线图规定未来研究顺序，但不会把尚未执行的 M4/M5 自动写成已验证证据。历史研究报告、冻结文件和原始数据保持原路径与原字节。

修改当前证据状态时只编辑 [状态源](docs/REPOSITORY_STATE.json)，再运行 `python scripts/repository_consistency.py --render` 和 `--check`。不要分别手改生成状态块。
