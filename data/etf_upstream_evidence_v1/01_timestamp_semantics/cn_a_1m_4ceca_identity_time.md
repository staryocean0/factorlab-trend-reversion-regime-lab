# 固定 CN-A 1m 版本的身份与时间合同

适用固定版本 `bars_cn_a_1m_raw_canonical_4ceca170a851` 的股票、ETF、LOF、可转债及已核验的 TDX、百度和本地归档生产路径。未识别的新来源和其他产品不自动继承本合同。

| 字段/读取层 | 解释 |
|---|---|
| 目录、catalog、API信封的 `dataset_version` | 固定容器身份；查询和复现使用此pin |
| Parquet关闭Hive后的嵌入 `dataset_version` | 分区最后物理写入代次；硬链接复用允许其早于容器版本 |
| `BarsQuery`返回的行级 `dataset_version` | Hive目录值覆盖同名列，通常与信封一致；不能以它证明磁盘嵌入值相同 |
| bar `timestamp`、`trading_day` | 交易所本地会话标签；`Z`是既有序列化载体，不能直接当UTC瞬间 |
| `available_at`、`ingested_at` | 各生产者的知识/导入时间通道；本轮受证归档路径由UTC导入参数生成，不套用bar标签解释 |

完整860文件footer已核验。只有本代重写的`lof/2026-08`嵌入版本等于容器，其余859文件复用前代，与发布回执一致。股票2026-05的嵌入代次仍为`6e2ae97df9c4`；ETF/LOF/可转债有各自代次，不能因同一容器就改写成一个来源版本。嵌入代次也不等同于最初vendor来源，来源追溯仍结合`source_kind`及发布/父manifest。

查询和导出保留标签。例如`2026-05-08T13:21:00Z`表示上海下午13:21；显式生成UTC瞬间时为`2026-05-08T05:21:00Z`，该UTC字符串不能直接替代原标签查询条件。交易日按本地标签日界解释。固定pin的物理查询绕过未固定版本的派生缓存；其他派生产品必须遵守自己的source snapshot合同，不得从本pin结论继承缓存授权。

本地归档导入器、权威湖重建器及TDX转换器已用真实函数回放；百度源合同明确沿用本地墙钟加Z。接受的naive本地源以及Shanghai-aware输入与任意UTC-aware输入须分开，后者不属于本合同核定输入，不可因同为timestamp类型就扩大支持。ISO-Z原始字符串在已测归档入口被拒绝。当前源码相关函数与执行者所用版本的AST一致，并在主仓再次回放。

[主控验收](../../../evidence/market_rules/cn_a_stock_trading_rules.v1/composer_m7_primary_20260909/PRIMARY_ACCEPTANCE.md)包含全footer矩阵、父回执、源码指纹、真实查询/生产者测试。此次完成字段身份与消费解释，不证明所有原始vendor字节、历史首收PIT、数据覆盖或外部客户端实现；这些能力按独立来源与消费者合同核验。未修改湖值或serving指针。
