# 接管：单日字段对账已完成，不再自动追加实验

仓库staryocean0/factorlab-trend-reversion-regime-lab。保护未提交工作，安全同步main。先读CONTINUE_HERE.md和docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md。

本轮已完成：六个单日源文件与旧CSV仅2025-12-01的482行对账；9798行逐报价账、1928行四种分钟情景账、限定盘口消费者与完整处置记录。

日终量相等但日内同标签量不完全相等：连续报价629/4711、3508/4740条cum_volume大于该标签及以前逐笔量。不能叫作ETF领先指数，不拟合时间偏移。四种固定分钟边界都未完整复原旧OHLC，不挑一个好看的方案改旧数据；未认证单位也不擅自乘100。13:26零量非平价异常仍未在原供应商分钟层解释。

本仓RestrictedSourceView已限制读取：同阶段checkpoint，左闭右开，只收紧消费者阶段结束，坏的最新事件不退回旧事件，禁止跨休息/竞价、未来回填和倒置末行查询。未修改DataHub生产代码或源Parquet。其valid_until仍是离线元数据，不宣称实时可知。

没有新的本地搬运任务；五年CSV、说明和六个单日文件都已交付。当前有限对账结束，不自动扩日期、读2026、采购、拟合时移、试更多分桶或计算收益。后续新问题须单独说明来源假设和授权范围，不能把未知事实用统计拟合补造。

R1_A继续储备，旧行动修复及历史结果零影响结论不变。旧来源/配对/收益/阈值与所有失败记录保留。BLACKBOX_query_count=3，production_authority=false，fresh_oos=false。
