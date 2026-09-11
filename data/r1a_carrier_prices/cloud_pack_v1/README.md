# R1_A ETF public cloud pack v1

Git-tracked byte copies of the local private DataHub export (`b656b4b` lineage).
No OHLCV imputation, no zero-volume fill, no timestamp shift.

- Prices: `data/r1a_carrier_prices/cloud_pack_v1/prices/*.csv`
- Manifests: `data/r1a_carrier_prices/cloud_pack_v1/512100.SH.json`, `data/r1a_carrier_prices/cloud_pack_v1/588000.SH.json`
- Checklist: `data/r1a_carrier_prices/cloud_pack_v1/DELIVERY_CHECKLIST.json`

Cloud replay (does not change blocked primary admission):

```bash
PYTHONPATH=src:. python research/r1a_carrier_transport/transport.py \
  --manifest-dir data/r1a_carrier_prices/cloud_pack_v1 \
  --output /tmp/r1a-cloud-replay-new
```

`512100.SH` may remain `INSUFFICIENT_CARRIER_MINUTE_COVERAGE` for 2021; that is
separate from whether these bytes are publicly readable.
