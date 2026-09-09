# R5-B1 current-data identity adapter

Date: 2026-09-10

Status: **FROZEN BEFORE ANY LIMITED-DIAGNOSTIC OUTCOME WAS PRODUCED**

The first execution attempt stopped because the current yearly 5m files expose `timestamp`, not the historical R5 field name `bar_end_shanghai`. The second attempt renamed the field but stopped at the semantic-identity gate. No B1 breadth or monotonic-shape output was produced in either attempt.

Historical provenance resolves the timestamp semantics. In the frozen Two-Wave commit `cf8397c12a9defa243dc272224dedebe6ccd3251`, `.github/workflows/cloud-data-bridge-import.yml` records that the R5 single-file source was checked against this repository's annual CSI1000 5m partitions. That audited bridge used trend/reversion repository commit `1a573ccf87732b07686285b92db9c31257481869` and defined the current annual-file `timestamp` contract as:

> Z-tagged source strings encode Shanghai wall clock.

Therefore the only permitted current-data timestamp canonicalization for this R5 reproduction is:

1. read `timestamp` as text;
2. take the first 19 characters (`YYYY-MM-DD HH:MM:SS` wall clock);
3. parse as naive wall time;
4. localize to `Asia/Shanghai`;
5. convert to UTC;
6. compare the resulting instant row-for-row with the frozen R5 `bar_end_shanghai` parsed as UTC.

The identity gate also requires exact equality of row count, symbol, trading_day, and float64 close after deterministic timestamp sorting. No bar may be removed, inserted, shifted, or price-adjusted to force equivalence.

This is a data-contract restoration, not a model or outcome adjustment. R5 windows, lags, TRAIN/VALIDATION dates, B0/B1 models, and the preregistered limited-diagnostic gates remain unchanged.

`BLACKBOX_read=false`; `post_2020_read=false`; `production_authority=false`.
