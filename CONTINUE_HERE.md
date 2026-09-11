# Continue here — reversal / mean-reversion bucket

## Current state

**`PARTIAL_CARRIER_TRANSPORT`** — secondary STAR50 ETF measured locally; primary CSI1000 ETF remains below its frozen data-coverage gate.

User delivery commit: `b656b4b8cda266800b33a374d5a5c98360c51837`, building on `659c32f1216a84bf9d9da14bf017c92a9383db05`.

Cloud audit run `34624375457`: SUCCESS. Audit decision:

`PUBLIC_LEDGER_AUDIT_PASS_RAW_ETF_REPLAY_NOT_PERFORMED`

The old `BLOCKED_CARRIER_DATA_NOT_ADMITTED` receipt in `r1a_carrier_transport_20260912/` is preserved as the earlier pre-delivery state, not the current overall result.

## Read first

1. `docs/ops/evidence/r1a_carrier_cloud_audit_20260912/REPORT.md`
2. `docs/ops/evidence/r1a_carrier_cloud_audit_20260912/audit_receipt.json`
3. `docs/ops/evidence/r1a_carrier_transport_20260912_local/transport_receipt.json`
4. `docs/governance/R1A_CARRIER_PRICE_TRANSPORT_FREEZE@1.0.json`
5. `research/r1a_carrier_transport/README.md`
6. `PROMPT.md`

## What was delivered and what was independently checked

The user pushed DataHub export code, two carrier manifests, an export receipt, and the local STAR50 coverage/outcome ledger. The raw ETF OHLCV and corporate-action files remain under Git-ignored `data/r1a_carrier_prices/private/`, not in the public repository.

The cloud audit verified receipt/evidence hashes, original event-control identities, the same common sample across seven horizons, return identities, nested MFE/MAE bounds, annual/side/pooled summaries and same-sample index returns recomputed from the original verified STAR50 1m index bytes. It checked 12,537 outcome rows and 2,128 summary leaves. All return identities and independently recomputed index comparators had maximum absolute error 0 in this run.

It did NOT regenerate ETF returns from raw ETF bars or independently authenticate the upstream timestamp dictionary/corporate-action completeness. Local data-admission PASS is retained as local evidence; public arithmetic audit is not a second raw-data admission or a new empirical alpha PASS.

## Secondary carrier — 588000.SH / STAR50

Local admission: `PASS_DATA_ADMISSION_ONLY`.

Outcome: `TRANSPORT_MEASURED_DESCRIPTIVE_ONLY`.

Complete original event/control pairs: 1,791 / 1,802 = 99.3896%. Eleven pairs are explicitly excluded for event/control missing or zero-volume minutes. The same 1,791 pairs are used at every horizon.

| Index observation bars | ETF event mean bp | Same-sample index event bp | ETF incremental mean bp | Same-sample index increment bp |
|---:|---:|---:|---:|---:|
| 1 | +0.067 | +0.350 | +0.557 | +0.502 |
| 5 | +1.643 | +1.285 | +1.784 | +1.179 |
| 15 | +3.600 | +3.011 | +3.019 | +2.074 |
| 30 | +5.160 | +3.908 | +3.727 | +2.015 |
| 60 | +3.759 | +2.323 | +1.618 | -0.442 |
| 120 | +2.316 | +0.732 | +1.605 | -0.284 |
| 240 | +6.018 | +3.005 | +4.763 | +1.217 |

Increment means event return minus the ORIGINAL matched control return, not return after transaction costs. LONG and synthetic SHORT increments are both positive at 15/30 bars, but annual increments there are positive in only 3/5 years. Event medians there are zero and event positive fractions are about 48.4%/48.0%. At longer horizons the sides diverge. This is descriptive price-transport evidence, not a selected holding period, newly certified alpha, causal proof or executable profit.

STAR50 is the secondary carrier. It cannot substitute for completion of primary CSI1000 transport.

## Primary carrier — 512100.SH / CSI1000

The local delivery exists; the blocker is no longer simply failure to find a source.

Frozen positive-volume minute coverage:

- 2021: 94.478738% — below the unchanged 95% annual gate;
- 2022: 99.008264%; 2023: 99.876033%; 2024: 99.919077%; 2025: 99.996571%.

`ETF_outcomes_read=false` for 512100. No primary return table exists. Do not drop 2021, lower 95%, forward-fill zero-volume prices, switch ETFs, or call insufficient data an alpha failure.

## Exact continuation — source and coverage audit, not a new payoff search

Use the existing private DataHub files where legitimately available to document why 2021 falls short. A public-safe receipt should separate missing timestamps, explicit zero-volume minutes, invalid/filtered rows, and time/session alignment mismatches, by month and year. Verify whether zero volume is genuine absence of trades or an ingestion convention using source metadata or an authorized independent data check. True no-trade minutes are not missing trades to invent or fill.

Complete source-level evidence without changing research rules:

- raw source/delivery fingerprints and the upstream `session_end_label_v2` dictionary supporting interpretation of Z-suffixed values as Shanghai wall-clock rather than UTC;
- counts before/after session/window filtering and deduplication, including duplicate/conflicting timestamps (the current exporter uses keep-last without such a receipt);
- a complete source-backed corporate-action coverage receipt, including justification for the empty 588000 action file.

These are unresolved assurance items, not a claim that the existing local results are corrupted. If a factual mapping/source defect is established, version the correction and retain all original receipts before any replay. If 2021 zero-volume coverage is genuine, preserve the primary insufficient-data result under this freeze rather than tuning it away.

Raw ETF reproduction in a cloud runner additionally requires authorized private delivery access. Manifests/hashes and outcome ledgers alone do not supply the underlying raw files. No public raw-data upload, new subscription purchase or secret disclosure is required by this handoff.

## Reproduction commands

Public evidence audit (does not read private ETF prices):

```bash
PYTHONPATH=src:. python research/r1a_carrier_transport/audit_public_delivery.py --output /tmp/r1a-public-audit-new
```

Original transport when the manifest-referenced private files are available:

```bash
PYTHONPATH=src:. python research/r1a_carrier_transport/transport.py --output /tmp/r1a-transport-new-version
```

Use new output directories and preserve all prior evidence. No fresh historical replay is needed merely to synchronize documentation.

## Unchanged scope

R1/R2 mechanism certifications remain. R1_A is the lead historical price-alpha lane; R1_B is not a distinct standalone entry-alpha lead under the existing matched-parent study. R2 direct directional translation and all closed structural, temporal and MO payoff identities remain closed.

The frozen maps stay `000852.SH -> 512100.SH`, `000688.SH -> 588000.SH`; the original pairs, directions and all `1/5/15/30/60/120/240` observed-index-bar horizons stay fixed. Zero-cost synthetic SHORT is not a claim of real borrow/execution. Do not refit, rematch, optimize stops/targets/fees or select years/sides/horizons.

`BLACKBOX_query_count=3`; no query #4; `production_authority=false`; `fresh_oos=false`.
