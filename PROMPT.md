# 接管提示：真实开发期噪声分解已完成

仓库：staryocean0/factorlab-trend-reversion-regime-lab。
先检查 git status，保护本地改动，安全同步 main。先读 CONTINUE_HERE.md 与 docs/research/R1A_DEVELOPMENT_NOISE_REVIEW_20260912.md。

当前状态：DEVELOPMENT_NOISE_ACCOUNTING_COMPLETED_NOT_ALPHA_TEST。
不是等待本地模型补数据。现有历史 ETF 文件已在云端；本轮指数开发数据也已在 GitHub Actions 实际计算。

已完成内容：
- 中证1000使用原2015—2020开发期，1752组R1_A事件/对照；科创50仅2020短样本，156组。
- 原信号、阈值与匹配算法不改，另存DEV配对；没有把2021—2025验证期改称开发期，没有重配旧验证样本。
- 全报七周期事件方差、对照方差、协方差；按真实分钟时钟拆账重复及重叠暴露；分组与假设性多对照测算完整留存。
- 单个配对中事件腿更波动，但汇总到实际行情日期后，对照的重复、区间重叠造成暴露集中。两种方差不能混同，更不等于已校准的均值标准误。

精确证据位于 docs/ops/evidence/r1a_development_noise_20260912/。
复现代码位于 research/r1a_development_noise/。使用新输出目录，不覆盖旧receipt。

下一项若获授权，应讨论并另行冻结对照基准：事件发生时即可确定、限制或明确计入相同及重叠对照暴露、完整报告事件覆盖与协变量平衡。先做结果盲的可行性检查，不按收益选择设计。改有限样本对照定义属于新测量设计，不能用来追认旧显著性。
本轮并未实现这一新设计。不要把“已发现集中暴露”写成“已实现降噪”。也不允许为过门槛丢事件、删年份、挑方向或改周期。

不继续更换统计公式寻找历史p值，不启动正式确认，不打开2026候选行情，不返回期权。旧失败身份和数据质量门槛保留。
BLACKBOX_query_count=3，禁止query #4；production_authority=false；fresh_oos=false；confirmation_protocol_frozen=false。
