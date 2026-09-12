# 本地模型交接

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

目标仓库：staryocean0/factorlab-trend-reversion-regime-lab。先保护未提交修改，安全fetch/fast-forward main，再读 [CONTINUE_HERE](CONTINUE_HERE.md)。

当前没有新的数据搬运或研究执行任务。五年ETF分钟CSV、上游说明、2025-12-01六个文件均已交付并经云端检查。不要再次运行已完成交付指令，不需要重试完整clone来证明现有文件存在。

本地默认任务仅为同步或维护；需要新增材料时，必须有新任务写明确切字段/日期/权限。不能采购、猜单位、平移时钟、重开R1_A或改旧结果。非公开文件和凭据不进公共Git。

启动：`bash .codex/cloud_setup.sh`。完整测试见 [测试说明](docs/TESTING.md)，默认环境安装不再调用已退役的validate_seed.py。
