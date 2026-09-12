# 接管提示：ETF已知行动修复完成，剩下是来源资格

接管 staryocean0/factorlab-trend-reversion-regime-lab，安全同步main，不覆盖用户未提交工作。先读CONTINUE_HERE.md和docs/research/ETF_SOURCE_REPAIR_IMPACT_REVIEW_20260912.md。

不要重做已完成的任务：512100 2022-09-02份额合并已经在data/etf_source_actions_v2/及来源overlay中补入；2022-08-03拆分提案已取消，不得纳入有效调整。3,098组旧配对、21,686行周期记录的影响已核实：已发表样本不变，旧均值不变；三行只是新增排除原因。停牌日不补行情。

完整源数据资格仍未通过。不得把“已知遗漏修复”写成两只ETF 2021—2025完整行动/停牌及交易所时钟已认证；588000空表不等于完整无事件证明。原manifest中的complete=true和旧导出器硬编码不能用于新研究准入。

用户要求进一步补本地材料时，仅执行docs/ops/ETF_UPSTREAM_SEMANTICS_HANDOFF_20260912.md中的明确缺口：上游分钟/墙钟字典与版本、固定零成交量非平价样例的原始字段与聚合规则、指数causal_flat_fill及available_at语义、完整行动来源范围。公开权限不明的内容不得直接放公共Git；账号token等凭据不得交付。缺证据写UNKNOWN，不修改价格凑一致。

现有五年ETF CSV已在云端，不要重复上传；本任务不授权数据采购、L1历史批量下载、2026收益、R1_A重启或任何策略参数调整。

维护验证：

```bash
PYTHONPATH=src:. python -m pytest -q tests/test_etf_source_repair.py tests/test_etf_source_repair_retained.py
PYTHONPATH=src:. python research/etf_source_repair/verify_retained.py
```

原始数据、旧冻结和旧结果全部保留。R1_A继续储备，ETF相对定价研究仍需来源/同步报价依据；BLACKBOX_query_count=3，production_authority=false，fresh_oos=false。
