# 云端研究接管提示 — R1_A 端点价格诊断已完成

仓库：staryocean0/factorlab-trend-reversion-regime-lab。先读取 CONTINUE_HERE.md 和 docs/research/R1A_ENDPOINT_METHOD_REVIEW_20260912.md，再安全同步主干，不覆盖用户工作。

## 当前不是数据搬运任务

实际 ETF CSV 已在 data/r1a_carrier_prices/cloud_pack_v1/。无需本地 DataHub 或 private/；不要再让用户搬同一批数据。

新完成状态：ENDPOINT_DIAGNOSTIC_COMPLETE_DESCRIPTIVE。两只 ETF、七个固定周期，共14个逐周期端点诊断都已测算。旧全路径 v1 仍按自己的定义保留 PARTIAL_CARRIER_TRANSPORT，不能覆盖或改写它。

## 已经做完的事

独立冻结的端点诊断只使用原事件及对照的四个必要价格端点；每个端点必须精确对齐指数时钟、正价格、正成交量。中间无成交不用于否定端点收益，但本研究也不据此声称完整路径风险可观测。

中证1000 ETF：15/30 bar 事件均值 +5.007/+7.739bp，增量 +4.368/+7.074bp，同样本指数增量 +3.894/+6.527bp；LONG/SHORT增量都正，年度增量分别4/5、5/5为正。未选持有期，也未做新增显著性检验。

主载体每周期覆盖97.15%-98.07%，但七周期共同样本的2021覆盖仅60.22%，未过共同样本门槛，其ETF收益表没有打开。不能假装七行来自完全相同的样本。

科创50ETF逐周期和共同样本诊断均有结果；短周期增量为正，但年度一致性更弱，不构成中证1000的独立确认。

## 下一研究重点

在不改信号、原配对、载体或七周期的前提下，审查重叠收益窗口、重复使用的对照、日期相关、历史重复研究和观测选择对结论的影响。任何新增推断应先单独冻结，再执行；不要因为有多个数学方案就重新把整条研究从头设计一遍。

当前是条件于未来退出时点可观测性的历史描述，不是可执行的入场过滤器；高覆盖率也不证明缺失随机。完整ETF缺失结果仍未知。先解决统计稳健性，再讨论执行经济学，不要跳回期权，不要用15/30结果直接选持有期。

## 复现

PYTHONPATH=src:. python research/r1a_carrier_transport/endpoint_diagnostic.py --output /tmp/r1a-endpoint-new

PYTHONPATH=src:. python -m pytest -q tests/test_r1a_*.py

输出目录必须是新的。旧 transport.py / verify_cloud_replay.py 仍按原协议运行，不修改其95%正成交量门槛或完整路径定义。

保留所有源数据、旧回执和新端点回执。R1_B、R2方向交易和已关闭期权身份不重开。BLACKBOX_query_count=3；禁止query#4；production_authority=false；fresh_oos=false。
