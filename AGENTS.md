# Reversal / Mean-Reversion Strategy Bucket

Read CONTINUE_HERE.md and docs/research/R1A_ENDPOINT_METHOD_REVIEW_20260912.md.

Latest measurement: ENDPOINT_DIAGNOSTIC_COMPLETE_DESCRIPTIVE, all 14 fixed carrier/horizon cells. The old full-path v1 remains PARTIAL_CARRIER_TRANSPORT under its unchanged definition; do not overwrite its freeze or failures. The endpoint alternative was explicitly separately frozen after a user-authorized method review, before new endpoint outcomes.

Actual ETF CSVs live in data/r1a_carrier_prices/cloud_pack_v1/. No local DataHub/private dependency or routine data-transfer request remains.

Preserve the original R1_A signals, pairs, directions, fixed carriers and seven horizons. New endpoint sampling requires four positive-volume exact observations per pair/horizon, record integrity >=95% by year and endpoint-pair coverage >=80% pooled AND every event year. These are frozen diagnostic gates, not a retroactive full-path PASS. No fills, nearest quotes, clock shifts, filters, rematching or excluded-year rescue.

Primary CSI1000 common-endpoint intersection failed the 2021 gate; its common-sample ETF outcomes were not opened. Per-horizon primary samples differ. Secondary common-endpoint sensitivity passed. Preserve this distinction.

Conditional terminal returns do not establish a live entry rule: exit availability is future information. Selection may be informative; source volume=0 is not independent proof of exchange no-trade. No path risk, MFE/MAE, stops/targets or execution feasibility was measured in the endpoint diagnostic.

Next work is a separately frozen dependence/observation-selection robustness treatment, not choosing 15/30 as a trading horizon or jumping to options. Account for overlapping windows, reused controls and multiple historical analyses before strong inference. Keep current conclusions descriptive until then.

Preserve old evidence and require fresh output directories. R1_B, R2 directional and closed MO identities stay closed. BLACKBOX_query_count=3; no query #4; production_authority=false; fresh_oos=false.
