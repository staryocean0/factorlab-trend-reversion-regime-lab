# Versioned known-action correction

The actual small CSV files in this directory are byte-identical copies of the decisive action-correction outputs, not pointers to local private data. The underlying five-year ETF price pack is unchanged.

Read `manifest.json` and `docs/governance/ETF_ACTION_SOURCE_OVERLAY_V2_20260912.json` together. The detailed overlay contains the consolidation ratio, record/effective/resumption dates, verified suspension, cancelled proposal and source references. A cancelled 2022-08-03 split must never enter price adjustments. The effective 2022-09-02 consolidation must not be mistaken for investment return.

**This fixes the identified omission; it does not certify exhaustive 2021-2025 action/suspension history or exchange-synchronous price semantics.** In particular, the empty 588000 known-action inventory is not independent proof of no actions. The manifest explicitly denies full source qualification and microstructure-research admission.

Do not replace the old frozen action CSVs, fill the suspended day, infer executable NAV premiums, or re-open R1_A. Use this overlay when evaluating future source qualification, not old `corporate_actions_complete=true` in isolation.

Impact evidence: `docs/ops/evidence/etf_source_repair_20260912/`. All existing included endpoint and full-path memberships are unchanged by this specific correction; source qualification limitations remain.
