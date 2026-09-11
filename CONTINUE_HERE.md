# Continue here — reversal / mean-reversion bucket

## Current state

**`PARTIAL_CARRIER_TRANSPORT`** — secondary STAR50 ETF measured; primary CSI1000 ETF remains below its frozen 2021 positive-volume gate.

Public ETF bytes now live under `data/r1a_carrier_prices/cloud_pack_v1/` (Git-tracked byte copies of the private `b656b4b` export). Cloud runners can read, hash-verify and re-admit carriers without local DataHub or `private/`.

Prior blocked receipt `docs/ops/evidence/r1a_carrier_transport_20260912/` remains historical pre-delivery evidence. Local descriptive replay remains in `r1a_carrier_transport_20260912_local/`. Public ledger audit: `r1a_carrier_cloud_audit_20260912/`. Source audit: `r1a_carrier_source_audit_20260912/`.

## Read first

1. `data/r1a_carrier_prices/cloud_pack_v1/README.md`
2. `data/r1a_carrier_prices/cloud_pack_v1/DELIVERY_CHECKLIST.json`
3. `docs/ops/evidence/r1a_carrier_source_audit_20260912/REPORT.md`
4. `docs/ops/evidence/r1a_carrier_cloud_audit_20260912/REPORT.md`
5. `docs/governance/R1A_CARRIER_PRICE_TRANSPORT_FREEZE@1.0.json`
6. `PROMPT.md`

## What is publicly delivered vs what is still blocked

**Delivered (public Git):** twelve annual OHLCV CSVs plus two corporate-action CSVs under `cloud_pack_v1/prices/`, with manifests `cloud_pack_v1/512100.SH.json` and `cloud_pack_v1/588000.SH.json`. Bytes match the earlier private export (same SHA256/rows/bytes). Zero-volume minutes are preserved.

**Still blocked at admission:** `512100.SH` 2021 positive-volume minute coverage **94.478738%** vs frozen **95%**. Source audit: **true zero-volume on the index clock** (3,220 minutes with row present and volume=0; 0 completely missing; dedup removed 0 rows for 2021). `ETF_outcomes_read=false` for 512100.

**Measured from public bytes:** `588000.SH` — `TRANSPORT_MEASURED_DESCRIPTIVE_ONLY`, 1,791/1,802 complete pairs. Re-run transport on `cloud_pack_v1` reproduces the same partial decision.

## Reproduction commands (no local DataHub)

```bash
PYTHONPATH=src:. python -m pytest -q \
  tests/test_r1a_carrier_transport.py \
  tests/test_r1a_public_delivery_audit.py \
  tests/test_r1a_delivered_ledger_regression.py \
  tests/test_r1a_cloud_pack_delivery.py
```

```bash
PYTHONPATH=src:. python research/r1a_carrier_transport/transport.py \
  --manifest-dir data/r1a_carrier_prices/cloud_pack_v1 \
  --output /tmp/r1a-cloud-replay-new
```

## Unchanged scope

Frozen maps `000852.SH -> 512100.SH`, `000688.SH -> 588000.SH`; original pairs and all `1/5/15/30/60/120/240` horizons fixed. `BLACKBOX_query_count=3`; `production_authority=false`; `fresh_oos=false`.
