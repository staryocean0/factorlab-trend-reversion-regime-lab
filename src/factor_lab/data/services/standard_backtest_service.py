"""Project-level backtest adapter paired with the session-offset data contract.

Strategies emit signals only. This adapter chooses the execution window from
the dataset contract, keeps CloudRidge close-to-close as an optimistic
diagnostic, and refuses illegal pairings such as noon-close + next_session.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd

from factor_lab.data.session_offset_defaults import (
    DEFAULT_COMMISSION_BPS,
    DEFAULT_SLIPPAGE_BPS,
    DataContract,
    inferred_execution_window,
    validate_execution_pairing,
)
from factor_lab.portfolio.relative_performance import (
    CLOUDRIDGE_INDEX_ID,
    compute_relative_performance,
)


def _backtest_signed_signal(
    log_return: pd.Series,
    signal: pd.Series,
    *,
    buy_cost_bps: float,
    sell_cost_bps: float,
) -> pd.DataFrame:
    """Shared causal next-bar ledger for signed positions in [-1, 1]."""

    if buy_cost_bps < 0.0 or sell_cost_bps < 0.0:
        raise ValueError("transaction costs must be non-negative")
    aligned_signal = (
        pd.to_numeric(signal.reindex(log_return.index), errors="raise")
        .fillna(0.0)
        .clip(-1.0, 1.0)
    )
    position = aligned_signal.shift(1).fillna(0.0)
    change = position.diff().fillna(position)
    strategy_return = (
        position * pd.to_numeric(log_return, errors="raise").fillna(0.0)
        - change.clip(lower=0.0) * buy_cost_bps / 10_000.0
        - (-change).clip(lower=0.0) * sell_cost_bps / 10_000.0
    )
    nav = np.exp(strategy_return.cumsum())
    frame = pd.DataFrame(index=log_return.index)
    frame["signal"] = aligned_signal
    frame["position"] = position
    frame["position_change"] = change
    frame["strategy_log_return"] = strategy_return
    frame["nav"] = nav
    frame["drawdown"] = nav / nav.cummax() - 1.0
    return frame


def contract_from_metadata(metadata: Mapping[str, Any], *, frequency: str) -> DataContract:
    raw = metadata.get("data_contract")
    if isinstance(raw, Mapping):
        return DataContract(
            frequency=str(raw.get("frequency") or frequency),
            close_anchor=raw.get("close_anchor"),  # type: ignore[arg-type]
            session_offset_minutes=int(raw.get("session_offset_minutes") or 0),
            bar_align=str(raw.get("bar_align") or "session_wall_clock"),
            construction_contract=str(raw.get("construction_contract") or ""),
            signal_view=str(raw.get("signal_view") or "qfq_canonical"),
            fill_view=str(raw.get("fill_view") or "raw_canonical"),
            legacy_official_session=bool(raw.get("legacy_official_session")),
        )
    return DataContract(
        frequency=frequency,
        close_anchor=metadata.get("close_anchor"),  # type: ignore[arg-type]
        session_offset_minutes=int(metadata.get("session_offset_minutes") or 0),
        bar_align=str(metadata.get("bar_align") or "session_end_label_v2"),
        construction_contract=str(metadata.get("construction_contract") or ""),
        legacy_official_session=bool(metadata.get("legacy_official_session")),
    )


def resolve_execution_window(
    contract: DataContract,
    *,
    execution_window: str | None = None,
    optimistic_research_only: bool = False,
) -> str:
    window = execution_window or inferred_execution_window(contract)
    validate_execution_pairing(
        contract,
        window,
        optimistic_research_only=optimistic_research_only,
    )
    return window


def run_standard_backtest(
    log_return: pd.Series,
    signal: pd.Series,
    *,
    metadata: Mapping[str, Any] | None = None,
    frequency: str = "1d",
    execution_window: str | None = None,
    optimistic_research_only: bool = False,
    commission_bps: float = DEFAULT_COMMISSION_BPS,
    slippage_bps: float = DEFAULT_SLIPPAGE_BPS,
    benchmark_simple_return: pd.Series | None = None,
    benchmark_id: str = CLOUDRIDGE_INDEX_ID,
) -> dict[str, Any]:
    """Replay a signal with the project execution window.

    Signals may be signed in [-1, 1].  Positions are shifted one bar and
    turnover is charged by buy/sell direction.  Illegal data/execution
    pairings fail closed before any NAV is computed.
    """

    metadata = metadata or {}
    contract = contract_from_metadata(metadata, frequency=frequency)
    window = resolve_execution_window(
        contract,
        execution_window=execution_window,
        optimistic_research_only=optimistic_research_only,
    )
    fill_view = str(metadata.get("fill_view") or contract.fill_view)
    if fill_view.startswith("qfq"):
        raise ValueError("fill_view cannot be qfq; execution must use raw/pit prices")
    cost_bps = float(commission_bps) + float(slippage_bps)
    frame = _backtest_signed_signal(
        log_return,
        signal,
        buy_cost_bps=cost_bps,
        sell_cost_bps=cost_bps,
    )
    result: dict[str, Any] = {
        "frame": frame,
        "data_contract": contract.to_dict(),
        "execution_window": window,
        "fill_view": fill_view,
        "optimistic_research_only": optimistic_research_only,
        "commission_bps": float(commission_bps),
        "slippage_bps": float(slippage_bps),
        "signal_domain": "signed_unit_interval",
    }
    if benchmark_simple_return is not None:
        if frequency != "1d":
            raise ValueError("period_relative_performance_requires_daily_backtest")
        relative = compute_relative_performance(
            pd.Series(
                np.expm1(frame["strategy_log_return"].to_numpy(dtype=np.float64)),
                index=frame.index,
            ),
            benchmark_simple_return,
            strategy_id=str(metadata.get("strategy_id") or "standard_backtest_strategy"),
            benchmark_id=benchmark_id,
        )
        result["relative_performance"] = {
            "metadata": relative.metadata,
            "daily": relative.daily,
            "annual": relative.annual,
            "quarterly": relative.quarterly,
            "monthly": relative.monthly,
        }
    return result
