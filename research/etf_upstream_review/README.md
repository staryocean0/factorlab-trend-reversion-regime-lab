# Read-only review of the delivered upstream evidence

Read `docs/research/ETF_UPSTREAM_CLOUD_REVIEW_20260912.md`.

35 payload files plus the pinned manifest are verified; four excerpt ranges are compared against supplied full text. The 20 frozen anomalies are compared independently at the imported/archive, canonical and delivered-example levels. Two encodings and two views of the same upstream data are not independent providers.

The reviewed source's scalar labeling and prior-close fill functions are exercised on synthetic inputs only. The missing production settings and complete 3s minute input are NOT reconstructed; eight delivered 3s observations do not reconstruct an entire minute.

```bash
PYTHONPATH=. python -m unittest discover -s tests -p test_etf_upstream_review.py -v
PYTHONPATH=. python research/etf_upstream_review/audit.py --output /tmp/new-upstream-review
```

Use a fresh output directory. No five-year market pack, outcomes, fitting, 2026 candidate prices, vendor calls or credentials are needed. `available_at` is not a common real-time publication field across these producers. The legacy Z exception is explicitly dataset-scoped, not a replacement for normal UTC parsing.

Only the source-repository versions declared in the supplied manifest are available here. Full files/excerpts and supplied samples are verified, not unseen upstream Git repositories or original vendor archives.

A separately prepared one-day delivery request is `docs/ops/ETF_ONE_DAY_SOURCE_DELIVERY_20251201.md`. The local files are in `data/etf_microstructure_sample_20251201_v1/`. That pack does not start a backtest or buy data. R1_A remains reserved.
