"""Schema/clock preflight for the v0.14.2 3-second execution-clock bridge.

No strategy result is produced. This script only inspects the supplied CSI1000
3s observations and their alignment to the frozen 1m/5m measurement planes.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from regime_lab.market_data import load_market_data

OUT = Path("artifacts/reversal_3s_schema_audit_v0_14_2")
OUT.mkdir(parents=True, exist_ok=True)

SYMBOL = "000852.SH"
START = "2025-01-02"
END = "2025-01-10"


def main() -> None:
    f3 = load_market_data(SYMBOL, "3s", START, END)
    f1 = load_market_data(SYMBOL, "1m", START, END)
    f5 = load_market_data(SYMBOL, "5m", START, END)

    print("=== 3S COLUMNS ===")
    print(list(f3.columns))
    print("=== 3S DTYPES ===")
    print(f3.dtypes.astype(str).to_string())
    print("=== 3S FIRST ROWS ===")
    print(f3.head(12).to_string(index=False))

    duplicate_clock = f3["market_time_shanghai"].duplicated(keep=False)
    print("=== CLOCK DENSITY ===")
    print({
        "rows_3s": len(f3),
        "days_3s": int(f3["trading_day"].nunique()),
        "duplicate_clock_rows": int(duplicate_clock.sum()),
        "duplicate_clock_times": int(f3.loc[duplicate_clock, "market_time_shanghai"].nunique()),
        "first_time": str(f3["market_time_shanghai"].min()),
        "last_time": str(f3["market_time_shanghai"].max()),
    })

    numeric_summary = {}
    for col in f3.columns:
        x = pd.to_numeric(f3[col], errors="coerce")
        n = int(x.notna().sum())
        if n:
            numeric_summary[col] = {
                "non_null_numeric": n,
                "min": float(x.min()),
                "max": float(x.max()),
                "nunique": int(x.nunique(dropna=True)),
            }
    print("=== NUMERIC FIELD SUMMARY ===")
    print(json.dumps(numeric_summary, indent=2, ensure_ascii=False))

    # For each 1m/5m timestamp, count 3s observations sharing the same minute
    # and inspect exact clock intersections without assigning bar semantics.
    t3 = f3["market_time_shanghai"]
    minute3 = t3.dt.floor("min")
    minute_counts = minute3.value_counts()
    one_minute = f1["market_time_shanghai"].dt.floor("min")
    five_minute = f5["market_time_shanghai"].dt.floor("min")
    print("=== ALIGNMENT COUNTS ===")
    print({
        "1m_rows": len(f1),
        "1m_minutes_with_any_3s": int(one_minute.isin(minute_counts.index).sum()),
        "1m_exact_clock_in_3s": int(f1["market_time_shanghai"].isin(set(t3)).sum()),
        "5m_rows": len(f5),
        "5m_minutes_with_any_3s": int(five_minute.isin(minute_counts.index).sum()),
        "5m_exact_clock_in_3s": int(f5["market_time_shanghai"].isin(set(t3)).sum()),
        "median_3s_rows_per_observed_minute": float(minute_counts.median()) if len(minute_counts) else None,
        "min_3s_rows_per_observed_minute": int(minute_counts.min()) if len(minute_counts) else None,
        "max_3s_rows_per_observed_minute": int(minute_counts.max()) if len(minute_counts) else None,
    })

    pd.DataFrame({"column": f3.columns, "dtype": f3.dtypes.astype(str).to_numpy()}).to_csv(
        OUT / "schema.csv", index=False
    )
    f3.head(200).to_csv(OUT / "sample_rows.csv", index=False)


if __name__ == "__main__":
    main()
