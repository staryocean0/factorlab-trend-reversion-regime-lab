# R1_B MO fee-source status — 2026-09-11

Research identity: `rmr_R1B_MO_convex_impulse_mapping_v1`

Current decision: **FEE CONTRACT FROZEN**

Machine contract: `docs/governance/R1B_MO_FEE_CONTRACT@1.0.json`

## User-authoritative freeze

On 2026-09-11 the account holder froze the all-in MO trading fee assumption:

| Leg | CNY per contract |
| --- | ---: |
| open | 14 |
| close | 14 |

Exercise/assignment and declaration fees are set to **0** for the current R1B mapping because the inherited causal exit is bid/ask based, not expiry exercise.

Effective MO quote window for fee binding: **2022-07-22 .. 2026-08-25** (tail to 2026-09-10 waived separately).

Spread is **not** double-counted in fees; execution uses ask-entry and bid-exit.

## Prior exchange-evidence note (historical context only)

Earlier work collected strong CFFEX public anchors at RMB 15/contract trading and RMB 2/contract exercise/assignment. That chain was never promoted into the research contract because broker/customer history remained unresolved. The user override above supersedes pending exchange/broker negotiation for this study.

## Validator implication

Any populated admission manifest must reference `fee_contract.status=frozen` and copy the effective period above. Pending fee state is no longer the blocker.

`BLACKBOX_query_count=3`
