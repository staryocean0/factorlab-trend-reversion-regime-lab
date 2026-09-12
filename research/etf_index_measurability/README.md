# ETF/index measurability — no repair backtest

Read `docs/research/ETF_INDEX_MEASURABILITY_REVIEW_20260912.md` and the source-quality advisory before interpreting the preserved outputs.

Decision: `MEASUREMENT_SCREEN_COMPLETED_MICROSTRUCTURE_IDENTIFICATION_BLOCKED`.

The arithmetic describes same-label, within-session consecutive-minute relative price CHANGE magnitudes. It does not measure level NAV premium, equilibrium value, mean reversion, price-discovery leadership or executable spread profits. The .001 CNY reference tick is neither a bid/ask spread nor a hard noise bound.

The existing index sources contain upstream causal-flat-fill markers. The existing 512100 action ledger omits the documented 2022-09-02 share consolidation and trading suspension. Replaying old bytes does not certify their action completeness. Nothing here overwrites the old pack or revives R1_A.

Reproduce in NEW output directories:

```bash
PYTHONPATH=src:. python -m pytest -q tests/test_etf_index_measurability.py tests/test_etf_measurement_retained.py
PYTHONPATH=src:. python research/etf_index_measurability/audit.py \
  --output /tmp/etf-measurement-new \
  --reference docs/ops/evidence/etf_index_measurability_20260912
PYTHONPATH=src:. python research/etf_index_measurability/source_flags.py \
  --output /tmp/etf-source-flags-new
```

The reference hashes pin the 22 local source files through the immutable manifests. Exact source scope is ten 2021-2025 index1m partitions and the 12 delivered ETF/action CSVs. No old event ledgers, 3s/2026/MO or new fitted model are needed. Repository path inventory inspects names only; a filename is not admitted ETF bid/ask data.

The supplemental source inspection was deliberately added after the first schema audit exposed fill/as-of fields. It does not modify the original measurement masks or output. Compare its three CSVs and receipt file hashes separately.

## Concrete external-data contract, NOT a purchase request

Before another study, qualify existing-source access to a predeclared small contiguous period, with all records rather than only apparent deviations:

1. ETF L1 best bid/ask and sizes, exchange quote timestamps, last-trade timestamps and conditions, update sequence/correction rules and vendor availability timestamps.
2. Matching index values and publication/as-of timestamps. For a NAV-premium question, timed IOPV and its methodology/publication lag, or auditable constituent basket/cash/action valuation. Daily final NAV or a scaled index level is not contemporaneous NAV evidence.
3. Documented timezone and bar inclusion rules; volume units/rounding/placeholder semantics; index native-versus-filled observations; complete cash distribution, split/consolidation and suspension history.

Do not re-upload the same minute OHLCV files, shift timestamps to maximize correlation, infer spread from ticks/ranges, or treat zero-volume OHLC as proven exchange no-trade. A new action ledger must be a separate version and accompanied by an affected-output audit. No other stage begins automatically.

The read-only regression is engineering reproduction, not a positive strategy result. `BLACKBOX_query_count=3`, no production/fresh-OOS authority; R1_A remains reserved.
