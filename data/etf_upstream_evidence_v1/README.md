# ETF 上游证据包 v1

只补云端缺少的上游材料。不重传五年 ETF 分钟 CSV，不重复份额合并修复，不做策略/回测，不重开 R1_A，不改原行情/信号/配对/结果/阈值。

| 目录 | 内容 |
|---|---|
| `01_timestamp_semantics/` | 白皮书全文+§5 摘录、`session_offset_contract.py` 全文与 1m/分桶摘录、4ceca 时间身份卡、导出解码摘录 |
| `02_raw_anomaly_samples/` | 冻结 20 行对应的 4ceca 原字段（含 amount）与 Baidu 1m 史源对照；导入/导出代码；单位与止层 |
| `03_index_processing/` | `causal_flat_fill` / `available_at` 生成代码摘录；3s 输入与 1m 观察/填行样例 |
| `04_corporate_actions/` | overlay 副本、NAV 事件行、Sina 因子行、覆盖与 UNKNOWN |
| `05_microstructure_inventory/` | 买一卖一/成交/指数发布：字段、频率、覆盖、访问方式 |

每项出处、commit、SHA256 见 `manifest.json`。摘录文件头标注原路径和行号。

公开仓只含合同、摘录、样例和索引。供应商整包 zip 本地未找到，故**没有私有附件包**。材料不含账号、token、cookie。
