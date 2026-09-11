# 本地执行模型接管提示

你接管的是 `staryocean0/factorlab-trend-reversion-regime-lab`。不要重新设计、重跑或调参救援已经关闭的研究身份。先读 `CONTINUE_HERE.md`。

## 当前 authority

- R1 / R2 是 certified mechanism；机制认证仍有效。
- `BLACKBOX_query_count=3`；禁止 query #4。
- `production_authority=false`。
- 纯指数价格层验证已经完成，当前状态：

`R1_PRICE_EDGE_SUPPORTED_R2_DIRECT_DIRECTIONAL_PRICE_EDGE_NOT_SUPPORTED`

## 已完成的价格层验证

冻结合同：`docs/governance/INDEX_PRICE_VALIDITY_FREEZE@1.0.json`

结果：`docs/research/INDEX_PRICE_VALIDITY_STUDY_20260911.md`

Receipt：`docs/ops/evidence/index_price_validity_20260911/price_validity_receipt.json`

研究只问一个问题：信号确认以后，现金指数价格是否沿信号方向移动。

固定定义：

- entry = causal event confirmation 后下一条 1m close；
- LONG/SHORT 都用 synthetic signed cash-index return；
- primary cost = 0；
- horizons = `1/5/15/30/60/120/240` observed bars；
- 所有 horizon 全报，禁止挑赢家；
- LONG/SHORT 分开报告；
- MFE/MAE 和年度稳定性同时报告。

主要结论：

- CSI1000 R1_A：1–120 bars 多个 horizon 有一致正 price edge；
- CSI1000 R1_B：延迟 edge 明确，120 bars mean `+11.03bp`，240 bars `+23.43bp`；
- STAR50 R1_B transport：120 bars `+5.60bp`，240 bars `+18.19bp`；
- 上述 R1_B 120/240 在两个指数都达到 4/5 年正均值，且 LONG/SHORT 两侧均值都为正；
- R2_A/R2_B 没有形成稳定直接方向 price edge，CSI1000 随 horizon 拉长反而更加不利。

这证明 R1 在**价格层**有信息，但不等于已经得到可执行策略，也不授权从结果中选 120/240 作为持有期。

## 已关闭身份仍然关闭

不要因为新价格层结果重新打开：

- R1 structural economic translations v1/v2/v3；
- R2 `rmr_R2_range_reentry_economic_translation_v1`；
- `rmr_R1B_temporal_impulse_completion_v1`；
- R1_B 单 long ATM MO；
- R1_B 1x2 adjacent-OTM ratio backspread；
- 其他 archived closed lanes。

两个 MO 失败现在应理解为**具体 option payoff mapping 失败**，不是 R1 price signal 失败。

禁止基于已看到的 option outcomes 搜 strike / DTE / ratio / width / exit / horizon / year / side / regime。

## 当前下一层

研究顺序改为：

`R1 mechanism -> cash-index price validity -> ETF/index-carrier transport -> executable implementation`

当前仓库已有：

- `000852.SH` 1m：2015-01-05 .. 2025-12-31；
- `000688.SH` 1m：2020-07-23 .. 2025-12-31。

当前仓库**没有 admitted ETF minute-price package**，所以 ETF transport 尚未执行。

如果拿到 ETF 数据：

1. 先记录 ETF identity、数据来源、时间范围、时间戳/复权规则并冻结；
2. 不用 index 结果挑 horizon；
3. 原样 replay causal event timestamps/directions；
4. 同样报告完整 `1/5/15/30/60/120/240` signed return term structure；
5. ETF SHORT 可以作为 signal-transport synthetic return，但必须明确标注非实际可执行 short（除非另有真实借券/库存机制）；
6. 先回答 ETF 是否复制 index edge，再单独讨论交易成本/T+1/借券/期指/期权实现。

不要把 R2 直接推进 ETF/options directional execution；当前 price-layer evidence 不支持。

## 工程纪律

- empirical identity 必须先冻结后读结果；
- synthetic/fail-closed tests 先于真实回放；
- 不覆盖失败证据；
- 一次性 workflow 完成后删除；
- 当前 authority 入口是 `CONTINUE_HERE.md`；
- 不提交账号、凭据、非公开链接或本地原始 DataHub lake；
- 不为了“继续研究”从已见结果中挑参数。
