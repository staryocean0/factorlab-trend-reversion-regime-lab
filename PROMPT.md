# 本地执行模型接管提示

你现在接管仓库 `staryocean0/factorlab-trend-reversion-regime-lab` 的本地工作副本。不要重新设计前面的研究，不要重跑已经关闭的机制，不要向用户重复询问已经冻结的数学/数据工程决策。直接从 `main` 当前 authority 继续执行。

## 先做

1. `git status`，确保了解本地未提交改动；不要覆盖用户本地工作。
2. `git fetch`，在安全前提下同步 `main`；只允许 fast-forward，不要强制覆盖。
3. 先读：
   - `CONTINUE_HERE.md`
   - `AGENTS.md`
   - `docs/research/R1B_MO_CONVEX_PAYOFF_THEORY_REVIEW_20260910.md`
   - `docs/research/R1B_MO_CFFEX_ACQUISITION_SPEC_20260910.md`
   - `docs/research/R1B_MO_CIIS_CURRENT_ORDER_ROUTE_20260910.md`
   - `docs/governance/R1B_MO_DATA_ADMISSION_PROTOCOL_V1.json`
   - `docs/governance/R1B_MO_CIIS_DELIVERY_EPOCH_FREEZE_20260910.json`
   - GitHub issue #7

## 不可改变的 authority

- R1 / R2 已经是 certified mechanism，不重新发现。
- 关闭的线性经济翻译、unified router、R1_B temporal impulse completion、R5-B1 不允许通过调参救活。
- 当前唯一 active identity：`rmr_R1B_MO_convex_impulse_mapping_v1`。
- 当前决策：`R1B_MO_CONVEX_PAYOFF_THEORY_ACCEPTED_DATA_ADMISSION_REQUIRED`。
- `BLACKBOX_query_count=3`，禁止 query #4。
- `production_authority=false`。
- 现在只允许做 **MO instrument-data acquisition / schema admission / fee-contract completion**；尚不允许任何 R1_B 事件条件化的 MO 收益、PnL、strike/DTE/horizon 搜索。

## 你的执行任务

### A. 获取真实、非事件条件化的数据样本或正式交付

优先 CFFEX 官方历史 Level-2 Snapshot 或 CIIS 官方分发。旧公开样本 `20221206_Sample_CFF_Snapshot.xlsx` 已确认 live 404，且同路径变体和 exact-URL Internet Archive 路径都已耗尽；不要盲目重复。

尝试获得：
- 当前等价的非事件条件化 Snapshot sample；或
- 正式完整交付。

目标范围是全部挂牌 MO 合约，历史段 2022-07-22 至 2026-09-10。不要把 R1_B event timestamps 提供给数据方，也不要只请求事件附近数据。

如果遇到付费、登录、人工审批、账号权限等不可自动跨越的现实边界：
- 不要伪造下载结果；
- 不要假装已经购买；
- 整理出精确的 order/request package、字段要求、时间范围、联系人/页面和待用户完成的唯一外部动作；
- 然后继续完成所有不依赖购买的代码、schema、测试和 provenance 工作。

### B. 严格按两个 delivery epoch 处理

研究窗口跨过已冻结的物理格式切换：

1. `LEGACY_CFFEX_SNAPSHOT`: 2022-07-22 .. 2024-07-07
2. `POST_TRANSITION_CFFEX_DELIVERY`: 2024-07-08 .. 2026-09-10

两个 epoch 必须分别：
- 保存原始 bytes；
- SHA-256；
- byte size / row count / file structure；
- 独立 source-specific mapping；
- 独立 schema/provenance check。

不能因为一个 epoch 映射成功就推断另一个 epoch；两个都过关前禁止 canonical concatenation。

### C. 必须实际解决的字段语义

对每个 epoch，从真实 sample / delivery dictionary 中确定，不允许猜：
- contract code / `SecurityID`；
- timestamp 格式、精度、时区；
- bid1 / bid1_size / ask1 / ask1_size 的物理列映射；
- last price；
- volume；
- open interest；
- trading/quote status；
- zero / missing quote semantics；
- contract master / expiry / last trading date；
- correction / republication / version semantics。

### D. 使用现有 fail-closed 基础设施

现有代码：
- `research/r1b_mo_data_admission/adapt_cffex_snapshot.py`
- `research/r1b_mo_data_admission/adapt_cffex_snapshot_epochs.py`
- `research/r1b_mo_data_admission/validate_mo_quote_source.py`

原则：
- adapter 成功最多是 `ADAPTED_NOT_ADMITTED` / `MULTI_EPOCH_ADAPTED_NOT_ADMITTED`；
- unresolved mapping、跨 epoch 日期泄漏、unknown status 等必须 FAIL_CLOSED；
- 不允许 midpoint / last price 替代缺失 bid/ask；
- 不允许为了通过 validator 修改策略定义。

先运行完整测试。新增代码必须补 synthetic / fail-closed tests。

### E. fee contract 并行推进

继续补齐：
- CFFEX 官方 exchange fee 的完整 effective-period chain；
- broker/customer 历史 commission schedule（只有真实来源才可写入）。

不能：
- 把 RMB 15/contract 当成完整历史 all-in fee；
- 假设 broker markup=0；
- 用别家券商客户费率替代本账户费率。

如果 broker 历史费率确实无法获得，明确保持 `pending`，不要用保守假设偷偷替代 admission requirement。

## 数据与仓库卫生

- 大型/付费/非公开原始交付默认不要提交到 public Git；本地原样保存，仓库只提交 public-safe manifest、checksums、schema mapping、receipt、代码和必要公开材料。
- 不提交账号、订单号、发票、个人联系方式、cookie/token、非公开下载链接。
- 临时下载脚本、一次性 workflow、探测日志完成使命后删除；决定性 receipt 留存。
- 关闭的研究线放 archive，不重新放回 active `research/`。
- 每完成一个阶段，同步 `CONTINUE_HERE.md` 与 issue #7，使下一位执行者可以无上下文接管。

## 决策权限

用户已授权你自行做剩余的数学、统计、数据工程、软件工程决策。不要因为存在多个合理实现就停下来询问用户；选择最保守、可复现、fail-closed 的方案执行，并在 receipt 中记录理由。

只有真正涉及以下情况才停下等待用户：
- 需要用户付款/签署/登录/提供账号权限；
- 需要用户提供只有其本人拥有的 broker 历史佣金材料；
- 会产生不可逆的外部商业行为。

## 完成标准

你应尽可能推进到下列最远状态：

`REAL_SOURCE_BYTES_ACQUIRED -> PER_EPOCH_SCHEMA_MAPPED -> CANONICALIZED_NOT_ADMITTED -> FEE_CONTRACT_FROZEN -> VALIDATOR_PASS/FAIL_RECEIPT`

只有完整 admission PASS 才能提出一个**单独的 pre-execution freeze**。即使 PASS，也不要直接运行 MO PnL。

结束时汇报：
- 实际取得的数据/文档及 checksum；
- 两个 epoch 的 mapping 状态；
- 测试和 validator 结果；
- fee-contract 状态；
- commit SHA；
- 唯一剩余 blocker（如有）。
