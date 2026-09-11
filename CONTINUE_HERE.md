# Continue here — reversal / mean-reversion research

## Latest completed work

**`ENDPOINT_DIAGNOSTIC_COMPLETE_DESCRIPTIVE`**

Both fixed ETFs now have all seven horizon-specific observed-endpoint price diagnostics measured in the cloud. This is not a full-path admission PASS, significance certificate or live strategy.

The earlier full-path protocol remains **`PARTIAL_CARRIER_TRANSPORT` under its own unchanged definition**. Do not use that historical label to imply the new endpoint diagnostic is still waiting for local data or that 512100 has never had any ETF returns measured.

Read first:

1. `docs/research/R1A_ENDPOINT_METHOD_REVIEW_20260912.md`
2. `docs/ops/evidence/r1a_endpoint_diagnostic_20260912/REPORT.md`
3. `docs/ops/evidence/r1a_endpoint_diagnostic_20260912/endpoint_receipt.json`
4. `docs/governance/R1A_ENDPOINT_PRICE_DIAGNOSTIC_FREEZE@1.0.json`
5. `PROMPT.md`

Decisive Actions run `34630965766`, job `103367406954`: SUCCESS. Separate freeze commit `6687f9fa7000e02b03a0d5a7a4a65d9a63359116` preceded new endpoint outcomes. The prior index/588000 outcomes and old coverage had already been seen and are disclosed in the freeze.

## What changed, and what did not

Terminal paired returns use four prices: event entry/exit and original control entry/exit. Interior nontrading/missing observations do not enter that algebra. Complete-path MFE/MAE or path exits are different estimands and were not computed here.

The new diagnostic checks source RECORD coverage >=95% in each year, then positive-volume EXACT endpoint pair coverage >=80% pooled and in every event year, separately for each fixed horizon. Zero-volume rows count only as source records and are NEVER valid return endpoints. This is a separate sampling contract, not the original positive-volume annual gate being relabeled PASS.

All original R1_A pairs, directions, carriers, timestamp alignment and horizons `1/5/15/30/60/120/240` are unchanged. No fills, nearest quotes, year removal, ETF replacement, refitting or control rematching. Corporate-action crossings remain excluded using the unchanged delivered action tables.

Endpoint eligibility uses future exit availability, so it is a retrospective conditional sample, not a tradable entry filter. Per-horizon samples can differ. Same-sample index comparators and full/eligible/excluded index composition are reported explicitly.

## Primary: CSI1000 / 512100.SH

All seven endpoint gates passed. Pooled coverage is 97.15%-98.07%; worst individual year/horizon coverage is 85.48%. No 2021 deletion.

| h | included / 1296 | ETF event bp | ETF control bp | ETF increment bp | same-sample index increment bp |
|---:|---:|---:|---:|---:|---:|
| 1 | 1271 | +0.344 | +1.206 | -0.861 | -0.449 |
| 5 | 1268 | +1.926 | +0.942 | +0.984 | +1.112 |
| 15 | 1268 | +5.007 | +0.638 | +4.368 | +3.894 |
| 30 | 1259 | +7.739 | +0.665 | +7.074 | +6.527 |
| 60 | 1261 | +6.901 | -0.076 | +6.976 | +7.198 |
| 120 | 1265 | +7.236 | +0.209 | +7.026 | +6.697 |
| 240 | 1261 | +5.371 | +1.240 | +4.131 | +4.397 |

15/30-bar increments are positive in 4/5 and 5/5 years, with positive LONG and synthetic SHORT increments. They are descriptive locations in a fixed surface, NOT selected holding periods. Longer-horizon annual/side stability is weaker; 1-bar increment is negative and 240-bar SHORT increment is negative.

Selection caveat: at h30, full-original-pair index increment +6.074bp becomes +6.527bp in the eligible subset; about +0.453bp is an observable composition shift. The ETF adds approximately +0.547bp relative to that same-sample index. Excluded ETF outcomes remain unknown; high coverage does not prove missingness is random.

The all-seven-endpoint common intersection is 1192/1296 overall but only 60.22% in 2021. Its separate common-sample gate FAILS and its ETF outcomes were NOT opened. Do not claim all primary horizon rows are the same cohort.

## Secondary: STAR50 / 588000.SH

All seven endpoint gates passed with 1801-1802/1802 pairs. ETF increments at 15/30 bars are +3.118/+3.963bp versus index +2.128/+2.195bp. Both sides are positive there, but annual increment means are positive only 3/5 years.

The common-endpoint sensitivity passes with 1799/1802 pairs; 15/30-bar ETF increments on that common sample are +3.024/+3.813bp. This is related secondary transport, not independent confirmation. No fresh OOS or execution result exists.

## Current research frontier

The fixed R1_A signal's short-horizon conditional price response and matched-parent increment are visible in ETF prices. The next unresolved layer is **dependence and observation-selection robustness before execution economics**, not another data-transfer cycle or a redesigned signal.

Any further inference must separately freeze treatment of overlapping return windows, reused controls, calendar clustering, historical research reuse and the multiple-horizon surface. Do not casually call the current means statistically established, causally identified, all-event alpha or net profits. Do not select a preferred horizon from these tables.

No new uncertainty test, MFE/MAE, stops/targets, costs, borrow/T+1 mechanics, futures or options were opened in this diagnostic.

## Data and reproduction

`data/r1a_carrier_prices/cloud_pack_v1/` contains the actual public data: 10 annual OHLCV CSVs and 2 action CSVs, 583,943 price rows. No private/ directory or DataHub is needed. Do not request routine local re-delivery.

```bash
PYTHONPATH=src:. python research/r1a_carrier_transport/endpoint_diagnostic.py --output /tmp/r1a-endpoint-new
PYTHONPATH=src:. python -m pytest -q tests/test_r1a_*.py
```

Use fresh output directories. Old `transport.py` and `verify_cloud_replay.py` remain unchanged and reproduce the original full-path partial result. New endpoint evidence has its own directory.

Canonical source semantics are inherited. Recorded volume=0 versus independently confirmed exchange no-trade remains unresolved; do not invent upstream proof.

## Preserved authority and history

R1/R2 mechanism certification remains. R1_B does not acquire standalone entry alpha from its delayed raw returns. R2 directional execution and all previously closed structural/temporal/MO identities remain closed.

Retain prior index validity, matched attribution, pre-delivery, local replay, public-ledger audit, source audit and cloud-raw replay evidence. The old full-path insufficiency is not rewritten.

`BLACKBOX_query_count=3`; no query #4; `production_authority=false`; `fresh_oos=false`.
