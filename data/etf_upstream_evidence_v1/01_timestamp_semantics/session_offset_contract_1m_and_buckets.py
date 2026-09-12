# Excerpt of /home/starryocean/桌面/量化/unified_datahub/src/datahub/storage/query/session_offset_contract.py
# 1m forbids offset; official v2 buckets; Z first_tradable_slot

# ---- session_offset_contract.py:32-37 ----
SUPPORTED_INTRADAY_FREQUENCIES = ("5m", "15m", "30m", "60m")
SUPPORTED_DERIVED_FREQUENCIES = (*SUPPORTED_INTRADAY_FREQUENCIES, "1d")
PERIOD_MINUTES = {"5m": 5, "15m": 15, "30m": 30, "60m": 60}
CN_A_MORNING_WINDOW = (570, 690)
CN_A_AFTERNOON_WINDOW = (780, 900)
CN_A_SESSION_WINDOWS = (CN_A_MORNING_WINDOW, CN_A_AFTERNOON_WINDOW)

# ---- session_offset_contract.py:144-149 ----
    if freq == "1m":
        if offset != 0 or (anchor not in (None, DEFAULT_CLOSE_ANCHOR)):
            raise ValueError(
                "session offset / close_anchor cannot be applied to frequency=1m"
            )
        return SessionOffsetRequest(frequency=freq)

# ---- session_offset_contract.py:183-232 ----
def assign_intraday_bucket_minute(
    minute_of_day: int,
    *,
    period_minutes: int,
    offset_minutes: int = 0,
    include_tail_partial: bool = False,
) -> int | None:
    """Return the end-label minute for one 1m observation, or None to drop it."""

    for session_start, session_end in CN_A_SESSION_WINDOWS:
        if not session_start <= minute_of_day <= session_end:
            continue
        if offset_minutes == 0 and not include_tail_partial:
            # Official v2: first bucket [start, start+period], later ceil,
            # last bucket capped at session_end.  13:00 stays in the first
            # afternoon bucket.
            first_end = session_start + period_minutes
            if minute_of_day <= first_end:
                return first_end if first_end <= session_end else session_end
            raw = session_start + period_minutes * int(
                -(-int(minute_of_day - session_start) // period_minutes)
            )
            return min(session_end, raw)

        grid_start = session_start + offset_minutes
        if minute_of_day < grid_start:
            return None
        elapsed = minute_of_day - grid_start
        bucket_index = -(-elapsed // period_minutes)  # ceil, 1-based for elapsed>0
        if elapsed == 0:
            bucket_index = 1
        label = grid_start + bucket_index * period_minutes
        if label <= session_end:
            return label
        if include_tail_partial:
            return session_end
        return None
    return None


def first_tradable_slot(*, trading_day: str, bar_close_minute: int) -> str:
    """First tradable clock time after a completed bar."""

    if bar_close_minute < CN_A_MORNING_WINDOW[1]:
        return f"{trading_day}T{minute_to_hhmm(bar_close_minute)}:00Z"
    if bar_close_minute == CN_A_MORNING_WINDOW[1]:
        return f"{trading_day}T{AFTERNOON_OPEN_LABEL}:00Z"
    if bar_close_minute < CN_A_AFTERNOON_WINDOW[1]:
        return f"{trading_day}T{minute_to_hhmm(bar_close_minute)}:00Z"
    return f"{trading_day}T{minute_to_hhmm(CN_A_AFTERNOON_WINDOW[1])}:00Z"
