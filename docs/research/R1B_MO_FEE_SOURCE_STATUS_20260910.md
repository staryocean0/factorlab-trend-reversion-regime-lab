# R1_B MO fee-source status — 2026-09-10

Research identity: `rmr_R1B_MO_convex_impulse_mapping_v1`

Purpose: close as much of the fee-admission prerequisite as can be supported **before any event-conditioned option outcome is inspected**.

Current decision: **FEE CONTRACT NOT YET FROZEN**

Reason: exchange-level evidence is strong but the full effective-period chain has not yet been proven from a complete official historical notice set, and the account/broker commission schedule is not known.

`production_authority=false`.

## 1. Exchange-level evidence currently established

### Official CFFEX current/historical reference

CFFEX's July 2024 official fee table lists the three CSI index-option families together under the same merged fee standard:

- trading fee: RMB 15 per contract;
- exercise/assignment fee: RMB 2 per contract.

Official source:

- https://www.cffex.com.cn/cn/zjssf/20240701/39212.html

The CFFEX index-option trading rules separately state that option fee standards are set by the exchange outside the contract rules, so the fee table / fee notices, not the contract-rule text, are the authoritative numeric source.

Rule source:

- https://www.cffex.com.cn/cn/ssxz/20221214/43100.html

### 2022 launch-level evidence — official notice body retrieved 2026-09-11

CFFEX official notice (business notice page, 2022-07-18):

- http://www.cffex.com.cn/cn/ywtz/20220718/28904.html

The notice body states, under “六、相关费用”:

- MO option trading fee: **RMB 15 per contract**;
- exercise/assignment fee: **RMB 2 per contract**;
- MO option declaration/order fee: **not charged for now**.

Local archive SHA-256: `3d8390a900616a50a074beb2d3fe6c690f18becf0bc12ec7ab8bc98400f947b0`.

CFFEX's exchange-rule index still lists the same item as:

`关于中证1000股指期货和股指期权合约上市交易有关事项的通知`

Member reproductions identify it as **中金所发〔2022〕41号** and distinguish exchange baseline from customer/broker fees. Corroboration example:

- MO exchange trading fee: RMB 15 per contract;
- MO exchange exercise/assignment fee: RMB 2 per contract;
- MO exchange declaration/order fee: temporarily not charged.

Examples:

- CICC Wealth Futures: https://www.ciccwmf.cn/gsgg/73874.jhtml
- Jin Xin Futures, explicitly citing `中金所发〔2022〕41号`: https://www.jinxinqh.com/article/4739
- Zhejiang New Century Futures reproduction retained as corroboration: https://www.zjncf.com.cn/customer/info/4197.html

Important distinction: other member notices sometimes publish **their own customer fee** (for example a multiple of the exchange fee) in the same launch context. Such customer numbers are not exchange-level evidence and must not be imported into this account's fee contract.

This strengthens launch-date provenance, but it still does **not** replace retrieval of the original CFFEX notice body or another official CFFEX effective-period history sufficient to prove continuity.

## 2. Why the exchange fee is not yet marked `frozen`

The evidence now strongly supports the following two anchor points:

- launch, 2022-07-22: member reproductions of CFFEX notice `中金所发〔2022〕41号` report 15 RMB/contract trading, 2 RMB/contract exercise/assignment, declaration fee temporarily not charged;
- July 2024 official CFFEX fee table: 15 RMB/contract trading and 2 RMB/contract exercise/assignment for CSI index options including MO.

However, this research covers observations from 2022-07-22 onward. Before marking the exchange fee history frozen, one of the following must be obtained:

1. the original official CFFEX `中金所发〔2022〕41号` notice plus official notices/fee tables sufficient to establish every effective period through the historical study end; or
2. an official CFFEX fee-history statement sufficient to prove that the same standard applied continuously over the relevant period.

Absence of a search result for a fee-change notice is not evidence that no change occurred. The fact that a current fee table matches the launch-level member reproductions is strong continuity evidence, but not a complete effective-period proof by itself.

Therefore:

`exchange_fee_history_status = launch_notice_identity_strengthened_current_official_anchor_present_full_effective_period_chain_not_proven`

## 3. Broker/customer fee layer

The exchange table is charged to clearing members and does not determine the user's actual broker/customer commission.

Member notices demonstrate why this matters: some brokers published customer fees above the exchange baseline, while others referred clients to their individually agreed fee schedule.

No broker identity or account-specific historical commission schedule is available in this repository, and none will be invented.

Therefore:

`broker_fee_history_status = unresolved`

The primary economic test cannot silently assume:

- exchange fee only;
- zero broker markup;
- today's broker schedule for historical trades;
- a convenient multiple of exchange fees;
- a fee inferred from another broker's public notice.

## 4. Fail-closed fee policy

Until both layers are frozen, `docs/governance/R1B_MO_ADMISSION_MANIFEST_TEMPLATE.json` must keep:

`fee_contract.status = pending`

and the MO source validator must return FAIL for a supposedly complete admission package whose fee contract remains pending.

The final frozen fee contract must contain effective periods and distinguish at minimum:

- exchange open/close trading fee per contract;
- exchange exercise/assignment fee if the inherited causal exit can ever reach expiry;
- exchange declaration/order fee if applicable in a historical period;
- broker/customer commission per open and close contract;
- any broker minimum or other unavoidable per-order charge if applicable;
- source reference for every period.

For the current proposed R1_B mapping, bid/ask spread is handled directly by ask-entry and bid-exit and must **not** be counted again as a fee.

## 5. What this does and does not authorize

Authorized:

- continue collecting original official CFFEX fee history;
- obtain the actual historical broker commission schedule;
- freeze those numbers before option outcomes;
- retain a conservative sensitivity schedule only if preregistered before outcomes.

Not authorized:

- run option PnL using 15 RMB as if the full historical all-in fee were already proven;
- use another broker's customer commission as this account's historical fee;
- choose fees after seeing R1_B outcome profitability;
- compensate for missing fee evidence by using midpoint execution;
- open BLACKBOX query #4.

Current state:

`R1B_MO_FEE_CONTRACT_PENDING_EXCHANGE_CHAIN_STRONG_PARTIAL_BROKER_UNRESOLVED`

`BLACKBOX_query_count=3`.
`production_authority=false`.
