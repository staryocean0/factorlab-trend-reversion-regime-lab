# 云端研究接管 — 有限方法校准已完成

仓库 staryocean0/factorlab-trend-reversion-regime-lab。先读 CONTINUE_HERE.md 和 docs/research/R1A_METHOD_CALIBRATION_REVIEW_20260912.md，安全同步主干，不覆盖本地未提交改动。

## 最新实际停点

BOUNDED_SYNTHETIC_METHOD_REVIEW_COMPLETED_NO_CONFIRMATION_AUTHORITY。

七个预定模拟模型、28个设计、每模型2000组联合重复，三种可实现方法加一个已知协方差参照，已经执行完成。不要再把它当待设计或未执行的任务。

HAC6在中等持续相关情景下明显减少误报，但更强持续相关仍不稳健。五年分组法整体多重检验表现较好，但单项误报不满足预定要求，且把目标改成年度等权。没有可实现方法通过全部预定筛查；已知协方差参照不可部署。

未使用真实R1_A收益重新计算p值，没有读取2026行情，也没有消耗新的确认样本。R1_A仍是历史线索，不是已证实策略，也没有判定机制无效。

## 不再无限扩展方法筛选

本轮有限方法筛选到此结束。不能调整分块、滞后、组数、随机种子、模拟情景或判定容忍度，直到出现PASS；也不能拿新方法去反复检验旧R1_A收益。

后续经授权的具体问题应是：在已使用的Development资料中分解事件噪声、对照噪声、方向相反的共同冲击与协方差，确认哪些成分实际主导，以及是否有不依赖未来信息的降噪测量。先单独冻结这种诊断，不能把它当新的独立验证。当前回执尚未执行或冻结这项后续研究。

原样本量假设下，4bp增量在一年内确认需要约94.65%/98.01%的噪声方差减少；这不是实际可达到的R平方。在事件/对照等方差且独立的明确模型中，无限独立对照最多减半噪声；这个条件结论不能冒充真实R1_A噪声分解。

## 数据与边界

历史ETF原文件已在 data/r1a_carrier_prices/cloud_pack_v1/，不要再要求本地模型搬运。隔夜仓2026中证1000分钟候选真实存在，但有重复使用记录，R1_A专属暴露情况未确定，仍只允许元数据层，不打开价格或确认收益。

保留原信号、原配对、方向、两只ETF、七周期、全部旧冻结和结果。失败的主载体七周期共同样本收益表不打开。不开期权，不改交易成本/止损/时段/阈值救活旧身份。没有正式确认协议或观察时钟启动。

BLACKBOX_query_count=3；禁止#4；production_authority=false；fresh_oos=false；horizon_selected=false。

## 复现

OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=src:. python research/r1a_method_calibration/study.py --output /tmp/r1a-method-new

PYTHONPATH=src:. python -m pytest -q tests/test_r1a_*.py

每次使用全新输出目录。回归复算是确定性核验，不是重新获取策略证据。
