# 接管提示：当前 R1_A 价格版本已阶段性收口，转为储备

仓库：staryocean0/factorlab-trend-reversion-regime-lab。
安全检查本地git状态并同步main，不覆盖用户工作。先读CONTINUE_HERE.md和docs/research/R1A_EVIDENCE_CLOSEOUT_REVIEW_20260912.md。

当前状态：R1A_CURRENT_PRICE_FORMULATION_RESERVED_ACTIVE_DEVELOPMENT_PAUSED。
不是待补数据，也不是又有一个设计等待自动执行。跨研究对账、已保存预测误差分解和阶段性去留判断已经完成。

已有数据和原事件身份不变。原预测记录、评分和参数在本轮锁定审计范围内没有实质算术差异；但这不代表原始行情语义或所有统计假设已被独立验证。
15/30等位置的小幅前推MSE改善主要来自年度平均偏差修正，年内中心化误差没有改善。本轮没有重新训练。指标在每个年度事件样本中恒为1，不能因此推断所有非线性、排序或均值回归均无效。

当前默认没有后续实证任务。不得自动更换模型、lambda、特征、配对、方向、年份、持有周期、费用或期权来寻找通过；不得打开失败严格配对方案的241/17组收益或2026候选数据。

储备只针对当前R1_A价格策略版本的连续主动开发，不是永久禁止科学研究或关闭整个项目。以后用户明确授权新的独立问题或可复现错误修复时，应写清研究对象、数据资格、预算与停止条件，并保留旧结论。

历史ETF文件已在云端；无例行本地搬运任务。不要反复请求同一份数据。原R1/R2机制记录和全部历史证据保留，旧R1_B/R2方向/期权关闭身份不重开。

仅维护复现时，使用research/r1a_evidence_closeout/README.md中的命令，输出到新目录；不要将复现成功写成策略确认。

BLACKBOX_query_count=3；禁止query #4；production_authority=false；fresh_oos=false；confirmation_clock_started=false；horizon_selected=false。
