# 本地执行模型接管提示 — 已交付数据后的审计

仓库：`staryocean0/factorlab-trend-reversion-regime-lab`。先读 `CONTINUE_HERE.md`，检查本地未提交改动后安全 fetch/fast-forward main，不覆盖用户工作。

## 已完成，不要重复

用户提交 `b656b4b` 已导出两只 ETF 的本地 DataHub 历史并推送清单与结果。现在不是“从头找 ETF 数据”。

- `588000.SH` 已本地 admission PASS 并完成描述性回放：1,791/1,802 组、12,537 行。云端已核验结果 hashes、原始配对、七周期、2,128 个汇总字段，并用原指数分钟 bytes 独立重算指数对照，均一致。
- `512100.SH` 已本地导出，但 2021 正成交量分钟覆盖率 94.478738% 低于冻结的 95%；没有打开其收益。
- 总状态 `PARTIAL_CARRIER_TRANSPORT`，不是全部成功、全部失败或两只都没数据。
- 原始 ETF CSV 和除权除息文件留在 Git-ignored `data/r1a_carrier_prices/private/`；不要误说已上传云端原始行情。

## 下一项任务：源数据与2021覆盖率审计

使用已经存在、合法可访问的本地 DataHub 原始分区和导出文件，不购买、不借 token，不请求事件条件化数据，不重跑或优化收益。

输出 public-safe 审计回执，优先解决 `512100` 的2021年：按月/年分别列出指数应有分钟数、原源行数、导出行数、缺失时间戳数、零成交量数、异常价格行数、时段/窗口过滤数、时间标签不一致数、重复时间戳数和冲突重复数。各类口径须说明是否互斥并核对总数。

核实零成交量到底是真实无成交、源数据占位约定还是采集问题。必要时用已有权限的独立来源仅核查这些数据语义/成交事实，不读取策略收益来挑修复方式。真实无成交不能补价或伪造为正成交量，也不能自动降低95%、删除2021或换ETF。若确为真实覆盖不足，保留本冻结下的INSUFFICIENT。

另外补齐：

1. 原始分区/导出的 SHA256、字节数和行数，以及支撑 `session_end_label_v2` 和 `Z`后缀实际表示上海墙钟时间的上游字典/转换链。不能仅凭收益相关性选择平移。
2. 现有 `export_datahub_lake.py` 的 keep-last 去重前后计数及冲突样本摘要。云端看到代码会去重，但无法判断本交付实际是否发生冲突；不要凭空推定有或没有。
3. 完整分红/拆分源的快照hash或来源回执，说明2021-2025覆盖范围，并为588000空事件表提供完整性证据。

只提交可公开的审计数字、hash、schema和证据说明；不公开付费原始数据、凭据、账号、非公开下载地址。源数据真实性审计与已完成的公开账本算术审计是不同层次。

## 发现实际缺陷时

先固定具体事实与更正版本，保留所有旧manifest/receipt。只更正已被证据确认的数据或映射错误；不改信号、配对、horizon、年份、侧别、成本或门槛。更正后按原协议用新的输出目录回放，禁止覆盖历史输出。仅补文档不需要重跑收益。

## 复核命令

```bash
PYTHONPATH=src:. python research/r1a_carrier_transport/audit_public_delivery.py --output /tmp/r1a-public-audit-new
```

有完整manifest引用原始文件时的原协议回放命令：

```bash
PYTHONPATH=src:. python research/r1a_carrier_transport/transport.py --output /tmp/r1a-transport-new-version
```

全报 `1/5/15/30/60/120/240` 根指数观察bar，event和原matched-control保持不变。synthetic SHORT与零成本价格收益不是可实盘盈利。588000只是科创50次载体，不能替代中证1000主检验。

`BLACKBOX_query_count=3`，禁止query#4；`production_authority=false`；`fresh_oos=false`。R1_B/R2及旧期权身份均不重开。
