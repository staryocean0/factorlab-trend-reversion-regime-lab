from scripts import m5_development_adequacy as study
from scripts.m5_development_adequacy_core import episode_adequacy, five_bucket


def test_development_window_and_profiles_are_frozen():
    assert (study.START, study.END) == ("2020-07-23", "2022-12-30")
    assert study.PROFILES == {
        "trend_1m_official_v1": "1m",
        "trend_5m_offset0_v1": "5m",
    }
    assert study.CARRIERS == ("000852.SH", "000688.SH")


def test_five_bucket_boundaries_match_m4():
    assert five_bucket(-4.01, 2.0, 4.0) == "STRONG_DOWN"
    assert five_bucket(-4.0, 2.0, 4.0) == "DOWN"
    assert five_bucket(-2.0, 2.0, 4.0) == "SIDEWAYS"
    assert five_bucket(2.0, 2.0, 4.0) == "SIDEWAYS"
    assert five_bucket(4.0, 2.0, 4.0) == "UP"
    assert five_bucket(4.01, 2.0, 4.0) == "STRONG_UP"


def test_episode_adequacy_counts_availability_without_outcomes():
    series = [(0, "UP")] * 30 + [(0, "STRONG_UP")] * 30 + [(0, None)] + [(1, "DOWN")] * 30
    result = episode_adequacy(series)
    assert result["episode_counts"]["UP"]["total"] == 1
    assert result["episode_counts"]["STRONG_UP"]["complete_20"] == 1
    assert result["episode_counts"]["DOWN"]["complete_20"] == 1
    assert result["episode_counts"]["STRONG_DOWN"]["total"] == 0
