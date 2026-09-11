# R1_A ETF price transport

This is a price-layer study, not a trading execution strategy. The fixed carriers are `512100.SH` for `000852.SH` and `588000.SH` for `000688.SH`. The input is the already-frozen R1_A event/control pair list. Neither signals nor controls are reconstructed or optimized.

Authority: `docs/governance/R1A_CARRIER_PRICE_TRANSPORT_FREEZE@1.0.json`.

## Run

```bash
PYTHONPATH=src:. python -m pytest -q tests/test_r1a_carrier_transport.py
PYTHONPATH=src:. python research/r1a_carrier_transport/transport.py \
  --output /tmp/r1a-carrier-new-delivery
```

Use a NEW output directory for each delivered-data version. Do not overwrite historical evidence. The command returns `0` only when both carriers have been measured, `2` for an explicit missing-data / insufficient-coverage / partial-carrier state, and a nonzero error for a failed frozen-input guard. A blocked receipt is NOT a strategy FAIL. A green engineering workflow is NOT empirical alpha PASS.

A public-safe source audit can be repeated deliberately with:

```bash
PYTHONPATH=src:. python research/r1a_carrier_transport/probe_sources.py \
  --output /tmp/r1a-carrier-source-inventory.json
```

The probe requests no strategy-conditioned data. It does not enumerate secrets or circumvent a provider's permissions. An already configured `TUSHARE_TOKEN` is optional; without it, that route is explicitly `NOT_ATTEMPTED_AUTH_NOT_CONFIGURED`.

## Delivery request — can be sent to a local data agent or licensed provider

Obtain **non-event-conditioned full historical data**, not just signal dates, for:

| Carrier | Price reference | Window | Priority |
|---|---|---|---|
| `512100.SH` | CSI1000 `000852.SH` | 2021-01-01 through 2025-12-31 | Primary |
| `588000.SH` | STAR50 `000688.SH` | 2021-01-01 through 2025-12-31 | Secondary |

Required: actual unadjusted 1-minute OHLCV; timezone and bar-label dictionary; volume units and zero-volume semantics; complete source-backed cash-distribution/split ex-dates over the same window; file SHA256, bytes and row counts; permission to use the data for this research. This layer does NOT require MO data, Level-2 quotes, a broker fee schedule, borrow inventory, or a live account.

Do not use an index series renamed as an ETF, daily data, 5-minute data expanded into 1-minute rows, the latest five trading days, synthetic prices or an undocumented adjusted series. Preserve provider raw bytes separately. A documented source-specific conversion to the canonical schema is allowed; choosing timestamp shifts or adjustment factors by best correlation/returns is not.

Paid/nonpublic raw data default to `data/r1a_carrier_prices/private/`, which is Git-ignored. Public redistribution requires separate permission. Do not put tokens, account numbers or nonpublic URLs in public manifests or Git. The 49k-scale anchor output is an INTERNAL reproducibility check, not the default acquisition request.

## Canonical files and metadata

Place one manifest per carrier at `data/r1a_carrier_prices/512100.SH.json` and `data/r1a_carrier_prices/588000.SH.json`.

Price CSV columns:

```text
symbol,timestamp,open,high,low,close,volume
```

Timestamps must be documented bar-end Shanghai time, for example `2023-01-04 10:00:00+08:00`. Volume is shares. A separate source mapping must convert another physical representation before this validator. No default guess about time labels or volume units is admitted.

Corporate-action CSV columns:

```text
symbol,ex_date,event_type,source_reference
```

A header-only action file is acceptable ONLY where a complete authoritative source establishes there were no actions in the entire declared window; an empty search result is not such evidence.

Manifest shape (the placeholders are intentionally not an admitted delivery):

```json
{
  "symbol": "512100.SH",
  "source": "PENDING_REAL_PROVIDER",
  "source_reference": "PENDING_PUBLIC_DICTIONARY_OR_REDACTED_SOURCE_RECEIPT",
  "frequency": "1m",
  "timezone": "Asia/Shanghai",
  "bar_label": "bar_end",
  "price_basis": "unadjusted_actual_traded_OHLC",
  "volume_unit": "shares",
  "zero_volume_semantics": "not_an_observed_trade",
  "research_use_authorized": true,
  "corporate_actions_complete": true,
  "corporate_actions_reference": "PENDING_COMPLETE_SOURCE",
  "corporate_actions_window": {"start": "2021-01-01", "end": "2025-12-31"},
  "files": [
    {"path": "data/r1a_carrier_prices/private/512100_2021.csv", "sha256": "PENDING", "bytes": 0, "rows": 0}
  ],
  "corporate_actions_file": {
    "path": "data/r1a_carrier_prices/private/512100_actions.csv",
    "sha256": "PENDING", "bytes": 0, "rows": 0
  }
}
```

Include every delivered annual/monthly price file. Set authorization and completeness to true ONLY when verified. All paths are relative to the repository root, and path traversal is refused. The validator checks hashes, byte counts, row counts, identities, finite positive OHLC, OHLC ordering, duplicate timestamps, calendar bounds, and source semantics.

## Fixed sampling and measurement

The exact original `event_entry_idx` / `control_entry_idx` are mapped to verified index timestamps. Each horizon is an offset in the INDEX observation clock. Lunch/overnight crossings remain possible; 240 observed bars must not be silently interpreted as 240 elapsed minutes.

Primary comparison uses a common complete-pair sample across ALL seven horizons: both event and control must have valid, positive-volume ETF observations at each index timestamp from entry through 240 bars. No interpolation, forward fill, next-available-price join, or ETF row-offset shift is permitted. The denominator remains all frozen pairs. Every exclusion is reported, and index comparators are recomputed on the identical included subset.

A path crossing an ex-date (`entry_day < ex_date <= exit_day`) is excluded from the raw-price common sample and explicitly counted. An ex-date intraday path beginning after the adjustment is not automatically excluded. This avoids mistaking a mechanical distribution/split for alpha; it is NOT a factor fitted to ETF/index returns.

Coverage contracts: at least 95% valid observed minutes in each year and 80% complete frozen pairs pooled and in each event year. Data failure means insufficient coverage, not signal rejection. A separately admitted carrier can be measured while the other remains blocked.

Report event return, control return, their difference, same-sample index equivalents, ETF-minus-index residuals, close-observation MFE/MAE including zero at entry, all years, and LONG/synthetic SHORT across `1/5/15/30/60/120/240` bars. No winner or executable holding period is selected.

## Source routes verified

- Tushare official `etf_mins`: https://tushare.pro/document/2?doc_id=387 . Documents ETF 1-minute history, up to 8000 rows per request, and separate permission. A usable subscription/token is an external prerequisite, not permission to buy or use someone else's token.
- AKShare official ETF-minute interface: https://akshare.akfamily.xyz/data/fund/fund_public.html . `fund_etf_hist_min_em` documents the recent-five-trading-days limitation for 1-minute data. Date parameters do not create unavailable 2021-2025 history.
- CSI1000 ETF identity: https://www.sse.com.cn/disclosure/announcement/general/c/c_20201021_5237291.shtml . STAR50 ETF identity: https://www.chinaamc.com/fund/588000/ . These fixed identities were chosen before ETF outcomes, not by historical profitability.
- A concrete distribution example is the `512100` ex-date 2025-01-15 documented at https://www.sse.com.cn/assortment/options/mnjyzxxx/c/c_20250115_10770107.shtml . This is a metadata source only; it does not authorize option research or substitute for the complete action ledger.

## Interpretation

This is descriptive transport on already-consumed historical dates, conditional on the inherited matching design. ETF/index exposure overlap is not independent validation. The earlier matching confidence intervals were pointwise and are not proof of causal identification or immunity to multiple testing. Transport alone cannot upgrade those claims.

`BLACKBOX_query_count=3`, `production_authority=false`, `fresh_oos=false`. Existing R1_B, R2 and option closeouts are unchanged.
