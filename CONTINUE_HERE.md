# Continue here — reversal / mean-reversion bucket

## Current authority

This repository owns real reversal / mean-reversion strategy research.

Certified mechanism identities remain:

- **R1** — `rmr_cross_scale_pullback_parent_integrity_v2`;
- **R2** — `rmr_range_boundary_parent_integrity_v2`.

Reusable BLACKBOX query count remains exactly **3**: R1 PASS, R5-C FAIL, R2 PASS. No query #4 is authorized.

`production_authority=false`.

## Closed — do not restart or retune

The following are closed under their frozen definitions:

- R1 immediate index-level economic translation;
- R2 `rmr_R2_range_reentry_economic_translation_v1`;
- unified parent-normal-state router;
- R1_B `rmr_R1B_temporal_impulse_completion_v1`;
- R1_B MO single-long identity `rmr_R1B_MO_convex_impulse_mapping_v1` / `R1B_MO_ATM_DIRECTIONAL_LONG_SAME_CAUSAL_EXIT`;
- R1_B MO financed-tail identity `rmr_R1B_MO_ratio_backspread_v1` / `R1B_MO_1x2_ADJACENT_OTM_RATIO_BACKSPREAD_SAME_CAUSAL_EXIT`;
- probability-threshold / probability-sizing rescue;
- simple horizon / delay / stop / target / cost / scale rescue;
- broad automatic R8/R9 generation;
- R3/R4 and other closed Stage-1 lanes;
- R5-B1 limited diagnostic.

The scientific distinction remains:

> certified restoration probability is not the same thing as a certified trading payoff.

## Latest decisive result — R1_B MO 1x2 adjacent-OTM backspread

The user authorized the next cloud research stage. A genuinely different payoff object was frozen **before** opening its outcomes:

`R1B_MO_1x2_ADJACENT_OTM_RATIO_BACKSPREAD_SAME_CAUSAL_EXIT`

Mapping:

- same certified R1_B events and parent direction;
- same next-1m-close underlying entry;
- same causal S2 completion / S3 failure exit;
- same 1200-bar safety horizon and deterministic expiry rule;
- short 1 deterministic ATM directional MO option;
- long 2 immediately adjacent OTM options of the same type/expiry;
- both contracts must be executable at the same quote timestamp;
- entry short at bid / long at ask; exit short at ask / long at bid;
- 14 CNY per contract per leg, 84 CNY total fees for a completed 1x2 package;
- no ratio, spread-width, strike-distance, DTE, horizon, exit, filter or fee search.

Results-blind preflight Actions run `34612801045`: **PASS, 5/5 tests**.

Frozen historical outcome Actions run `34612892387`, job `103307532666`: the outcome step itself completed successfully. The workflow's final status was failure only because sparse checkout prevented `git add` of generated evidence; the aggregate adjudication was recovered exactly from the immutable job log without rerunning the empirical study.

Decisive result:

`R1B_MO_RATIO_BACKSPREAD_FAIL_IDENTITY_CLOSED`

- joinable R1_B events: **385**;
- completed synchronized backspreads: **360**;
- joint-fill coverage: **93.51%** — PASS versus 80% gate;
- pooled mean net: **-376.61 CNY** — FAIL;
- descriptive median: **-884.00 CNY**;
- descriptive win rate: **22.22%**;
- annual mean 2023: **-408.57 CNY**;
- annual mean 2024: **-131.43 CNY**;
- annual mean 2025: **-484.82 CNY**;
- positive voting years: **0/3** — FAIL versus >=2;
- positive quarters 2023Q1..2025Q4: **2/12** — FAIL versus >=6.

Only 2024Q1 and 2024Q3 were positive. The large 2024Q3 right tail does not support a reusable identity.

Read:

- `docs/research/R1B_MO_RATIO_BACKSPREAD_THEORY_FREEZE_20260911.md`
- `docs/governance/R1B_MO_BACKSPREAD_PRE_EXECUTION_FREEZE@1.0.json`
- `docs/research/R1B_MO_RATIO_BACKSPREAD_OUTCOME_STUDY_20260911.md`
- `docs/ops/evidence/r1b_mo_backspread_20260911/outcome_receipt.json`

Do **not** rescue this identity by changing ratio, OTM distance, DTE, calendar structure, exit, horizon, filters, side or fees.

## Program-level payoff review

After two separately frozen directional-convex payoff objects failed — single long ATM and 1x2 adjacent-OTM backspread — a post-result theory review found no additional nearby listed-MO structure that can currently be specified independently of the already observed option outcomes.

Decision:

`R1B_LISTED_DIRECTIONAL_OPTION_PAYOFF_PROGRAM_CLOSED_NO_NEW_EMPIRICAL_IDENTITY`

Read:

- `docs/research/R1B_POST_BACKSPREAD_PAYOFF_THEORY_REVIEW_20260911.md`

This does **not** claim every conceivable option strategy is unprofitable. It means no R1_B option v3/v4 is presently authorized because another strike, ratio, width, DTE, vertical, calendar or volatility structure would require a new independent mechanism/theory rather than outcome-conditioned rescue.

## Current frontier

**There is no open empirical payoff identity.**

The R1 and R2 mechanism certifications remain valid, but the tested economic translations are closed. The current correct state is therefore:

`CERTIFIED_R1_R2_MECHANISMS_NO_AUTHORIZED_EMPIRICAL_PAYOFF_CANDIDATE`

A future empirical program may open only when a genuinely independent theory or economic use-case determines the payoff object before its corresponding outcomes are read. Examples could include a separately justified volatility-risk-premium mechanism, a real account-level hedge/inventory problem, or a newly admitted instrument whose contractual payoff directly matches restoration. Such a restart requires a new freeze and explicit authority; it may not use the failed option outcomes to choose parameters.

No BLACKBOX query #4 is scheduled.

## Data state — cloud execution is available

Historical MO intraday best-bid/best-ask data are admitted on the DataHub primary route. Admission validator PASS receipt:

`docs/ops/evidence/r1b_mo_admission_20260911/admission_validator_receipt.json`

Primary admitted inventory contains **46,365,986** canonical rows across **50** monthly files over **2022-07-22 .. 2026-08-25**.

Cloud-ready research CSV pack is committed under:

`data/r1b_research/`

It contains:

- `underlying_1m/`: CSI1000 `000852.SH` 1m through 2025-12-31;
- `contract_master.csv`;
- `mo_quotes/`: cloud-readable slim MO L1 quote files through 2025-12-31.

Therefore historical 2022-07-22..2025-12-31 option research can execute entirely in GitHub/cloud runners without the local DataHub lake.

2026 MO quotes are not currently event-joinable because no separately admitted 2026 underlying 1m package is in the cloud research pack. Do not fabricate 2026 events from option quotes alone.

Active all-in fee authority is:

`R1B_MO_FEE_CONTRACT_FROZEN_USER_14_CNY_PER_LEG`

Machine contract: `docs/governance/R1B_MO_FEE_CONTRACT@1.0.json`.

CIIS/CFFEX official Level-2 acquisition remains optional provenance strengthening, not a current historical-computation blocker.

## Exact next authorized action

Do not launch another empirical R1_B option structure automatically.

Authorized now:

- preserve and audit the two closed option identities;
- maintain the admitted cloud research pack and provenance;
- conduct results-blind theory work only if it is genuinely independent of the observed option payoffs;
- formulate a new freeze only when such a theory exists.

Not authorized:

- ratio/strike/DTE/vertical/calendar search around the failed option outcomes;
- R2 timing rescue against its adverse markout surface;
- probability filtering/sizing rescue;
- BLACKBOX query #4;
- production promotion.

## Bucket boundary

Generic Range / UpTrend / DownTrend state recognition belongs to `factorlab-two-wave-strategy-lab`.
Unsafe / Recovering / HighVol risk-state switching belongs to `factorlab-star50-filter-lab`.

Legacy, mis-scoped and closed evidence remains under `docs/archive/` and Git history.

## Read first

1. `CONTINUE_HERE.md`
2. `docs/research/R1B_POST_BACKSPREAD_PAYOFF_THEORY_REVIEW_20260911.md`
3. `docs/research/R1B_MO_RATIO_BACKSPREAD_OUTCOME_STUDY_20260911.md`
4. `docs/research/R1B_MO_OUTCOME_STUDY_20260911.md`
5. `docs/ops/evidence/r1b_mo_backspread_20260911/outcome_receipt.json`
6. `docs/ops/evidence/r1b_mo_outcome_20260911/outcome_receipt.json`
7. `docs/RESEARCH_GOVERNANCE.md`
8. `docs/DATA.md`

`BLACKBOX_query_count=3`.
`production_authority=false`.
