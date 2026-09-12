# 从这里接管

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

最近完成的是2025-12-01字段对账和受限读取层，不是新收益实验。本次整理仅修复组件同步与运行入口。

先读 [当前白皮书](docs/WHITEPAPER.md)、[最新来源对账](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)、[组件生命周期](docs/COMPONENTS.md)。

现有五年分钟包、上游说明和六个单日Parquet已经交付，不再索取相同材料。已知份额合并遗漏已修正且旧样本/均值不受影响，不重复该任务。不同产品的同步、单位和原生分钟生成语义仍有限制；不得拟合时移或补造字段让数据通过。

没有正在等待执行的金融实验。下一项实证须由用户另行授权，先明确问题和数据假设。本仓维护、合成测试、保留证据核对不构成重开R1_A或旧期权身份。

修改当前状态时只编辑 [状态源](docs/REPOSITORY_STATE.json)，再运行 `python scripts/repository_consistency.py --render` 和 `--check`。不要分别手改多个入口。历史研究报告、冻结文件和原始数据保持原路径与原字节。
