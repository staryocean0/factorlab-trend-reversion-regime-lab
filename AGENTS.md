# Reversal / Mean-Reversion Strategy Bucket

Read `CONTINUE_HERE.md`, then `docs/research/R1A_CARRIER_TRANSPORT_STATUS_20260912.md` before acting.

## Current scope

R1_A is the lead historical price-alpha lane. Carrier transport is now frozen and implemented but **data-blocked**, not empirically complete:

`BLOCKED_CARRIER_DATA_NOT_ADMITTED`; `ETF_outcomes_read=false`.

The tested code and cloud preflight do not imply an ETF alpha PASS. The missing dependency is real 2021-2025 ETF minute prices and complete source semantics/corporate actions.

Fixed maps: `000852.SH -> 512100.SH` and `000688.SH -> 588000.SH`. Do not choose another ETF using outcomes. Freeze: `docs/governance/R1A_CARRIER_PRICE_TRANSPORT_FREEZE@1.0.json`.

## Continue, do not redesign

Use `research/r1a_carrier_transport/transport.py`. Exact manifest/data request/commands are in its README. Preserve the original matched event/control pairs and replay both sides on exact INDEX timestamps. Report every 1/5/15/30/60/120/240 observed-bar horizon; no new signal, rematching, selected horizon, interpolation or next-price fallback.

Data insufficiency remains BLOCKED/INSUFFICIENT, not alpha rejection. Record all exclusions and same-sample index comparators. Corporate-action crossings must not silently become signal returns. Do not claim an actual shorting mechanism from synthetic SHORT price returns.

Use a new output directory for each delivery version. Preserve prior receipts. Keep nonpublic bytes, tokens and links out of public Git; raw private carrier data default to `data/r1a_carrier_prices/private/`.

## Scientific and governance boundary

Prior R1_A evidence is observational and conditional on its frozen matching design; pointwise bootstrap flags do not establish causal identification or familywise statistical confidence. ETF/index overlap is not fresh independent OOS.

R1/R2 certifications remain. R1_B is not the lead standalone entry-alpha lane; its raw delayed price returns cannot rescue the closed temporal/option mappings. R2 direct directional execution remains unsupported. Do not refit, filter by probability/year/side/regime/clock, optimize exits/stops/targets, or open another option structure.

`BLACKBOX_query_count=3`, no query #4; `production_authority=false`; `fresh_oos=false`.
