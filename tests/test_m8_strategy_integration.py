"""M8 synthetic integration checks against real upper-layer caller contracts.

No market data or strategy outcome is computed here. The tests prove that the
M7 trend consumer can be consumed as a read-only Layer-2 input while any
cross-interval/risk composition remains outside Layer 2.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from factor_lab.market_state.trend_regime_baseline import REASON_OK, STATUS_AVAILABLE, STATUS_UNAVAILABLE
from factor_lab.market_state.trend_regime_consumer import (
    REASON_LATEST_SNAPSHOT_EXPIRED,
    REASON_STATE_NOT_ADMITTED,
    TrendRegimeConsumer,
    build_trend_regime_snapshot,
)
from factor_lab.market_state.trend_regime_profiles import ProfileTrendRegimeResult, resolve_trend_profile

TZ = ZoneInfo("Asia/Shanghai")


def dt(hour: int, minute: int, second: int = 0) -> datetime:
    return datetime(2026, 9, 14, hour, minute, second, tzinfo=TZ)


def measurement(*, when: datetime, interval: str, profile_id: str, state: str | None, slope_t: float | None, reason: str = REASON_OK) -> ProfileTrendRegimeResult:
    profile = resolve_trend_profile(bar_interval=interval, profile_id=profile_id)
    available = state is not None and slope_t is not None and reason == REASON_OK
    return ProfileTrendRegimeResult(
        profile_id=profile_id,
        bar_interval=interval,
        layer1_view_id=profile.layer1_view_id,
        as_of=when,
        status=STATUS_AVAILABLE if available else STATUS_UNAVAILABLE,
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


def snapshot(*, symbol: str, when: datetime, interval: str, profile_id: str, state: str | None, slope_t: float | None, reason: str = REASON_OK, valid_seconds: int = 120):
    published = when + timedelta(seconds=1)
    return build_trend_regime_snapshot(
        measurement(when=when, interval=interval, profile_id=profile_id, state=state, slope_t=slope_t, reason=reason),
        symbol=symbol,
        published_at=published,
        valid_until=published + timedelta(seconds=valid_seconds),
        source_receipt_id=f"m8-synthetic-{symbol}-{profile_id}-{when.isoformat()}",
    )


def strategy_input_envelope(*, trend_by_interval: dict[str, dict[str, object]], risk: dict[str, object] | None = None) -> dict[str, object]:
    """Upper-layer test envelope: preserve inputs; deliberately make no decision."""
    payload: dict[str, object] = {"trend_by_interval": trend_by_interval}
    if risk is not None:
        payload["risk"] = dict(risk)
    return payload


def test_csi1000_upper_layer_keeps_multi_interval_states_separate():
    consumer = TrendRegimeConsumer()
    one = snapshot(symbol="000852.SH", when=dt(10, 0), interval="1m", profile_id="trend_1m_official_v1", state="UP", slope_t=3.25)
    five = snapshot(symbol="000852.SH", when=dt(10, 0), interval="5m", profile_id="trend_5m_offset0_v1", state="DOWN", slope_t=-4.0)
    consumer.ingest(one, received_at=dt(10, 0, 2))
    consumer.ingest(five, received_at=dt(10, 0, 3))
    at = dt(10, 0, 30)
    q1 = consumer.query_regime("000852.SH", at, "1m").to_dict()
    q5 = consumer.query_regime("000852.SH", at, "5m", "trend_5m_offset0_v1").to_dict()
    envelope = strategy_input_envelope(trend_by_interval={"1m": q1, "5m": q5})

    assert envelope["trend_by_interval"]["1m"]["snapshot"]["state"] == "UP"
    assert envelope["trend_by_interval"]["5m"]["snapshot"]["state"] == "DOWN"
    assert envelope["trend_by_interval"]["1m"]["snapshot"]["directional_score"] == 3.25
    assert envelope["trend_by_interval"]["5m"]["snapshot"]["directional_score"] == -4.0
    assert not {"global_state", "action", "position", "selected_strategy", "route"}.intersection(envelope)


def test_star50_trend_and_risk_remain_parallel_layer2_inputs():
    consumer = TrendRegimeConsumer()
    trend = snapshot(symbol="000688.SH", when=dt(10, 0), interval="1m", profile_id="trend_1m_official_v1", state="DOWN", slope_t=-3.75)
    consumer.ingest(trend, received_at=dt(10, 0, 2))
    trend_view = consumer.query_regime("000688.SH", dt(10, 0, 30), "1m").to_dict()
    # Mirrors the real state_degree_consumer_d5 as_of() envelope: risk state is
    # inside snapshot, while availability/authority remain top-level.
    risk_view = {
        "symbol": "000688.SH",
        "as_of": dt(10, 0, 30).isoformat(),
        "status": "AVAILABLE",
        "reason": "AVAILABLE",
        "snapshot": {"state": "UNSAFE", "state_basis": "CLOSE_CONFIRMED"},
        "production_authority": False,
    }
    envelope = strategy_input_envelope(trend_by_interval={"1m": trend_view}, risk=risk_view)

    assert envelope["trend_by_interval"]["1m"]["snapshot"]["state"] == "DOWN"
    assert envelope["risk"]["snapshot"]["state"] == "UNSAFE"
    assert "fused_state" not in envelope
    assert "action" not in envelope
    assert "position" not in envelope
    assert envelope["trend_by_interval"]["1m"]["production_authority"] is False
    assert envelope["risk"]["production_authority"] is False


def test_expired_or_unavailable_trend_is_not_substituted_with_sideways():
    consumer = TrendRegimeConsumer()
    old = snapshot(symbol="000852.SH", when=dt(10, 0), interval="1m", profile_id="trend_1m_official_v1", state="UP", slope_t=3.0, valid_seconds=900)
    newer = snapshot(symbol="000852.SH", when=dt(10, 5), interval="1m", profile_id="trend_1m_official_v1", state="DOWN", slope_t=-3.0, valid_seconds=30)
    consumer.ingest(old, received_at=dt(10, 0, 2))
    consumer.ingest(newer, received_at=dt(10, 5, 2))
    expired = consumer.query_regime("000852.SH", dt(10, 6), "1m").to_dict()
    assert expired["status"] == STATUS_UNAVAILABLE
    assert expired["reason"] == REASON_LATEST_SNAPSHOT_EXPIRED
    assert expired["snapshot"] is None
    assert expired.get("state") != "SIDEWAYS"


def test_unadmitted_profile_stays_unavailable_before_strategy_layer():
    result = TrendRegimeConsumer().query_regime("000852.SH", dt(10, 0), "15m", "trend_15m_offset5_v1").to_dict()
    assert result["status"] == STATUS_UNAVAILABLE
    assert result["reason"] == REASON_STATE_NOT_ADMITTED
    assert result["snapshot"] is None


def test_stable_snapshot_has_no_strategy_or_five_bucket_semantics():
    consumer = TrendRegimeConsumer()
    snap = snapshot(symbol="000852.SH", when=dt(10, 0), interval="1m", profile_id="trend_1m_official_v1", state="UP", slope_t=5.5)
    consumer.ingest(snap, received_at=dt(10, 0, 2))
    payload = consumer.query_regime("000852.SH", dt(10, 0, 30), "1m").to_dict()["snapshot"]
    forbidden = {"t2", "T2", "strong_state", "five_bucket_state", "global_state", "action", "position", "order", "route", "selected_strategy"}
    assert forbidden.isdisjoint(payload)
    assert payload["state"] == "UP"
    assert payload["directional_score"] == 5.5
    assert payload["strength"] == 5.5
