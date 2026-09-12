# 精确上游材料缺口：不是再次导出五年ETF行情

已完成的行动修复和旧结果影响审计不要重做。先读 `docs/research/ETF_SOURCE_REPAIR_IMPACT_REVIEW_20260912.md`。现有云端数据可读，公开包不需要重传。

当用户授权本地补充时，仅在现有合法访问范围内取得下列来源证据；没有权限不购买、不借凭据、不输出账号或token。

1. 提供所引用 `unified_datahub/docs/modules/history/canonical-bars-whitepaper.md` 第5节以及 `unified_datahub/src/datahub/storage/query/session_offset_contract.py` 相关定义的可公开摘录、版本commit和文件hash。解释session_end_label_v2为何以Z形式保存上海墙钟，明确分钟边界包含规则，而不是用ETF/指数最高相关性选择平移。
2. 对 `docs/ops/evidence/etf_index_measurability_source_20260912/earliest_nonflat_zero_volume_examples.csv` 已固定的最早样例，提供对应上游字段、成交量原单位、分钟聚合及缺失占位规则。只需必要样例和转换链，不要求重新交付全部价格。原始volume=0但OHLC有范围的原因无法查明时记UNKNOWN，不能补造交易。
3. 解释指数causal_flat_fill与available_at的生成逻辑，区分交易所时点、供应商发布时点、canonical可用时点和历史入库时点。当前available_at不只有15:30，需按实现解释而不是概括猜测。
4. 有完整来源时，补充两只ETF 2021—2025的分红、拆分/合并及停牌事件核验范围。588000空表不能仅靠一次分红接口返回空证明；512100 2022-08-03提案已取消，不得再次补入有效行动。

交付：一份来源解释表、可公开的最小代码/文档摘录、每项证据版本/hash、无法核实事项。付费或非公开材料先脱敏并核实交付权利，不直接上传公共Git。不要更改原行情、信号、配对、收益、阈值或原行动CSV；必要修订只另建版本并说明具体依据。

这份任务只补来源资格，不授权新收益回测、2026样本、L1数据采购或R1_A重启。

本地已交付（2026-09-12）：公开包 `data/etf_upstream_evidence_v1/`。不重传五年 ETF CSV，不重复份额合并修复，不做前视裁决。供应商 zip 原始成员未找到，无单独私有包。
