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

### 2022 launch-level corroboration

Multiple CFFEX member notices reproducing the CSI1000 option launch terms identify the exchange baseline at launch as:

- MO trading fee: RMB 15 per contract;
- exercise/assignment fee: RMB 2 per contract;
- option order-declaration fee temporarily not charged.

Examples that explicitly distinguish the exchange fee from the broker/customer fee include:

- CICC Wealth Futures launch notice: https://www.ciccwmf.cn/gsgg/73874.jhtml
- Zhejiang New Century Futures reproduction of the exchange launch notice: https://www.zjncf.com.cn/customer/info/4197.html

These are useful corroborating evidence but do **not** replace a complete official CFFEX effective-period history for the frozen research contract.

## 2. Why the exchange fee is not yet marked `frozen`

The evidence strongly supports 15 RMB/contract trading and 2 RMB/contract exercise at launch and in the July-2024 CFFEX fee table.

However, this research covers observations from 2022-07-22 onward. Before marking the exchange fee history frozen, one of the following must be obtained:

1. an official CFFEX historical notice/archive proving the effective periods and any changes from 2022-07-22 through the historical study end; or
2. an official CFFEX statement/fee history sufficient to prove that the same standard applied continuously over the relevant period.

Absence of a search result for a fee-change notice is not evidence that no change occurred.

Therefore:

`exchange_fee_history_status = strong_partial_evidence_not_full_effective_period_chain`

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

- continue collecting official CFFEX fee history;
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

`R1B_MO_FEE_CONTRACT_PENDING_EXCHANGE_CHAIN_PARTIAL_BROKER_UNRESOLVED`

`BLACKBOX_query_count=3`.
`production_authority=false`.
