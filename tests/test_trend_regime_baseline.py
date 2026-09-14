"""M2 synthetic regression tests for the frozen three-bucket baseline."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

import pytest

from factor_lab.market_state.trend_regime_baseline import (
    DEFAULT_SIDEWAYS_THRESHOLD,
    REASON_INSUFFICIENT_COMPLETED_BARS,
    REASON_INVALID_CLOSE_IN_WINDOW,
    STATE_DOWN,
    STATE_SIDEWAYS,
    STATE_UP,
    STATUS_AVAILABLE,
    STATUS_UNAVAILABLE,
    TrendRegimeBaselineConfig,
    classify_slope_t,
    measure_trend_regime_as_of,
)

START = datetime(2026, 1, 5, 1, 30, tzinfo=timezone.utc)
STEP = timedelta(minutes=5)
DELAY = timedelta(seconds=1)


def bars(closes):
    out = []
    for index, close in enumerate(closes):
        end = START + STEP * (index + 1)
        out.append(
            {
                "bar_end": end,
                "available_at": end + DELAY,
                "close": close,
            }
        )
    return out


def noisy_exponential(sign: int) -> list[float]:
    return [
        100.0
        * math.exp(sign * 0.001 * index + 0.00008 * math.sin(index * 1.7))
        for index in range(20)
    ]


def test_three_bucket_boundaries_are_frozen():
    t = DEFAULT_SIDEWAYS_THRESHOLD
    assert classify_slope_t(-t - 1e-9) == STATE_DOWN
    assert classify_slope_t(-t) == STATE_SIDEWAYS
    assert classify_slope_t(0.0) == STATE_SIDEWAYS
    assert classify_slope_t(t) == STATE_SIDEWAYS
    assert classify_slope_t(t + 1e-9) == STATE_UP


@pytest.mark.parametrize(
    ("closes", "state"),
    [
        (noisy_exponential(1), STATE_UP),
        ([100.0] * 20, STATE_SIDEWAYS),
        (noisy_exponential(-1), STATE_DOWN),
    ],
)
def test_reference_shapes_classify_deterministically(closes, state):
    rows = bars(closes)
    result = measure_trend_regime_as_of(
        rows,
        as_of=rows[-1]["available_at"],
    )
    assert result.status == STATUS_AVAILABLE
    assert result.state == state
    assert result.completed_bar_count == 20
    assert result.production_authority is False
    assert result.measurement_authority is True


def test_log_close_measurement_is_price_scale_invariant():
    closes = noisy_exponential(1)
    first = bars(closes)
    scaled = bars([value * 137.0 for value in closes])
    a = measure_trend_regime_as_of(first, as_of=first[-1]["available_at"])
    b = measure_trend_regime_as_of(scaled, as_of=scaled[-1]["available_at"])
    assert a.state == b.state
    assert a.slope_t == pytest.approx(b.slope_t, rel=0.0, abs=1e-8)
    assert a.slope_per_bar == pytest.approx(b.slope_per_bar, rel=0.0, abs=1e-12)
    assert a.r_squared == pytest.approx(b.r_squared, rel=0.0, abs=1e-12)


def test_as_of_ignores_future_and_unpublished_rows():
    prefix = bars(noisy_exponential(1))
    as_of = prefix[-1]["available_at"]
    future = []
    last_end = prefix[-1]["bar_end"]
    for index, close in enumerate([50.0, 40.0, 30.0], start=1):
        end = last_end + STEP * index
        future.append(
            {
                "bar_end": end,
                "available_at": end + DELAY,
                "close": close,
            }
        )
    base = measure_trend_regime_as_of(prefix, as_of=as_of)
    extended = measure_trend_regime_as_of(prefix + future, as_of=as_of)
    assert extended.to_dict() == base.to_dict()


def test_delayed_twentieth_bar_is_not_visible_early():
    rows = bars(noisy_exponential(1))
    rows[-1]["available_at"] = rows[-1]["bar_end"] + timedelta(minutes=30)
    early = rows[-1]["bar_end"] + timedelta(minutes=1)
    result = measure_trend_regime_as_of(rows, as_of=early)
    assert result.status == STATUS_UNAVAILABLE
    assert result.reason == REASON_INSUFFICIENT_COMPLETED_BARS
    assert result.state is None
    assert result.completed_bar_count == 19


def test_invalid_close_in_selected_window_fails_closed_without_skipping():
    closes = noisy_exponential(1)
    closes[7] = 0.0
    rows = bars(closes)
    result = measure_trend_regime_as_of(
        rows,
        as_of=rows[-1]["available_at"],
    )
    assert result.status == STATUS_UNAVAILABLE
    assert result.reason == REASON_INVALID_CLOSE_IN_WINDOW
    assert result.state is None
    assert result.slope_t is None


def test_input_order_does_not_change_measurement():
    rows = bars(noisy_exponential(-1))
    a = measure_trend_regime_as_of(rows, as_of=rows[-1]["available_at"])
    b = measure_trend_regime_as_of(
        list(reversed(rows)),
        as_of=rows[-1]["available_at"],
    )
    assert a.to_dict() == b.to_dict()


def test_naive_as_of_and_duplicate_bar_end_are_rejected():
    rows = bars(noisy_exponential(1))
    with pytest.raises(ValueError, match="timezone-aware"):
        measure_trend_regime_as_of(
            rows,
            as_of=datetime(2026, 1, 5, 3, 30),
        )
    duplicate = rows + [dict(rows[-1])]
    with pytest.raises(ValueError, match="duplicate bar_end"):
        measure_trend_regime_as_of(
            duplicate,
            as_of=rows[-1]["available_at"],
        )


def test_frozen_config_rejects_silent_semantic_drift():
    with pytest.raises(ValueError):
        TrendRegimeBaselineConfig(lookback_bars=21)
    with pytest.raises(ValueError):
        TrendRegimeBaselineConfig(sideways_threshold=2.1)
