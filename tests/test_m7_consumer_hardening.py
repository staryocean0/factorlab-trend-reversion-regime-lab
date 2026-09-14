from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from factor_lab.market_state.trend_regime_consumer import (
    CURRENT_ADMISSION_RECEIPT_ID,
    CURRENT_PROVIDER_ID,
    CURRENT_SOURCE_DATASET_ID,
    SUPPORTED_SYMBOLS,
    TrendProviderAdmission,
    build_trend_regime_snapshot,
)
from factor_lab.market_state.trend_regime_profiles import ProfileTrendRegimeResult, resolve_trend_profile

TZ = ZoneInfo("Asia/Shanghai")


def _measurement() -> ProfileTrendRegimeResult:
    when = datetime(2026, 9, 14, 10, 0, tzinfo=TZ)
    profile = resolve_trend_profile(bar_interval="1m", profile_id="trend_1m_official_v1")
    return ProfileTrendRegimeResult(
        profile_id=profile.profile_id,
        bar_interval=profile.bar_interval,
        layer1_view_id=profile.layer1_view_id,
        as_of=when,
        status="AVAILABLE",
        reason="OK",
        state="UP",
        slope_t=3.0,
        slope_per_bar=0.001,
        r_squared=0.8,
        completed_bar_count=20,
        observation_time=when,
        available_at=when,
        lookback_bars=20,
        sideways_threshold=2.0,
    )


def test_m7_v1_provider_registry_cannot_be_expanded_by_constructor():
    with pytest.raises(ValueError, match="provider admission is frozen"):
        TrendProviderAdmission(
            provider_id=CURRENT_PROVIDER_ID,
            source_dataset_id=CURRENT_SOURCE_DATASET_ID,
            admission_receipt_id=CURRENT_ADMISSION_RECEIPT_ID,
            admitted_symbols=SUPPORTED_SYMBOLS,
            admitted_profiles=("trend_1m_official_v1", "trend_5m_offset0_v1", "trend_15m_offset5_v1"),
        )


def test_source_receipt_id_is_required_and_not_stringified():
    measurement = _measurement()
    published = measurement.as_of + timedelta(seconds=1)
    for bad in ("", "   ", None):
        with pytest.raises(ValueError, match="source_receipt_id is required"):
            build_trend_regime_snapshot(
                measurement,
                symbol="000852.SH",
                published_at=published,
                valid_until=published + timedelta(minutes=1),
                source_receipt_id=bad,  # type: ignore[arg-type]
            )
