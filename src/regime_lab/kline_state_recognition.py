"""Causal K-line state recognition and offline visual-reference scoring.

The online recognizer is strictly prefix-only.  The centered visual oracle is
allowed to inspect a fixed local future radius, but only for evaluation; oracle
fields must never become recognizer inputs.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right, insort
from collections import deque
from dataclasses import dataclass
import math

import numpy as np
import pandas as pd

CONCRETE_STATES = ("UpTrend", "DownTrend", "Range", "Shock")
ALL_STATES = (*CONCRETE_STATES, "Uncertain")
EVENT_COLUMNS = (
    "source",
    "symbol",
    "trading_day",
    "from_state",
    "to_state",
    "change_start_time",
    "event_time",
    "bar_ordinal_day",
)


@dataclass(frozen=True, slots=True)
class RecognitionConfig:
    short_window: int = 6
    primary_window: int = 24
    reference_history: int = 480
    oracle_radius: int = 12
    bdci_trend_threshold: float = 60.0
    bdci_range_threshold: float = 40.0
    trend_efficiency_threshold: float = 0.30
    range_efficiency_threshold: float = 0.20
    dii_trend_threshold: float = 1.25
    shock_vol_rank: float = 0.90
    shock_abs_return_rank: float = 0.995
    transition_confirm_bars: int = 2
    transition_tolerance_bars: int = 3

    def __post_init__(self) -> None:
        if self.short_window < 2:
            raise ValueError("short_window must be >= 2")
        if self.primary_window <= self.short_window:
            raise ValueError("primary_window must be greater than short_window")
        if self.reference_history < 100:
            raise ValueError("reference_history must be >= 100")
        if self.oracle_radius * 2 != self.primary_window:
            raise ValueError("oracle centered width must match primary return window")
        if self.transition_confirm_bars < 1:
            raise ValueError("transition_confirm_bars must be >= 1")
        if self.transition_tolerance_bars < 0:
            raise ValueError("transition_tolerance_bars must be >= 0")


def _as_shanghai(series: pd.Series) -> pd.Series:
    values = pd.to_datetime(series, errors="raise")
    if getattr(values.dt, "tz", None) is None:
        return values.dt.tz_localize("Asia/Shanghai")
    return values.dt.tz_convert("Asia/Shanghai")


def _truthy(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes"})


def _quality_mask(frame: pd.DataFrame) -> pd.Series:
    mask = pd.Series(True, index=frame.index)
    if "high_frequency_analysis_eligible" in frame.columns:
        mask &= _truthy(frame["high_frequency_analysis_eligible"])
    if "causal_flat_fill" in frame.columns:
        mask &= ~_truthy(frame["causal_flat_fill"])
    if "source_minute_count" in frame.columns:
        count = pd.to_numeric(frame["source_minute_count"], errors="coerce")
        mask &= count.ge(1)
    return mask


def _continuous_session_mask(times: pd.Series) -> pd.Series:
    minute = times.dt.hour * 60 + times.dt.minute
    return minute.between(9 * 60 + 30, 11 * 60 + 30) | minute.between(13 * 60, 15 * 60)


def _lunch_bridge(previous: pd.Timestamp, current: pd.Timestamp) -> bool:
    if previous.date() != current.date():
        return False
    p = previous.hour * 60 + previous.minute
    c = current.hour * 60 + current.minute
    return p == 11 * 60 + 30 and c in {13 * 60, 13 * 60 + 5}


def prepare_market_frame(market: pd.DataFrame) -> pd.DataFrame:
    """Validate/filter 5m OHLC input and mark contiguous trading-bar runs."""
    required = {
        "symbol",
        "trading_day",
        "market_time_shanghai",
        "open",
        "high",
        "low",
        "close",
    }
    missing = required - set(market.columns)
    if missing:
        raise ValueError(f"market data missing columns: {sorted(missing)}")

    frame = market.copy()
    frame["market_time_shanghai"] = _as_shanghai(frame["market_time_shanghai"])
    if (frame["market_time_shanghai"].dt.year >= 2026).any():
        raise ValueError("2026 rows are outside the frozen data role")
    frame = frame.loc[_quality_mask(frame)].copy()
    frame = frame.loc[_continuous_session_mask(frame["market_time_shanghai"])].copy()
    frame = frame.sort_values(["symbol", "market_time_shanghai"], kind="stable").reset_index(drop=True)

    for column in ("open", "high", "low", "close"):
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    if (frame[["open", "high", "low", "close"]] <= 0).any().any():
        raise ValueError("non-positive OHLC value")
    if (frame["high"] < frame[["open", "close", "low"]].max(axis=1)).any():
        raise ValueError("OHLC high invariant failed")
    if (frame["low"] > frame[["open", "close", "high"]].min(axis=1)).any():
        raise ValueError("OHLC low invariant failed")
    if frame.duplicated(["symbol", "market_time_shanghai"]).any():
        raise ValueError("duplicate symbol/timestamp market rows")

    run_ids = np.zeros(len(frame), dtype=np.int64)
    run = 0
    previous_symbol: str | None = None
    previous_time: pd.Timestamp | None = None
    for i, row in enumerate(frame[["symbol", "market_time_shanghai"]].itertuples(index=False)):
        symbol = str(row.symbol)
        current = row.market_time_shanghai
        contiguous = False
        if previous_symbol == symbol and previous_time is not None:
            delta = current - previous_time
            contiguous = delta == pd.Timedelta(minutes=5) or _lunch_bridge(previous_time, current)
        if not contiguous:
            run += 1
        run_ids[i] = run
        previous_symbol = symbol
        previous_time = current
    frame["contiguous_run_id"] = run_ids
    frame["bar_ordinal_day"] = frame.groupby(["symbol", "trading_day"], sort=False).cumcount().astype("int64")
    return frame


def _causal_rank_against_reference(
    current: pd.Series,
    reference: pd.Series,
    *,
    history: int,
) -> pd.Series:
    """Rank current[i] against the previous `history` finite reference values."""
    cur = pd.to_numeric(current, errors="coerce").to_numpy(float)
    ref = pd.to_numeric(reference, errors="coerce").to_numpy(float)
    out = np.full(len(cur), np.nan, dtype=float)
    queue: deque[float] = deque()
    ordered: list[float] = []

    for i in range(len(cur)):
        value = cur[i]
        if math.isfinite(value) and len(queue) >= history:
            out[i] = bisect_right(ordered, float(value)) / float(len(ordered))

        ref_value = ref[i]
        if math.isfinite(ref_value):
            ref_value = float(ref_value)
            queue.append(ref_value)
            insort(ordered, ref_value)
            if len(queue) > history:
                old = queue.popleft()
                pos = bisect_left(ordered, old)
                ordered.pop(pos)

    return pd.Series(out, index=current.index, dtype="float64")


def _signed_efficiency(log_close: pd.Series, returns: pd.Series, window: int) -> pd.Series:
    net = log_close - log_close.shift(window)
    path = returns.abs().rolling(window, min_periods=window).sum()
    return net / path.where(path > 0)


def _bdci(returns: pd.Series, window: int) -> pd.Series:
    sign = np.sign(returns)
    previous = sign.shift(1)
    pair_valid = sign.ne(0) & previous.ne(0) & sign.notna() & previous.notna()
    switched = pair_valid & sign.ne(previous)
    opportunities = pair_valid.astype(float).rolling(window - 1, min_periods=window - 1).sum()
    switches = switched.astype(float).rolling(window - 1, min_periods=window - 1).sum()
    return 100.0 * (1.0 - switches / opportunities.where(opportunities > 0))


def _dii(returns: pd.Series, efficiency: pd.Series, window: int) -> pd.Series:
    net = returns.rolling(window, min_periods=window).sum()
    energy = np.sqrt((returns * returns).rolling(window, min_periods=window).sum())
    impulse = net / energy.where(energy > 0)
    return impulse * (0.5 + 0.5 * efficiency.abs().clip(0.0, 1.0))


def _bar_geometry(frame: pd.DataFrame, short_window: int) -> pd.DataFrame:
    open_ = frame["open"].to_numpy(float)
    high = frame["high"].to_numpy(float)
    low = frame["low"].to_numpy(float)
    close = frame["close"].to_numpy(float)
    log_range = np.log(high / low)
    body = np.abs(np.log(close / open_))
    upper = np.log(high / np.maximum(open_, close))
    lower = np.log(np.minimum(open_, close) / low)
    body_ratio = np.divide(body, log_range, out=np.zeros_like(body), where=log_range > 0)
    upper_share = np.divide(upper, log_range, out=np.zeros_like(upper), where=log_range > 0)
    lower_share = np.divide(lower, log_range, out=np.zeros_like(lower), where=log_range > 0)
    price_range = high - low
    clv = np.divide(2.0 * close - high - low, price_range, out=np.zeros_like(close), where=price_range > 0)
    return pd.DataFrame(
        {
            "body_to_range": body_ratio,
            "wick_imbalance": lower_share - upper_share,
            "close_location_value": clv,
        },
        index=frame.index,
    ).rolling(short_window, min_periods=short_window).median()


def build_causal_features(
    prepared: pd.DataFrame,
    *,
    config: RecognitionConfig | None = None,
) -> pd.DataFrame:
    """Build prefix-only K-line features without bridging missing trading bars."""
    cfg = config or RecognitionConfig()
    parts: list[pd.DataFrame] = []
    for _, group in prepared.groupby(["symbol", "contiguous_run_id"], sort=False):
        group = group.copy()
        log_close = np.log(group["close"].astype(float))
        returns = log_close.diff()
        eff_short = _signed_efficiency(log_close, returns, cfg.short_window)
        eff_primary = _signed_efficiency(log_close, returns, cfg.primary_window)
        bdci = _bdci(returns, cfg.primary_window)
        dii = _dii(returns, eff_primary, cfg.primary_window)
        rv = np.sqrt((returns * returns).rolling(cfg.primary_window, min_periods=cfg.primary_window).sum())
        geometry = _bar_geometry(group, cfg.short_window)

        group["log_return_1"] = returns
        group["abs_log_return_1"] = returns.abs()
        group[f"signed_efficiency_{cfg.short_window}"] = eff_short
        group[f"signed_efficiency_{cfg.primary_window}"] = eff_primary
        group[f"bdci_{cfg.primary_window}"] = bdci
        group[f"dii_{cfg.primary_window}"] = dii
        group[f"realized_volatility_{cfg.primary_window}"] = rv
        group[f"body_to_range_ratio_{cfg.short_window}"] = geometry["body_to_range"]
        group[f"wick_imbalance_{cfg.short_window}"] = geometry["wick_imbalance"]
        group[f"close_location_value_{cfg.short_window}"] = geometry["close_location_value"]
        parts.append(group)

    out = pd.concat(parts, ignore_index=True) if parts else prepared.copy()
    out = out.sort_values(["symbol", "market_time_shanghai"], kind="stable").reset_index(drop=True)
    rv_col = f"realized_volatility_{cfg.primary_window}"
    out["volatility_rank_prior480"] = np.nan
    out["abs_return_rank_prior480"] = np.nan
    for _, indices in out.groupby("symbol", sort=False).groups.items():
        loc = list(indices)
        out.loc[loc, "volatility_rank_prior480"] = _causal_rank_against_reference(
            out.loc[loc, rv_col], out.loc[loc, rv_col], history=cfg.reference_history
        ).to_numpy()
        out.loc[loc, "abs_return_rank_prior480"] = _causal_rank_against_reference(
            out.loc[loc, "abs_log_return_1"],
            out.loc[loc, "abs_log_return_1"],
            history=cfg.reference_history,
        ).to_numpy()
    return out


def _direction_vote(values: tuple[float, float, float]) -> int:
    signs = [int(np.sign(value)) for value in values if math.isfinite(float(value)) and value != 0]
    positive = sum(value > 0 for value in signs)
    negative = sum(value < 0 for value in signs)
    if positive >= 2 and positive > negative:
        return 1
    if negative >= 2 and negative > positive:
        return -1
    return 0


def classify_state(
    *,
    efficiency_short: float,
    efficiency_primary: float,
    bdci: float,
    dii: float,
    volatility_rank: float,
    abs_return_rank: float,
    config: RecognitionConfig | None = None,
) -> str:
    """Apply the frozen transparent online/oracle semantic state rule."""
    cfg = config or RecognitionConfig()
    required = (
        efficiency_short,
        efficiency_primary,
        bdci,
        dii,
        volatility_rank,
        abs_return_rank,
    )
    if not all(math.isfinite(float(value)) for value in required):
        return "Uncertain"

    if volatility_rank >= cfg.shock_vol_rank or abs_return_rank >= cfg.shock_abs_return_rank:
        return "Shock"

    vote = _direction_vote((efficiency_short, efficiency_primary, dii))
    trend_evidence = (
        bdci >= cfg.bdci_trend_threshold
        and abs(efficiency_primary) >= cfg.trend_efficiency_threshold
    ) or abs(dii) >= cfg.dii_trend_threshold
    if trend_evidence and vote > 0:
        return "UpTrend"
    if trend_evidence and vote < 0:
        return "DownTrend"

    if (
        bdci <= cfg.bdci_range_threshold
        and abs(efficiency_primary) <= cfg.range_efficiency_threshold
        and abs(dii) < cfg.dii_trend_threshold
    ):
        return "Range"
    return "Uncertain"


def classify_online_states(
    features: pd.DataFrame,
    *,
    config: RecognitionConfig | None = None,
) -> pd.DataFrame:
    cfg = config or RecognitionConfig()
    short = f"signed_efficiency_{cfg.short_window}"
    primary = f"signed_efficiency_{cfg.primary_window}"
    bdci = f"bdci_{cfg.primary_window}"
    dii = f"dii_{cfg.primary_window}"
    out = features.copy()
    out["online_state"] = [
        classify_state(
            efficiency_short=float(es) if pd.notna(es) else math.nan,
            efficiency_primary=float(ep) if pd.notna(ep) else math.nan,
            bdci=float(b) if pd.notna(b) else math.nan,
            dii=float(d) if pd.notna(d) else math.nan,
            volatility_rank=float(v) if pd.notna(v) else math.nan,
            abs_return_rank=float(a) if pd.notna(a) else math.nan,
            config=cfg,
        )
        for es, ep, b, d, v, a in zip(
            out[short],
            out[primary],
            out[bdci],
            out[dii],
            out["volatility_rank_prior480"],
            out["abs_return_rank_prior480"],
            strict=False,
        )
    ]
    return out


def _window_geometry(log_close: np.ndarray) -> tuple[float, float, float, float]:
    returns = np.diff(log_close)
    if len(returns) == 0 or not np.isfinite(returns).all():
        return math.nan, math.nan, math.nan, math.nan
    path = float(np.abs(returns).sum())
    net = float(log_close[-1] - log_close[0])
    efficiency = net / path if path > 0 else 0.0
    signs = np.sign(returns)
    valid = (signs[1:] != 0) & (signs[:-1] != 0)
    opportunities = int(valid.sum())
    if opportunities > 0:
        switches = int(((signs[1:] != signs[:-1]) & valid).sum())
        bdci = 100.0 * (1.0 - switches / opportunities)
    else:
        bdci = math.nan
    energy = math.sqrt(float(np.square(returns).sum()))
    impulse = net / energy if energy > 0 else 0.0
    dii = impulse * (0.5 + 0.5 * min(abs(efficiency), 1.0))
    return efficiency, bdci, dii, energy


def build_visual_oracle(
    online: pd.DataFrame,
    *,
    config: RecognitionConfig | None = None,
) -> pd.DataFrame:
    """Create centered visual-reference labels for offline evaluation only."""
    cfg = config or RecognitionConfig()
    out = online.copy()
    n = len(out)
    oracle_eff = np.full(n, np.nan)
    oracle_bdci = np.full(n, np.nan)
    oracle_dii = np.full(n, np.nan)
    oracle_rv = np.full(n, np.nan)

    for _, indices in out.groupby(["symbol", "contiguous_run_id"], sort=False).groups.items():
        loc = np.asarray(list(indices), dtype=int)
        logs = np.log(out.loc[loc, "close"].to_numpy(float))
        radius = cfg.oracle_radius
        for local_i in range(radius, len(loc) - radius):
            window = logs[local_i - radius : local_i + radius + 1]
            efficiency, bdci, dii, rv = _window_geometry(window)
            global_i = loc[local_i]
            oracle_eff[global_i] = efficiency
            oracle_bdci[global_i] = bdci
            oracle_dii[global_i] = dii
            oracle_rv[global_i] = rv

    out["oracle_signed_efficiency_24"] = oracle_eff
    out["oracle_bdci_24"] = oracle_bdci
    out["oracle_dii_24"] = oracle_dii
    out["oracle_realized_volatility_24"] = oracle_rv
    out["oracle_volatility_rank_prior480"] = np.nan
    out["oracle_abs_return_rank_prior480"] = out["abs_return_rank_prior480"]

    rv_ref = f"realized_volatility_{cfg.primary_window}"
    for _, indices in out.groupby("symbol", sort=False).groups.items():
        loc = list(indices)
        out.loc[loc, "oracle_volatility_rank_prior480"] = _causal_rank_against_reference(
            out.loc[loc, "oracle_realized_volatility_24"],
            out.loc[loc, rv_ref],
            history=cfg.reference_history,
        ).to_numpy()

    out["oracle_state"] = [
        classify_state(
            efficiency_short=float(e) if pd.notna(e) else math.nan,
            efficiency_primary=float(e) if pd.notna(e) else math.nan,
            bdci=float(b) if pd.notna(b) else math.nan,
            dii=float(d) if pd.notna(d) else math.nan,
            volatility_rank=float(v) if pd.notna(v) else math.nan,
            abs_return_rank=float(a) if pd.notna(a) else math.nan,
            config=cfg,
        )
        for e, b, d, v, a in zip(
            out["oracle_signed_efficiency_24"],
            out["oracle_bdci_24"],
            out["oracle_dii_24"],
            out["oracle_volatility_rank_prior480"],
            out["oracle_abs_return_rank_prior480"],
            strict=False,
        )
    ]
    return out


def build_state_timeseries(
    market: pd.DataFrame,
    *,
    config: RecognitionConfig | None = None,
) -> pd.DataFrame:
    cfg = config or RecognitionConfig()
    prepared = prepare_market_frame(market)
    features = build_causal_features(prepared, config=cfg)
    online = classify_online_states(features, config=cfg)
    return build_visual_oracle(online, config=cfg)


def confirmed_states_and_events(
    frame: pd.DataFrame,
    *,
    label_column: str,
    source: str,
    config: RecognitionConfig | None = None,
) -> tuple[pd.Series, pd.DataFrame]:
    """Debounce concrete state changes and return transition events."""
    cfg = config or RecognitionConfig()
    confirmed = pd.Series("Uncertain", index=frame.index, dtype=object)
    events: list[dict[str, object]] = []

    for (symbol, day), indices in frame.groupby(["symbol", "trading_day"], sort=False).groups.items():
        loc = list(indices)
        stable: str | None = None
        pending: str | None = None
        pending_count = 0
        pending_start: int | None = None
        for idx in loc:
            label = str(frame.at[idx, label_column])
            if label not in CONCRETE_STATES:
                pending = None
                pending_count = 0
                pending_start = None
                confirmed.at[idx] = stable if stable is not None else "Uncertain"
                continue
            if stable is not None and label == stable:
                pending = None
                pending_count = 0
                pending_start = None
                confirmed.at[idx] = stable
                continue
            if pending == label:
                pending_count += 1
            else:
                pending = label
                pending_count = 1
                pending_start = idx
            if pending_count >= cfg.transition_confirm_bars:
                old = stable
                stable = label
                if old is not None and old != stable:
                    events.append(
                        {
                            "source": source,
                            "symbol": str(symbol),
                            "trading_day": str(day),
                            "from_state": old,
                            "to_state": stable,
                            "change_start_time": frame.at[pending_start, "market_time_shanghai"],
                            "event_time": frame.at[idx, "market_time_shanghai"],
                            "bar_ordinal_day": int(frame.at[idx, "bar_ordinal_day"]),
                        }
                    )
                pending = None
                pending_count = 0
                pending_start = None
            confirmed.at[idx] = stable if stable is not None else "Uncertain"
    return confirmed, pd.DataFrame(events, columns=EVENT_COLUMNS)


def _safe_f1(precision: float, recall: float) -> float:
    if not math.isfinite(precision) or not math.isfinite(recall):
        return math.nan
    if precision + recall == 0.0:
        return 0.0
    return 2.0 * precision * recall / (precision + recall)


def compare_transition_events(
    online_events: pd.DataFrame,
    oracle_events: pd.DataFrame,
    *,
    tolerance_bars: int = 3,
) -> tuple[pd.DataFrame, dict[str, float | int]]:
    """One-to-one nearest matching by asset/day/destination state."""
    online = online_events.reindex(columns=EVENT_COLUMNS).copy().reset_index(drop=True)
    oracle = oracle_events.reindex(columns=EVENT_COLUMNS).copy().reset_index(drop=True)
    online["matched"] = False
    oracle["matched"] = False
    online["match_id"] = pd.NA
    oracle["match_id"] = pd.NA
    matches: list[dict[str, object]] = []
    match_id = 0

    for oi, row in oracle.iterrows():
        candidates = online.loc[
            (~online["matched"])
            & online["symbol"].eq(row["symbol"])
            & online["trading_day"].eq(row["trading_day"])
            & online["to_state"].eq(row["to_state"])
        ].copy()
        if candidates.empty:
            continue
        candidates["distance"] = (candidates["bar_ordinal_day"] - int(row["bar_ordinal_day"])).abs()
        candidates = candidates.loc[candidates["distance"] <= tolerance_bars]
        if candidates.empty:
            continue
        best_idx = int(candidates.sort_values(["distance", "bar_ordinal_day"], kind="stable").index[0])
        match_id += 1
        online.at[best_idx, "matched"] = True
        oracle.at[oi, "matched"] = True
        online.at[best_idx, "match_id"] = match_id
        oracle.at[oi, "match_id"] = match_id
        delay = int(online.at[best_idx, "bar_ordinal_day"] - row["bar_ordinal_day"])
        matches.append(
            {
                "match_id": match_id,
                "symbol": row["symbol"],
                "trading_day": row["trading_day"],
                "to_state": row["to_state"],
                "oracle_time": row["event_time"],
                "online_time": online.at[best_idx, "event_time"],
                "delay_bars": delay,
                "delay_minutes": delay * 5,
            }
        )

    tp = int(online["matched"].sum()) if not online.empty else 0
    fp = int((~online["matched"]).sum()) if not online.empty else 0
    fn = int((~oracle["matched"]).sum()) if not oracle.empty else 0
    precision = tp / (tp + fp) if tp + fp else math.nan
    recall = tp / (tp + fn) if tp + fn else math.nan
    f1 = _safe_f1(float(precision), float(recall))
    matched = pd.DataFrame(matches)
    metrics: dict[str, float | int] = {
        "online_transition_count": int(len(online)),
        "oracle_transition_count": int(len(oracle)),
        "matched_transition_count": tp,
        "transition_precision": float(precision),
        "transition_recall": float(recall),
        "transition_f1": float(f1),
        "median_detection_delay_bars": float(matched["delay_bars"].median()) if not matched.empty else math.nan,
        "median_detection_delay_minutes": float(matched["delay_minutes"].median()) if not matched.empty else math.nan,
    }
    combined = pd.concat(
        [
            oracle.assign(event_role="oracle"),
            online.assign(event_role="online"),
        ],
        ignore_index=True,
        sort=False,
    )
    return combined, metrics


def _classification_tables(
    frame: pd.DataFrame,
) -> tuple[dict[str, float | int], pd.DataFrame, pd.DataFrame]:
    scored = frame.loc[frame["oracle_state"].isin(CONCRETE_STATES)].copy()
    if scored.empty:
        return {}, pd.DataFrame(), pd.DataFrame()
    y_true = scored["oracle_state"].astype(str)
    y_pred = scored["online_state"].astype(str)
    concrete_pred = y_pred.isin(CONCRETE_STATES)

    confusion = pd.DataFrame(0, index=CONCRETE_STATES, columns=ALL_STATES, dtype=int)
    for truth, prediction in zip(y_true, y_pred, strict=False):
        if truth in confusion.index and prediction in confusion.columns:
            confusion.at[truth, prediction] += 1

    rows: list[dict[str, object]] = []
    recalls: list[float] = []
    f1s: list[float] = []
    for state in CONCRETE_STATES:
        tp = int(((y_true == state) & (y_pred == state)).sum())
        fp = int(((y_true != state) & (y_pred == state)).sum())
        fn = int(((y_true == state) & (y_pred != state)).sum())
        support = int((y_true == state).sum())
        precision = tp / (tp + fp) if tp + fp else math.nan
        recall = tp / (tp + fn) if tp + fn else math.nan
        f1 = _safe_f1(float(precision), float(recall))
        if math.isfinite(recall):
            recalls.append(recall)
        if math.isfinite(f1):
            f1s.append(f1)
        rows.append(
            {
                "state": state,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "support": support,
                "predicted_count": int((y_pred == state).sum()),
            }
        )

    summary: dict[str, float | int] = {
        "n_scored": int(len(scored)),
        "online_concrete_coverage": float(concrete_pred.mean()),
        "exact_accuracy_including_abstention": float((y_true == y_pred).mean()),
        "conditional_accuracy_when_online_concrete": float((y_true[concrete_pred] == y_pred[concrete_pred]).mean()) if concrete_pred.any() else math.nan,
        "balanced_accuracy_4state": float(np.mean(recalls)) if len(recalls) == len(CONCRETE_STATES) else math.nan,
        "macro_f1_4state": float(np.mean(f1s)) if len(f1s) == len(CONCRETE_STATES) else math.nan,
    }
    return summary, confusion, pd.DataFrame(rows)


def score_recognition(
    state_timeseries: pd.DataFrame,
    *,
    config: RecognitionConfig | None = None,
) -> tuple[dict[str, object], pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Score point-state recognition, yearly stability and transitions."""
    cfg = config or RecognitionConfig()
    frame = state_timeseries.copy()
    point_summary, confusion, per_state = _classification_tables(frame)

    online_confirmed, online_events = confirmed_states_and_events(
        frame, label_column="online_state", source="online", config=cfg
    )
    oracle_confirmed, oracle_events = confirmed_states_and_events(
        frame, label_column="oracle_state", source="oracle", config=cfg
    )
    frame["online_confirmed_state"] = online_confirmed
    frame["oracle_confirmed_state"] = oracle_confirmed
    transition_table, transition_summary = compare_transition_events(
        online_events,
        oracle_events,
        tolerance_bars=cfg.transition_tolerance_bars,
    )
    days = max(1, frame[["symbol", "trading_day"]].drop_duplicates().shape[0])
    transition_summary["false_transitions_per_day"] = (
        float((transition_table["event_role"].eq("online") & ~transition_table["matched"]).sum()) / days
        if not transition_table.empty
        else 0.0
    )

    yearly_rows: list[dict[str, object]] = []
    years = pd.to_datetime(frame["trading_day"], errors="raise").dt.year
    for year in sorted(years.unique()):
        part = frame.loc[years.eq(year)]
        yearly, _, state_rows = _classification_tables(part)
        if not yearly:
            continue
        yearly_rows.append(
            {
                "year": int(year),
                **yearly,
                "min_state_support": int(state_rows["support"].min()) if not state_rows.empty else 0,
            }
        )

    summary: dict[str, object] = {**point_summary, **transition_summary}
    return summary, confusion, per_state, pd.DataFrame(yearly_rows), transition_table


def assess_capability_level(asset_results: dict[str, dict[str, object]]) -> dict[str, object]:
    """Apply the frozen project maturity rubric; v1 can never award Level 5."""
    if set(asset_results) != {"000852.SH", "000688.SH"}:
        return {"level": "inconclusive", "reason": "both frozen assets are required"}

    failures_l3: list[str] = []
    failures_l4: list[str] = []
    for symbol, result in asset_results.items():
        bal = float(result.get("balanced_accuracy_4state", math.nan))
        trans = float(result.get("transition_f1", math.nan))
        coverage = float(result.get("online_concrete_coverage", math.nan))
        min_support = int(result.get("min_state_support", 0))
        yearly_median = float(result.get("eligible_year_balanced_accuracy_median", math.nan))
        yearly_min = float(result.get("eligible_year_balanced_accuracy_min", math.nan))
        eligible_years = int(result.get("eligible_year_count", 0))

        if not math.isfinite(bal) or bal < 0.55:
            failures_l3.append(f"{symbol}: balanced_accuracy < 0.55")
        if not math.isfinite(trans) or trans < 0.40:
            failures_l3.append(f"{symbol}: transition_F1 < 0.40")
        if not math.isfinite(coverage) or coverage < 0.60:
            failures_l3.append(f"{symbol}: concrete coverage < 0.60")
        if min_support < 100:
            failures_l3.append(f"{symbol}: at least one concrete state support < 100")

        if not math.isfinite(bal) or bal < 0.70:
            failures_l4.append(f"{symbol}: balanced_accuracy < 0.70")
        if not math.isfinite(trans) or trans < 0.60:
            failures_l4.append(f"{symbol}: transition_F1 < 0.60")
        if not math.isfinite(coverage) or coverage < 0.75:
            failures_l4.append(f"{symbol}: concrete coverage < 0.75")
        if eligible_years < 3:
            failures_l4.append(f"{symbol}: fewer than 3 eligible yearly stability slices")
        if not math.isfinite(yearly_median) or yearly_median < 0.60:
            failures_l4.append(f"{symbol}: yearly median balanced_accuracy < 0.60")
        if not math.isfinite(yearly_min) or yearly_min < 0.50:
            failures_l4.append(f"{symbol}: an eligible year balanced_accuracy < 0.50")

    if not failures_l4 and not failures_l3:
        return {"level": "Level 4", "reason": "all frozen Level-4 gates passed", "failures": []}
    if not failures_l3:
        return {"level": "Level 3", "reason": "all frozen Level-3 gates passed", "failures": failures_l4}
    return {"level": "Level 2", "reason": "end-to-end recognizer scored but Level-3 gates failed", "failures": failures_l3}


__all__ = [
    "ALL_STATES",
    "CONCRETE_STATES",
    "RecognitionConfig",
    "assess_capability_level",
    "build_causal_features",
    "build_state_timeseries",
    "build_visual_oracle",
    "classify_online_states",
    "classify_state",
    "compare_transition_events",
    "confirmed_states_and_events",
    "prepare_market_frame",
    "score_recognition",
]
