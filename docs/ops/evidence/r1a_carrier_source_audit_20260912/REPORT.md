# R1_A ETF source delivery audit

Pack: `data/r1a_carrier_prices/cloud_pack_v1`

## 512100.SH 2021 attribution

- Index minutes expected: 58320
- Present on index clock: 58320
- Completely missing: 0
- Present zero volume: 3220
- Present positive volume: 55100
- Record coverage: 100.000000%
- Positive-volume coverage: 94.478738%
- Conclusion: **TRUE_ZERO_VOLUME_ON_INDEX_CLOCK**

Categories on the index clock are mutually exclusive: missing | zero-volume | positive-volume.

## Timestamp chain

Upstream stores `trading_dayTHH:MM:00Z` under session_end_label_v2; export strips `Z` and localizes Asia/Shanghai (not UTC convert).

## Deduplication 512100 2021

{
  "raw_rows": 58563,
  "unique_timestamps_before_dedup": 58563,
  "duplicate_timestamp_rows": 0,
  "duplicate_groups": 0,
  "conflicting_duplicate_groups": 0,
  "conflict_samples": [],
  "rows_after_keep_last": 58563,
  "rows_removed_by_dedup": 0
}
