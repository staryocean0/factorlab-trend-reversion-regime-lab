# 云端接管提示 — R1_A 统计稳健性已完成

仓库 staryocean0/factorlab-trend-reversion-regime-lab。先读 CONTINUE_HERE.md 和 docs/research/R1A_ENDPOINT_ROBUSTNESS_REVIEW_20260912.md，安全同步主干，不覆盖用户工作。

## 已经完成，不要重复当成新研究

实际 ETF CSV 在 data/r1a_carrier_prices/cloud_pack_v1/，无需本地 DataHub/private 或再次搬运。

指数价格层、匹配对照、两只 ETF 的七周期端点价格诊断，以及本轮依赖性/观测选择稳健性均已执行。

最新状态 RETROSPECTIVE_ENDPOINT_ROBUSTNESS_COMPLETED_NO_PRODUCTION。

R1_A 仍是短周期历史线索，不是已经统计确立、可直接交易的 alpha。均值没有被重算成负数，但考虑共享行情、重复对照和同时检查14项后，没有一项主检验区间完全高于零。不要把这误写成证明无效或关闭R1_A机制。

中证1000 15/30 bar 增量 +4.368/+7.074bp；14项校正区间 [-2.211,+10.948]/[-4.077,+18.224]bp。对照等权、去重叠、逐暴露年剔除的短周期符号仍为正。长周期更不稳。

2021年30 bar仅159/186组端点可观测，另27组的均值只需-7.403bp即可使该年全样本均值为零。原先5/5年正只属于观测样本，不是全体事件证据。所有缺失情景是假设分析，没有补造ETF结果。

## 下一有效方向

需要单独冻结真正未使用/前瞻样本的确认设计，先定数据角色、观测和退出处理，再看结果；不要在同一历史区间不停换块长、匹配、持有期、年份、方向或ETF寻求显著。不能默认2026或任何新标签就是未见样本。禁止BLACKBOX query#4。

本轮近似图依赖方差和t校准的假设未被独立证明，14/56项校正也没有消除此前整个研究史的选择影响。不宣称新OOS、因果识别、全事件收益或实盘净利润。

## 复现

PYTHONPATH=src:. python research/r1a_endpoint_robustness/study.py --output /tmp/r1a-robustness-new

PYTHONPATH=src:. python -m pytest -q tests/test_r1a_*.py

只能用新输出目录，不覆盖旧回执。原完整路径v1和端点协议保持原状。中证1000未通过的七周期共同样本收益表仍不打开。

不改信号、配对、时钟、固定载体、七周期和源数据。R1_B、R2方向和旧期权身份不重开。BLACKBOX_query_count=3；production_authority=false；fresh_oos=false；不选持有期。
