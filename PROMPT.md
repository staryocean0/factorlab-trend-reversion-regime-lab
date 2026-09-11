# 本地执行模型接管提示

接管 `staryocean0/factorlab-trend-reversion-regime-lab`。先读 `CONTINUE_HERE.md` 和 `research/r1a_carrier_transport/README.md`。检查本地未提交改动，安全地 fetch/fast-forward main，不覆盖用户工作。

## 当前停点

R1_A 的 ETF 价格回放已经冻结、实现并完成云端工程核验，但没有真实 ETF 交付数据：

`BLOCKED_CARRIER_DATA_NOT_ADMITTED`

`ETF_outcomes_read=false`

这不是 ETF 策略失败，也不是 ETF 验证通过。不要重新设计信号、改持有期或再研究期权。

## 直接执行的数据任务

从现有、本来就有权访问的 DataHub、行情终端或正式历史数据接口，查找并导出以下完整历史：

- 主载体 `512100.SH`，对应中证1000 `000852.SH`；
- 次载体 `588000.SH`，对应科创50 `000688.SH`；
- 时间都是 `2021-01-01 .. 2025-12-31`；
- 1分钟、真实未复权 OHLCV；
- 完整时间戳/标签/时区/成交量字典；
- 同期完整分红、拆分除权除息日期及来源。

请求完整非事件条件化数据，不只下载信号日期。不要用日线、5分钟插值、最近5个交易日、指数改名或合成价格替代。Tushare 当前对应接口是 `etf_mins`，但需要既有权限；不得购买、借用他人 token 或绕过权限。找不到合法访问方式就保留精确 blocker，不伪造数据。

保存原始 bytes、SHA256、字节数、行数和真实来源。付费或非公开文件默认放 `data/r1a_carrier_prices/private/`，禁止提交公共 Git；没有再分发授权不得为了云端方便公开原包。账号、token、非公开下载地址不得出现在公开回执里。

按 README 的 schema 建立每只 ETF 的 manifest：

`data/r1a_carrier_prices/512100.SH.json`

`data/r1a_carrier_prices/588000.SH.json`

只有来源证据齐全时才填写 research_use_authorized/corporate_actions_complete=true。不要猜 bar 是开始标签还是结束标签，更不能用最高相关性来选择时间平移。实际原始格式需要转换时，先冻结来源映射、补测试，再转换。

## 实际回放命令

```bash
PYTHONPATH=src:. python -m pytest -q tests/test_r1a_carrier_transport.py
PYTHONPATH=src:. python research/r1a_carrier_transport/transport.py --output /tmp/r1a-new-delivery
```

每次交付版本使用新的输出目录，不覆盖 `docs/ops/evidence/r1a_carrier_transport_20260912/` 的历史阻塞回执。

已冻结的 1,296 组 CSI1000 和 1,802 组 STAR50 R1_A 事件/对照原样使用，不重算信号、不重新匹配。ETF 必须精确匹配指数时钟；不能缺一分钟就顺延。全报 `1/5/15/30/60/120/240` 根指数观察 bar，不从结果选 15 或30。事件和对照必须一起覆盖，并和同一入选样本的指数收益对比。

先做零成本、synthetic LONG/SHORT 的价格层，不涉及真实可空性、保证金、手续费或期权。跨分红拆分、缺分钟、零成交量按冻结规则明确处理，不能改规则凑通过率。

## 完成时交付

实际取得文件及 hash、数据准入结果、有效配对覆盖率和剔除原因、完整七周期 ETF/指数/增量对照表、测试结果、commit SHA、仍缺的外部材料。数据不足就汇报 BLOCKED/INSUFFICIENT，不能记作策略 FAIL 或 PASS。只提交获准公开的证据，并同步 CONTINUE_HERE。

R1_B、R2、旧期权和其他已关闭身份不重开。既有指数证据是条件于匹配设计的历史观察，不是新的独立 OOS 或因果证明。`BLACKBOX_query_count=3` 不变，禁止 query #4，`production_authority=false`。
