# 当前研究与工程白皮书

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](REPOSITORY_STATE.json) · [最新研究解释](research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 目的与证据边界

本仓研究中证1000与科创50的趋势反转、均值回归及相关价格观测问题。指数价格反应、相对匹配对照的增量、模型预测评分、来源审计和交易执行是不同问题，不能混写为一个PASS。

R1_A历史价格线索与后续统计/预测局限均保留；当前版本已阶段性收口并储备。新ETF—指数方向完成可测量性和单日字段对账，尚不能把跨产品标签差异解释为可交易修复。当前没有批准的新实证候选。

## 当前代码承担什么

`src/regime_lab/market_data.py`是固定指数包读取器；`src/factor_lab`和`shared`是裁剪后的支持模块，不是完整FactorLab。`research/etf_day_reconciliation/audit.py`保留单日对账和RestrictedSourceView。其他研究模块均按[组件索引](COMPONENTS.md)保留用于已固定历史复现或来源追溯，旧数据采集工具已退役为参考代码。

读取视图拒绝倒置/空/未知结束区间、未来初始化、跨会话延续及无效最新状态后退用旧值；只在消费视图裁剪阶段终点，不改变原始价格。它使用离线valid_until，不证明实时可知或完整快照。

## 数据和可作结论

旧分钟、逐笔、报价、指数3秒的量纲和时间含义按各自来源合同解释。旧Z墙钟例外不泛化为所有字段。日终总量一致不能证明日内同步；四种分桶不能完整复原旧OHLC也不能以优化平移补齐证据。IOPV为零不能计算真实净值折溢价。详见[数据说明](DATA.md)。

## 维护规范

[状态源](REPOSITORY_STATE.json)同步生成入口与本白皮书状态块；[测试说明](TESTING.md)定义执行层级。业务状态变更必须同步裁决、模块和测试，不通过改历史报告假装过去已知当前结论。

历史白皮书和报告作为冻结研究快照保留原字节：[历史资料索引](research/README.md)、[归档索引](archive/README.md)。源数据附带白皮书是上游文档，不是本项目当前策略白皮书。

新研究须明确研究对象、数据角色、缺失处理、停止条件和授权；本维护不新增模型、参数、研究收益或2026行情读取。
