# Excerpt of /home/starryocean/桌面/量化/unified_datahub/scripts/export_factorlab_unified_index_kline_v3.py
# causal flat fill and fill available_at

# ---- export_factorlab_unified_index_kline_v3.py:49-59 ----
def _clock_range(start_minute: int, end_minute: int, step: int) -> tuple[str, ...]:
    return tuple(
        f"{minute // 60:02d}:{minute % 60:02d}"
        for minute in range(start_minute, end_minute + 1, step)
    )


ONE_MINUTE_CLOCKS = (
    *_clock_range(571, 690, 1),
    *_clock_range(781, 900, 1),
)

# ---- export_factorlab_unified_index_kline_v3.py:110-211 ----
def densify_one_minute_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["symbol"]), str(row["trading_day"]))].append(row)
    expected = EXPECTED_CLOCKS["1m_official"]
    expected_position = {clock: index for index, clock in enumerate(expected)}
    output: list[dict[str, Any]] = []
    previous_by_symbol: dict[str, dict[str, Any]] = {}
    filled_by_symbol: dict[str, int] = defaultdict(int)
    filled_day_count_by_symbol: dict[str, int] = defaultdict(int)
    excluded_symbol_days: dict[str, list[str]] = defaultdict(list)
    maximum_missing_by_symbol: dict[str, int] = defaultdict(int)
    maximum_run_by_symbol: dict[str, int] = defaultdict(int)

    for (symbol, trading_day), part in sorted(grouped.items()):
        part = sorted(part, key=lambda row: str(row["timestamp"]))
        observed = {
            str(row["timestamp"])[11:16]: dict(row)
            for row in part
            if str(row.get("timestamp") or "")[11:16] in expected_position
        }
        source_count = len(observed)
        if trading_day in KNOWN_SHORT_DAYS:
            for row in part:
                row = dict(row)
                row["causal_flat_fill"] = False
                row["source_minute_count"] = source_count
                row["high_frequency_analysis_eligible"] = False
                output.append(row)
            if part:
                previous_by_symbol[symbol] = dict(part[-1])
            excluded_symbol_days[symbol].append(trading_day)
            continue

        missing_positions = [
            expected_position[clock] for clock in expected if clock not in observed
        ]
        missing_count = len(missing_positions)
        maximum_missing_by_symbol[symbol] = max(
            maximum_missing_by_symbol[symbol], missing_count
        )
        maximum_run_by_symbol[symbol] = max(
            maximum_run_by_symbol[symbol], _max_consecutive_missing(missing_positions)
        )
        eligible = missing_count <= MAX_ELIGIBLE_MISSING_MINUTES
        if not eligible:
            excluded_symbol_days[symbol].append(trading_day)
        if missing_count:
            filled_day_count_by_symbol[symbol] += 1

        prior = previous_by_symbol.get(symbol)
        for clock in expected:
            row = observed.get(clock)
            if row is not None:
                payload = dict(row)
                payload["causal_flat_fill"] = False
            else:
                if prior is None:
                    raise ValueError(
                        f"cannot causally fill leading 1m gap: {symbol} {trading_day} {clock}"
                    )
                payload = deepcopy(prior)
                close = float(prior["close"])
                payload.update(
                    timestamp=f"{trading_day}T{clock}:00Z",
                    trading_day=trading_day,
                    open=close,
                    high=close,
                    low=close,
                    close=close,
                    volume=0.0,
                    amount=0.0,
                    available_at=f"{trading_day}T{clock}:00Z",
                    source_kind=(
                        f"{str(prior.get('source_kind') or '')}_causal_flat_missing_minute"
                    ),
                    causal_flat_fill=True,
                )
                filled_by_symbol[symbol] += 1
            payload["source_minute_count"] = source_count
            payload["high_frequency_analysis_eligible"] = eligible
            output.append(payload)
            prior = payload
        if prior is not None:
            previous_by_symbol[symbol] = prior

    global DENSE_FILL_AUDIT
    DENSE_FILL_AUDIT = {
        "policy": "prior_observed_point_flat_fill_non_circuit_breaker_v1",
        "maximum_eligible_missing_minutes": MAX_ELIGIBLE_MISSING_MINUTES,
        "filled_rows_by_symbol": dict(sorted(filled_by_symbol.items())),
        "filled_day_count_by_symbol": dict(sorted(filled_day_count_by_symbol.items())),
        "maximum_missing_minutes_by_symbol": dict(sorted(maximum_missing_by_symbol.items())),
        "maximum_consecutive_missing_by_symbol": dict(sorted(maximum_run_by_symbol.items())),
        "excluded_symbol_days": {
            symbol: sorted(set(days))
            for symbol, days in sorted(excluded_symbol_days.items())
        },
        "known_short_days_not_densified": sorted(KNOWN_SHORT_DAYS),
        "future_value_fill": False,
    }
    return sorted(output, key=lambda row: (str(row["symbol"]), str(row["timestamp"])))
