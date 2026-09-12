# 当前数据用途与来源边界

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](REPOSITORY_STATE.json) · [最新研究解释](research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

现有数据均用于历史研究或来源检查；数据可读、hash一致与金融语义完整是不同验收层。旧manifest按原字节保留，里面的complete=true或shares只代表当时声明，不自动准入新研究。

| 数据组 | 路径 | 当前用途 |
|---|---|---|
| 固定指数历史包 | `data/market/`、`data/manifest.json` | 按原合同读取与历史复现；补齐及available_at含义须分来源 |
| 已关闭MO研究包 | `data/r1b_research/` | 保留旧结果/依赖核验，不重开期权 |
| ETF历史分钟包 | `data/r1a_carrier_prices/cloud_pack_v1/` | 旧价格层研究复现；原生分桶、部分数量单位、完整行动表不视为已认证 |
| 已知行动修正版 | `data/etf_source_actions_v2/` | 已核实行动overlay，不是全历史完整性证明 |
| 上游文档/代码/固定样例 | `data/etf_upstream_evidence_v1/` | 固定来源解释，副本不是独立供应商认证 |
| 单日高频研究产品 | `data/etf_microstructure_sample_20251201_v1/` | 2025-12-01来源标签层核对，非实时/PIT或净值认证 |

指数amount/volume不得超出已核实源定义解释为统一交易量；指数观察分钟available_at为生产者日终赋值，填行是标签值，ETF归档是后来入库时刻，不能混作同一实时过滤字段。旧指数读取时间映射保持不变，不把上游知识时刻改成市场时刻。

512100已知2022-09-02合并及停牌、09-05复牌已登记，新/旧份额0.36555；2022-08-03取消提案不执行。该遗漏对旧已发表样本/均值无影响的审计已完成。588000空行动表不等于完整无事件证明。

单日报价末行两条倒置区间仍在原文件，只由受限消费者拒绝；全日数量相等不推出日内统一时钟。历史材料、元数据中的2026时间不等于已打开新确认行情；不得自动扩大日期。

数据原始文件、旧清单和供应商说明不由本次整理改写。完整性以当前用途说明和裁决为准，不以文件名或单个布尔值为准。
