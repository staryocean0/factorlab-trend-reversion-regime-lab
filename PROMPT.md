# 本地执行模型接管提示

你接管的是 `staryocean0/factorlab-trend-reversion-regime-lab`。不要重新设计、重跑或调参救援已经关闭的研究身份。先读 `CONTINUE_HERE.md`。

## 当前 authority

- R1 / R2 是 certified mechanism；机制认证仍有效。
- `BLACKBOX_query_count=3`；禁止 query #4。
- `production_authority=false`。
- 当前没有已授权的 empirical payoff candidate。

已经关闭：

- R1/R2 已测试的 index-level economic translations；
- unified router；
- `rmr_R1B_temporal_impulse_completion_v1`；
- R1_B 单 long ATM MO：`rmr_R1B_MO_convex_impulse_mapping_v1`；
- R1_B 1x2 adjacent-OTM ratio backspread：`rmr_R1B_MO_ratio_backspread_v1`；
- R5-B1 以及其他已归档 Stage-1 lanes。

最新 program state：

`CERTIFIED_R1_R2_MECHANISMS_NO_AUTHORIZED_EMPIRICAL_PAYOFF_CANDIDATE`

最新 payoff review：

`R1B_LISTED_DIRECTIONAL_OPTION_PAYOFF_PROGRAM_CLOSED_NO_NEW_EMPIRICAL_IDENTITY`

## 最新结果

1x2 backspread 在任何 outcome 打开前已冻结：同一 R1_B event/clock/exit，short 1 deterministic ATM，long 2 immediately adjacent OTM，同 expiry，同一 quote timestamp 同步成交，14 CNY/contract/leg，completed package 总 fee 84 CNY。

结果：

- joinable 385；completed 360；coverage 93.51%；
- pooled mean -376.61 CNY；
- median -884 CNY；
- win rate 22.22%；
- 2023/2024/2025 年均值全部为负；
- 2023Q1..2025Q4 仅 2/12 quarters 为正；
- `FAIL_IDENTITY_CLOSED`。

见：

- `docs/research/R1B_MO_RATIO_BACKSPREAD_OUTCOME_STUDY_20260911.md`
- `docs/ops/evidence/r1b_mo_backspread_20260911/outcome_receipt.json`
- `docs/research/R1B_POST_BACKSPREAD_PAYOFF_THEORY_REVIEW_20260911.md`

不要尝试 1x3、2x3、更多 OTM、vertical、calendar、另一 DTE 或其他从已见 payoff surface 选出来的变体。

## 数据

云端历史研究数据已经自给：`data/r1b_research/`。

包含：

- CSI1000 `000852.SH` 1m，至 2025-12-31；
- `contract_master.csv`；
- joinable 2022-07-22..2025-12-31 MO L1 bid/ask/status CSV。

DataHub 主 MO quote route 已 admission PASS；active fee contract 为 14 CNY/contract/leg。

2026 MO 不得自动构造 event，因为云端没有 separately admitted 的 2026 underlying 1m。

## 接下来允许做什么

可以：

- 审计与复现已关闭研究；
- 维护数据、provenance、tests、receipts；
- 做真正独立、results-blind 的 payoff/mechanism theory review；
- 若存在全新经济机制或真实账户 use-case，可先写 theory review，再在**任何对应 outcome 读取前**冻结新的 machine contract。

不可以：

- 用已看到的 option outcomes 搜 strike、ratio、width、DTE、exit、horizon、year、side、regime、time-of-day；
- 把 R2 adverse markout 重新包装成 timing rescue；
- probability filter/sizing rescue；
- BLACKBOX query #4；
- production promotion。

如果没有独立理论，不要为了“继续研究”硬造 v3/v4；正确动作是维持 `no empirical candidate`。

## 工程纪律

- 所有新 empirical identity 必须先冻结、后看 outcome；
- synthetic/fail-closed tests 先于真实回放；
- 失败必须保留，不覆盖历史证据；
- 一次性 workflow 完成后清理；
- `CONTINUE_HERE.md` 是当前 authority 入口；
- 不提交账号、凭据、非公开下载链接或本地原始 DataHub lake。
