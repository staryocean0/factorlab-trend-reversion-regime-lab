# One-day ETF source observation review

Scope: user-delivered commit `6004b42b1a6d68e13ec602126292a3709d474b70`, all six files in `data/etf_microstructure_sample_20251201_v1/`, source day 2025-12-01 only. Full git clone is not a prerequisite: pinned sparse checkout, actual file hashes and row/identity checks are used. No 2026 market prices, returns, lead-lag fit, threshold search, R1_A restart or data purchase.

Before the source-content audit, the delivery manifest, dictionary and materializer excerpts were read. The terminal valid_until=15:00 code boundary was already visible. This is a defect-oriented source audit, not a blinded statistical experiment.

The audit preserves all raw rows, checks original label decoding and stable event/trade sequence, checkpoints, full displayed price ordering, invalid intervals, trade same-timestamp multiplicity and index observation gaps. Nothing is deduplicated by timestamp. No inferred quantity multiplier or monetary conversion is applied.

Source-label interval coverage is examined at already observed index times within fixed half-open continuous interiors [09:30,11:30), [13:00,14:57). These intervals are observation-accounting scopes, not a selected trading schedule. All remaining phases remain in the full-file and phase reports. Lookups require same phase, valid_from <= target < valid_until, positive finite bid/ask and displayed size, bid<=ask. Invalid terminal intervals and uncovered boundaries are not repaired or backfilled. The immutable raw files remain authoritative as delivered evidence, not a claim they are defect-free.

A covered target is ONLY an offline labelled-source state. `valid_until` was built from a subsequent state-change event; it is not independently verified real-time knowledge. Time since last state change is not quote age, receipt latency or proof of continuous source snapshots. Original snapshot and archive bytes are not present. Sparse state changes cannot prove no missing snapshots.

The already-fixed 512100 13:26 anomaly is inspected using two adjacent raw clock bins [13:25,13:26), [13:26,13:27), with exact left-boundary counts and native integer prices/quantity sums. Both bins are reported, neither is selected by OHLC similarity. This is not a reconstruction of the legacy native 1m bucket or a proof of the vendor's zero-volume cause. Cross-product numeric agreement would not independently certify exchange accuracy, units or receipt-time synchronization.

Run:

```bash
python -m unittest discover -s tests -p test_etf_one_day_review.py
python research/etf_one_day_review/audit.py --output /tmp/etf-one-day-new
```

The runner requires pyarrow; tests for pure clock/boundary functions use only the standard library. Always use a new output directory. An engineering PASS is not trading, exact-PIT, NAV-premium, complete-history or representative-sample qualification. Existing R1_A reserve and known-action impact dispositions remain unchanged.
