from dataclasses import replace
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from factor_lab.market_state.trend_regime_baseline import REASON_OK, STATUS_AVAILABLE, STATUS_UNAVAILABLE
from factor_lab.market_state.trend_regime_consumer import (
    REASON_LATEST_SNAPSHOT_EXPIRED,
    REASON_NO_PUBLISHED_SNAPSHOT,
    REASON_STATE_NOT_ADMITTED,
    REASON_UNSUPPORTED_PROFILE,
    REASON_UNSUPPORTED_SYMBOL,
    TrendRegimeConsumer,
    TrendSnapshotStore,
    build_trend_regime_snapshot,
)
from factor_lab.market_state.trend_regime_profiles import ProfileTrendRegimeResult, resolve_trend_profile
from factor_lab.market_state.trend_regime_representation import REPRESENTATION_SCHEMA_ID

TZ = ZoneInfo("Asia/Shanghai")


def dt(hour: int, minute: int, second: int = 0) -> datetime:
    return datetime(2026, 9, 14, hour, minute, second, tzinfo=TZ)


def measurement(
    *,
    when: datetime,
    interval: str = "1m",
    profile_id: str = "trend_1m_official_v1",
    status: str = STATUS_AVAILABLE,
    reason: str = REASON_OK,
    state: str | None = "UP",
    slope_t: float | None = 3.5,
) -> ProfileTrendRegimeResult:
    profile = resolve_trend_profile(bar_interval=interval, profile_id=profile_id)
    available = status == STATUS_AVAILABLE
    return ProfileTrendRegimeResult(
        profile_id=profile_id,
        bar_interval=interval,
        layer1_view_id=profile.layer1_view_id,
        as_of=when,
        status=status,
        reason=reason,
        state=state if available else None,
        slope_t=slope_t if available else None,
        slope_per_bar=0.001 if available else None,
        r_squared=0.8 if available else None,
        completed_bar_count=20,
        observation_time=when if available else None,
        available_at=when if available else None,
        lookback_bars=20,
        sideways_threshold=2.0,
    )


def snapshot(
    *,
    when: datetime,
    interval: str = "1m",
    profile_id: str = "trend_1m_official_v1",
    status: str = STATUS_AVAILABLE,
    reason: str = REASON_OK,
    state: str | None = "UP",
    slope_t: float | None = 3.5,
    published_delay_seconds: int = 1,
    valid_for_seconds: int = 60,
):
    published = when + timedelta(seconds=published_delay_seconds)
    return build_trend_regime_snapshot(
        measurement(
            when=when,
            interval=interval,
            profile_id=profile_id,
            status=status,
            reason=reason,
            state=state,
            slope_t=slope_t,
        ),
        symbol="000852.SH",
        published_at=published,
        valid_until=published + timedelta(seconds=valid_for_seconds),
        source_receipt_id=f"receipt-{profile_id}-{when.isoformat()}",
    )


def test_available_query_delivers_only_m6_representation():
    snap = snapshot(when=dt(10, 0), slope_t=4.25)
    consumer = TrendRegimeConsumer()
    assert consumer.ingest(snap, received_at=dt(10, 0, 2)) is True
    result = consumer.query_regime("000852.SH", dt(10, 0, 30), "1m")
    assert result.status == STATUS_AVAILABLE
    assert result.reason == REASON_OK
    payload = result.to_dict()["snapshot"]
    assert payload["state"] == "UP"
    assert payload["directional_score"] == 4.25
    assert payload["strength"] == 4.25
    assert payload["representation_schema_id"] == REPRESENTATION_SCHEMA_ID
    assert payload["production_authority"] is False
    assert payload["trading_action_authority"] is False
    assert "t2" not in payload
    assert "strong_state" not in payload
    assert payload["state"] not in {"STRONG_UP", "STRONG_DOWN"}


def test_received_visibility_is_causal():
    snap = snapshot(when=dt(10, 0))
    consumer = TrendRegimeConsumer()
    consumer.ingest(snap, received_at=dt(10, 0, 20))
    before = consumer.query_regime("000852.SH", dt(10, 0, 10), "1m")
    after = consumer.query_regime("000852.SH", dt(10, 0, 30), "1m")
    assert before.status == STATUS_UNAVAILABLE
    assert before.reason == REASON_NO_PUBLISHED_SNAPSHOT
    assert after.status == STATUS_AVAILABLE


def test_latest_expired_never_falls_back_to_older_still_valid_snapshot():
    older = snapshot(when=dt(10, 0), valid_for_seconds=900)
    newer = snapshot(when=dt(10, 5), valid_for_seconds=30)
    consumer = TrendRegimeConsumer()
    consumer.ingest(older, received_at=dt(10, 0, 2))
    consumer.ingest(newer, received_at=dt(10, 5, 2))
    result = consumer.query_regime("000852.SH", dt(10, 6), "1m")
    assert result.status == STATUS_UNAVAILABLE
    assert result.reason == REASON_LATEST_SNAPSHOT_EXPIRED
    assert result.snapshot is None


def test_latest_explicit_unavailable_never_falls_back():
    older = snapshot(when=dt(10, 0), valid_for_seconds=900)
    newer = snapshot(
        when=dt(10, 5),
        status=STATUS_UNAVAILABLE,
        reason="CADENCE_GAP",
        state=None,
        slope_t=None,
        valid_for_seconds=300,
    )
    consumer = TrendRegimeConsumer()
    consumer.ingest(older, received_at=dt(10, 0, 2))
    consumer.ingest(newer, received_at=dt(10, 5, 2))
    result = consumer.query_regime("000852.SH", dt(10, 6), "1m")
    assert result.status == STATUS_UNAVAILABLE
    assert result.reason == "CADENCE_GAP"
    assert result.snapshot is None


def test_duplicate_is_idempotent_but_conflicting_duplicate_is_rejected():
    snap = snapshot(when=dt(10, 0))
    store = TrendSnapshotStore()
    assert store.ingest(snap, received_at=dt(10, 0, 2)) is True
    assert store.ingest(snap, received_at=dt(10, 0, 3)) is False
    conflicting = replace(snap, valid_until=snap.valid_until + timedelta(seconds=30))
    with pytest.raises(ValueError, match="conflicting duplicate"):
        store.ingest(conflicting, received_at=dt(10, 0, 4))


def test_source_and_receipt_order_are_append_only():
    later = snapshot(when=dt(10, 5))
    earlier = snapshot(when=dt(10, 0))
    store = TrendSnapshotStore()
    store.ingest(later, received_at=dt(10, 5, 2))
    with pytest.raises(ValueError, match="out-of-order source snapshot"):
        store.ingest(earlier, received_at=dt(10, 5, 3))

    other = snapshot(
        when=dt(10, 3),
        interval="5m",
        profile_id="trend_5m_offset0_v1",
    )
    with pytest.raises(ValueError, match="out-of-order receipt"):
        store.ingest(other, received_at=dt(10, 4))


def test_profile_resolution_and_current_provider_admission_fail_closed():
    consumer = TrendRegimeConsumer()
    ambiguous = consumer.query_regime("000852.SH", dt(10, 0), "5m")
    assert ambiguous.status == STATUS_UNAVAILABLE
    assert ambiguous.reason == REASON_UNSUPPORTED_PROFILE

    not_admitted = consumer.query_regime(
        "000852.SH",
        dt(10, 0),
        "15m",
        "trend_15m_offset5_v1",
    )
    assert not_admitted.status == STATUS_UNAVAILABLE
    assert not_admitted.reason == REASON_STATE_NOT_ADMITTED

    phase_not_admitted = consumer.query_regime(
        "000852.SH",
        dt(10, 0),
        "5m",
        "trend_5m_offset1_v1",
    )
    assert phase_not_admitted.reason == REASON_STATE_NOT_ADMITTED


def test_unsupported_symbol_is_unavailable_not_market_state():
    consumer = TrendRegimeConsumer()
    result = consumer.query_regime("BAD", dt(10, 0), "1m")
    assert result.status == STATUS_UNAVAILABLE
    assert result.reason == REASON_UNSUPPORTED_SYMBOL
    assert result.snapshot is None


def test_unadmitted_profile_cannot_be_published_with_current_provider():
    m = measurement(
        when=dt(10, 0),
        interval="15m",
        profile_id="trend_15m_offset5_v1",
    )
    with pytest.raises(ValueError, match="not admitted"):
        build_trend_regime_snapshot(
            m,
            symbol="000852.SH",
            published_at=dt(10, 0, 1),
            valid_until=dt(10, 15),
            source_receipt_id="receipt",
        )


def test_publication_and_expiry_clocks_are_strict():
    m = measurement(when=dt(10, 0))
    with pytest.raises(ValueError, match="published before"):
        build_trend_regime_snapshot(
            m,
            symbol="000852.SH",
            published_at=dt(9, 59, 59),
            valid_until=dt(10, 1),
            source_receipt_id="receipt",
        )
    with pytest.raises(ValueError, match="valid_until"):
        build_trend_regime_snapshot(
            m,
            symbol="000852.SH",
            published_at=dt(10, 0, 1),
            valid_until=dt(10, 0, 1),
            source_receipt_id="receipt",
        )


def test_query_payload_is_a_fresh_copy():
    snap = snapshot(when=dt(10, 0))
    consumer = TrendRegimeConsumer()
    consumer.ingest(snap, received_at=dt(10, 0, 2))
    first = consumer.query_regime("000852.SH", dt(10, 0, 30), "1m").to_dict()
    first["snapshot"]["state"] = "DOWN"
    second = consumer.query_regime("000852.SH", dt(10, 0, 30), "1m").to_dict()
    assert second["snapshot"]["state"] == "UP"


def test_timezone_awareness_is_mandatory():
    consumer = TrendRegimeConsumer()
    with pytest.raises(ValueError, match="timezone-aware"):
        consumer.query_regime("000852.SH", datetime(2026, 9, 14, 10, 0), "1m")
