# 云端研究交接 — R1_A 确认可行性已完成

仓库：staryocean0/factorlab-trend-reversion-regime-lab。
先读 CONTINUE_HERE.md 和 docs/research/R1A_CONFIRMATION_FEASIBILITY_REVIEW_20260912.md，安全同步 main，不覆盖用户工作。

## 当前结论

CONFIRMATION_FEASIBILITY_COMPLETED_NOT_READY_TO_START。

样本量／检验能力、22.4万组模拟空假设数据、五仓元数据资格审计均已实际执行。不要把它们重新说成待做计划；也不要立即打开2026收益。

R1_A仍是历史短周期线索，不是已经确认可交易的alpha，也没有被证明为零效应。

按原配对噪声与出现频率，假设真实增量4bp，80%检出能力、14项比较的指数层方案，15/30 bar分别需要约4858/13062组配对。这些是条件测算，不是确认样本承诺；其多年甚至数十年信息等价长度说明原方案效率不够，绝不是让用户等几十年。

旧graph/t方法在模拟跨日历块持续相关时会明显误报膨胀。模拟AR(1)=0.6下名义5%误报为6.8%-22.2%，不能把它当成真实市场误报率。不能据此改块长或估计器然后重算旧p值，直到显著。

## 下一步的有限任务

仅做方法校准／测量效率研究：使用预先声明的合成模型和已经披露的历史噪声、事件时钟，先检验方法能否处理跨块相关，再判断能否在明确资源预算下获得足够信息。所有方案必须有数学理由和停止边界，不能无限发散。

不改旧信号、原配对、七周期、ETF载体或旧结果。若确需更改未来确认的estimand或matching，必须单独公开为新设计，而不是翻写旧研究结论。

## 数据情况

历史ETF实际CSV已在 data/r1a_carrier_prices/cloud_pack_v1/，无需本地DataHub或private/，不要再让用户搬同一包。

隔夜仓已有2026中证1000分钟文件：
data/gap_fill_repeat_2026/csi1000_1m_20260105_to_20260821.parquet

清单声明154个交易日、36960行、fresh_oos=false，已用于隔夜gap-fill重复验证。R1_A专属暴露史仍UNKNOWN；别的研究使用不自动等于本假设被污染，但也不能直接说未使用。当前只查了元数据，没有读行情或收益。

在最终确认设计、来源准入和数据角色明确前，保留该候选，不消费其价格结果。没有启动正式前瞻时钟；本轮可行性冻结不是确认实验起点。

## 复现

PYTHONPATH=src:. python research/r1a_confirmation_feasibility/study.py --output /tmp/r1a-feasibility-new
PYTHONPATH=src:. python -m pytest -q tests/test_r1a_*.py

用新输出目录，不覆盖已完成回执。常规CI只复算确定性的可行性结果，不反复在线刷新数据资格审计。

BLACKBOX_query_count=3；禁止query#4；production_authority=false；fresh_oos=false；confirmation_protocol_frozen=false。不选持有期，不重开R1_B/R2方向交易/旧期权，不下单、不购买、不启动自动化任务。
