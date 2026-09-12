# 当前云端与本地协作

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](REPOSITORY_STATE.json) · [最新研究解释](research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

云端可直接读取本仓既有指数、ETF分钟及单日高频文件并运行授权的核验。不是“研究启动包”，也不再禁止使用已配置GitHub Actions进行有范围的复现。

本地负责仅本地可得且已获准交付的原材料；云端负责独立核验和研究判断。完整clone失败不是已交付文件失效，固定提交窄检出和实际hash可作为文件交付核验。

当前没有新增本地搬运任务。已完成的两份任务保留为[来源交付历史](ops/ETF_UPSTREAM_SEMANTICS_HANDOFF_20260912.md)和[单日交付历史](ops/ETF_ONE_DAY_SOURCE_DELIVERY_20251201.md)，不可再次派发。

确需新材料时另写精确日期、字段、来源权限及验收标准；不要要求整个DataHub，不上传凭据或未经准许公开的原包，不把本地报告当独立核验。
