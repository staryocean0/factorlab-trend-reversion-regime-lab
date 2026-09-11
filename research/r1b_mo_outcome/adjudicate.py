"""Sealed viability gates for the frozen R1B MO outcome study."""
from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np
import pandas as pd

GATE_YEARS = ("2023", "2024", "2025")
REPORT_ONLY_YEAR = "2022"


def _year(value: str) -> str:
    return str(value)[:4]


def adjudicate(ledger: pd.DataFrame) -> dict[str, Any]:
    missing = Counter(ledger.loc[ledger["status"] != "completed_two_leg", "status"].astype(str))
    completed = ledger.loc[ledger["status"].eq("completed_two_leg")].copy()
    completed["year"] = completed["entry_day"].map(_year)
    nets = completed["net_cny"].to_numpy(float) if not completed.empty else np.array([], dtype=float)
    pooled_mean = float(np.mean(nets)) if len(nets) else float("nan")
    pooled_median = float(np.median(nets)) if len(nets) else float("nan")
    annual: dict[str, dict[str, Any]] = {}
    positive_gate_years = 0
    for year in ("2022", "2023", "2024", "2025"):
        block = completed.loc[completed["year"].eq(year), "net_cny"].to_numpy(float)
        mean_net = float(np.mean(block)) if len(block) else float("nan")
        median_net = float(np.median(block)) if len(block) else float("nan")
        votes = year in GATE_YEARS
        positive = bool(len(block) and mean_net > 0.0)
        if votes and positive:
            positive_gate_years += 1
        annual[year] = {
            "n_completed": int(len(block)),
            "mean_net_cny": mean_net,
            "median_net_cny": median_net,
            "votes": votes,
            "mean_net_positive": positive,
        }
    gates = {
        "pooled_mean_net_cny_positive": bool(len(nets) and pooled_mean > 0.0),
        "pooled_median_net_cny_positive": bool(len(nets) and pooled_median > 0.0),
        "annual_mean_net_positive_min_2_of_3": positive_gate_years >= 2,
    }
    passed = bool(all(gates.values()))
    return {
        "n_events": int(len(ledger)),
        "n_completed_two_leg": int(len(completed)),
        "missingness_counts": dict(missing),
        "exit_class_counts": completed["exit_class"].value_counts().astype(int).to_dict() if not completed.empty else {},
        "pooled_mean_net_cny": pooled_mean,
        "pooled_median_net_cny": pooled_median,
        "annual": annual,
        "positive_gate_years": positive_gate_years,
        "gate_years": list(GATE_YEARS),
        "report_only_year": REPORT_ONLY_YEAR,
        "gates": gates,
        "passed": passed,
        "decision": "PASS" if passed else "FAIL_IDENTITY_CLOSED",
        "fresh_oos": False,
        "production_authority": False,
        "blackbox_query_count": 3,
        "blackbox_query_4_authorized": False,
    }
