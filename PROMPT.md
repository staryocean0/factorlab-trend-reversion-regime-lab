# 接手任务边界

仓库 staryocean0/factorlab-trend-reversion-regime-lab。先读 CONTINUE_HERE.md、ETF_INDEX_MEASURABILITY_REVIEW_20260912.md 和 ETF_SOURCE_QUALITY_ADVISORY_20260912.json。

新的ETF/指数可测量性筛查已完成，没有运行回归收益策略。不要把本说明理解成自动授权下载/采购或继续新策略。

有一项已验证的问题：512100于2022-09-02合并份额并停牌，2022-09-05恢复，原行动表遗漏此事。原公告依据已记录，缺失240条ETF时间戳恰在停牌日，不能补造。旧文件保留，不再把corporate_actions_complete=true当成事实。另有零成交量与OHLC非平价并存、指数已补齐分钟及available_at口径问题。

若用户明确授权后续来源修复：保护工作区，同步main；核查合法源数据合同和完整分红/拆分/合并/停牌账本，建立新版本，不覆盖旧manifest和回执；先做受影响输出和边界范围审计，不为救R1_A调整参数。

若用户明确授权补充报价资料：先确认既有权限能否提供预先选定的小段完整非事件条件化ETF买一卖一/规模/最后成交时间、指数发布时间，以及IOPV方法与发布时间或篮子现金估值依据。带来源序号、修订和时区/分钟聚合/volume单位说明。不要先买五年L2，不要传账号token，不要重传已有一分钟CSV冒充新资料。

R1_A保持储备；不重开其模型、匹配或旧期权。不打开2026候选，不选择持有期，不运行修复收益直到另行冻结获准。BLACKBOX_query_count=3，production_authority=false，fresh_oos=false。
