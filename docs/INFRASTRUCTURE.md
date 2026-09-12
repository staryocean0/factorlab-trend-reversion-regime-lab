# 当前代码与运行环境

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](REPOSITORY_STATE.json) · [最新研究解释](research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

Python支持范围以[pyproject.toml](../pyproject.toml)为准。包装版本不是策略成熟度。[当前支持模块清单](infrastructure_manifest.json)仅列实际存在的文件；旧导入时清单已经归档，不再宣称不存在的standard_backtest_service可导入。

`src/regime_lab`提供市场包读取与发布检查；`src/factor_lab`、`shared`为裁剪后的支持库；`research/`按[生命周期索引](COMPONENTS.md)保留。历史算法模块与归档源码仍被固定研究导入，不能为了目录好看破坏导入闭包。

[云端初始化](../.codex/cloud_setup.sh)安装依赖并运行结构门禁，不调用已移走的seed验证器，不自动重新训练历史预测器。[统一一致性检查](../scripts/repository_consistency.py)检查状态块、文件角色、路径、导入、测试和工作流。

完整研究回归和冻结复现见[TESTING](TESTING.md)。工程验收不授予数据源真实性、实时撮合或策略生产资格。
