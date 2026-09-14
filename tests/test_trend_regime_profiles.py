"""M3 synthetic regression tests for multi-interval trend profiles."""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from factor_lab.market_state.trend_regime_baseline import (
    DEFAULT_LOOKBACK_BARS,
    DEFAULT_SIDEWAYS_THRESHOLD,
    STATE_DOWN,
    STATE_UP,
    STATUS_AVAILABLE,
    STATUS_UNAVAILABLE,
)
from factor_lab.market_state.trend_regime_profiles import (
    ADMITTED_BAR_INTERVALS,
    REASON_CADENCE_GAP,
    REASON_OFF_PROFILE_GRID,
    measure_multi_interval_trend_regimes_as_of,
    measure_profile_trend_regime_as_of,
    profiles_for_interval,
    resolve_trend_profile,
    trend_regime_profiles,
)

TZ = ZoneInfo("Asia/Shanghai")
START_DATE = date(2026, 1, 5)
DELAY = timedelta(seconds=1)


def _business_days(start: date):
    current = start
    while True:
        if current.weekday() < 5:
            yield current
        current += timedelta(days=1)


def _rows(profile, count: int, *, direction: int = 1):
    rows = []
    index = 0
    for day in _business_days(START_DATE):
        for label in profile.close_times:
            if len(rows) >= count:
                return rows
            hour, minute = (int(value) for value in label.split(":"))
            bar_end = datetime(
                day.year,
                day.month,
                day.day,
                hour,
                minute,
                tzinfo=TZ,
            )
            close = 100.0 * math.exp(
                direction * 0.001 * index + 0.00008 * math.sin(index * 1.7)
            )
            rows.append(
                {
                    "view_id": profile.layer1_view_id,
                    "bar_end": bar_end,
                    "available_at": bar_end + DELAY,
                    "close": close,
                }
            )
            index += 1
    raise AssertionError("unreachable")


def test_registry_admits_requested_intervals_without_inventing_views():
    profiles = trend_regime_profiles()
    assert ADMITTED_BAR_INTERVALS == ("1m", "5m", "15m", "60m")
    assert len(profiles) == 10
    assert {interval: len(profiles_for_interval(interval)) for interval in ADMITTED_BAR_INTERVALS} == {
        "1m": 1,
        "5m": 5,
        "15m": 2,
        "60m": 2,
    }
    assert {profile.layer1_view_id for profile in profiles} == {
        "1m_official",
        "5m_offset_0",
        "5m_offset_1",
        "5m_offset_2",
        "5m_offset_3",
        "5m_offset_4",
        "15m_offset_5",
        "15m_offset_10",
        "60m_offset_30",
        "60m_offset_45",
    }
    assert all(profile.bar_construction_owner == "datahub" for profile in profiles)


def test_interval_only_resolution_is_allowed_only_when_unambiguous():
    assert resolve_trend_profile(bar_interval="1m").profile_id == "trend_1m_official_v1"
    for interval in ("5m", "15m", "60m"):
        with pytest.raises(ValueError, match="explicit profile_id is required"):
            resolve_trend_profile(bar_interval=interval)
    with pytest.raises(ValueError, match="not admitted"):
        resolve_trend_profile(
            bar_interval="15m",
            profile_id="trend_60m_offset30_v1",
        )


def test_m3_preserves_m2_math_across_all_profiles_without_private_tuning():
    profiles = trend_regime_profiles()
    assert all(profile.lookback_bars == DEFAULT_LOOKBACK_BARS for profile in profiles)
    assert all(
        profile.sideways_threshold == DEFAULT_SIDEWAYS_THRESHOLD
        for profile in profiles
    )
    assert all(profile.production_authority is False for profile in profiles)


def test_same_asof_can_expose_different_interval_states_without_global_state():
    one_minute = resolve_trend_profile(bar_interval="1m")
    five_minute = resolve_trend_profile(
        bar_interval="5m",
        profile_id="trend_5m_offset0_v1",
    )
    up_rows = _rows(one_minute, 20, direction=1)
    down_rows = _rows(five_minute, 20, direction=-1)
    as_of = max(up_rows[-1]["available_at"], down_rows[-1]["available_at"])

    result = measure_multi_interval_trend_regimes_as_of(
        {
            one_minute.profile_id: up_rows,
            five_minute.profile_id: down_rows,
        },
        as_of=as_of,
        requests=(
            ("1m", None),
            ("5m", five_minute.profile_id),
        ),
    )
    payload = result.to_dict()
    states = {
        item["profile_id"]: item["state"]
        for item in payload["measurements"]
    }
    assert states[one_minute.profile_id] == STATE_UP
    assert states[five_minute.profile_id] == STATE_DOWN
    assert "state" not in payload
    assert "global_state" not in payload
    assert result.production_authority is False


def test_profile_cadence_gap_fails_closed_instead_of_backfilling():
    profile = resolve_trend_profile(
        bar_interval="5m",
        profile_id="trend_5m_offset0_v1",
    )
    rows = _rows(profile, 21, direction=1)
    rows = rows[:10] + rows[11:]
    result = measure_profile_trend_regime_as_of(
        rows,
        as_of=rows[-1]["available_at"],
        bar_interval="5m",
        profile_id=profile.profile_id,
    )
    assert result.status == STATUS_UNAVAILABLE
    assert result.reason == REASON_CADENCE_GAP
    assert result.state is None


def test_off_profile_grid_fails_closed_and_visible_view_mismatch_is_rejected():
    profile = resolve_trend_profile(
        bar_interval="15m",
        profile_id="trend_15m_offset5_v1",
    )
    rows = _rows(profile, 20, direction=1)
    rows[8]["bar_end"] = rows[8]["bar_end"] + timedelta(minutes=1)
    rows[8]["available_at"] = rows[8]["bar_end"] + DELAY
    result = measure_profile_trend_regime_as_of(
        rows,
        as_of=rows[-1]["available_at"],
        bar_interval="15m",
        profile_id=profile.profile_id,
    )
    assert result.status == STATUS_UNAVAILABLE
    assert result.reason == REASON_OFF_PROFILE_GRID

    clean = _rows(profile, 20, direction=1)
    clean[5]["view_id"] = "15m_offset_10"
    with pytest.raises(ValueError, match="does not match profile view"):
        measure_profile_trend_regime_as_of(
            clean,
            as_of=clean[-1]["available_at"],
            bar_interval="15m",
            profile_id=profile.profile_id,
        )


def test_future_wrong_view_is_invisible_to_earlier_asof():
    profile = resolve_trend_profile(
        bar_interval="60m",
        profile_id="trend_60m_offset30_v1",
    )
    rows = _rows(profile, 20, direction=1)
    as_of = rows[-1]["available_at"]
    base = measure_profile_trend_regime_as_of(
        rows,
        as_of=as_of,
        bar_interval="60m",
        profile_id=profile.profile_id,
    )
    assert base.status == STATUS_AVAILABLE

    future = dict(rows[-1])
    future["bar_end"] = rows[-1]["bar_end"] + timedelta(days=1)
    future["available_at"] = future["bar_end"] + DELAY
    future["view_id"] = "wrong_future_view"
    extended = measure_profile_trend_regime_as_of(
        rows + [future],
        as_of=as_of,
        bar_interval="60m",
        profile_id=profile.profile_id,
    )
    assert extended.to_dict() == base.to_dict()
