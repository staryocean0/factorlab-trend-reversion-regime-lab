import json
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from research.r1a_carrier_transport.transport import (
    HORIZONS, WINDOW, AdmissionError, assert_blob, validate_prices,
    checked_csv, admit, pair_clock, common_pairs, measure, summarize,
)
from research.r1a_carrier_transport.probe_sources import timestamp_summary, tushare_probe


def prices_frame(n=600):
    times = pd.date_range("2023-01-03 09:31", periods=n, freq="min", tz="Asia/Shanghai")
    return times, pd.DataFrame({"close": np.full(n, 10.0), "volume": np.ones(n)}, index=times)


def pairs_frame():
    return pd.DataFrame([{"pair_id": "p1", "symbol": "000852.SH", "event_day": "2023-01-03", "control_day": "2023-01-03", "event_entry_idx": 0, "control_entry_idx": 300, "parent_direction": 1, "side": "LONG"}])


def canonical():
    return pd.DataFrame([{"symbol": "512100.SH", "timestamp": f"{year}-01-04 10:00:00+08:00", "open": 10.0, "high": 11.0, "low": 9.0, "close": 10.0, "volume": 100.0} for year in range(2021,2026)])


def save_csv(root, name, frame):
    p = root/name; frame.to_csv(p, index=False)
    return {"path": name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size, "rows": len(frame)}


def manifest_fixture(tmp_path):
    f = canonical()
    m = {"symbol": "512100.SH", "source": "SYNTHETIC_UNIT_TEST_NOT_MARKET_DATA", "source_reference": "fixture", "frequency": "1m", "timezone": "Asia/Shanghai", "bar_label": "bar_end", "price_basis": "unadjusted_actual_traded_OHLC", "volume_unit": "shares", "zero_volume_semantics": "not_an_observed_trade", "research_use_authorized": True, "corporate_actions_complete": True, "corporate_actions_reference": "synthetic fixture has no corporate actions", "corporate_actions_window": WINDOW, "files": [save_csv(tmp_path, "prices.csv", f)], "corporate_actions_file": save_csv(tmp_path, "actions.csv", pd.DataFrame(columns=["symbol", "ex_date", "event_type", "source_reference"]))}
    p = tmp_path/"manifest.json"; p.write_text(json.dumps(m))
    times = pd.DatetimeIndex(pd.to_datetime(f.timestamp, utc=True)).tz_convert("Asia/Shanghai")
    return p, m, times


def test_documented_timezone_normalized_without_row_shift():
    f = canonical(); out = validate_prices(f, "512100.SH")
    assert out.index[0].hour == 10
    f.timestamp = pd.to_datetime(f.timestamp, utc=True).dt.strftime("%Y-%m-%d %H:%M:%S+00:00")
    assert validate_prices(f, "512100.SH").index.equals(out.index)


@pytest.mark.parametrize("col,value", [("close", float("nan")), ("close", float("inf")), ("close", 0), ("volume", -1), ("low", 12), ("high", 8), ("symbol", "000852.SH"), ("timestamp", "2026-01-05 10:00:00+08:00"), ("timestamp", "2023-01-04 12:00:00+08:00"), ("timestamp", "2023-01-04 10:00:03+08:00")])
def test_bad_carrier_prices_rejected(col, value):
    f = canonical(); f.loc[0,col] = value
    with pytest.raises(AdmissionError): validate_prices(f, "512100.SH")


def test_duplicate_prices_rejected():
    f=canonical()
    with pytest.raises(AdmissionError): validate_prices(pd.concat([f,f]), "512100.SH")


def test_hash_guard_and_path_traversal(tmp_path):
    spec=save_csv(tmp_path,"x.csv",canonical())
    checked_csv(tmp_path,spec)
    spec["sha256"]="0"*64
    with pytest.raises(AdmissionError): checked_csv(tmp_path,spec)
    spec["path"]="../x.csv"
    with pytest.raises(AdmissionError): checked_csv(tmp_path,spec)


def test_git_blob_input_is_pinned(tmp_path):
    p=tmp_path/"blob"; p.write_bytes(b"test\n")
    sha=hashlib.sha1(b"blob 5\0test\n").hexdigest(); assert_blob(p,sha)
    p.write_bytes(b"changed")
    with pytest.raises(AdmissionError): assert_blob(p,sha)


def test_missing_data_not_alpha_failure(tmp_path):
    with pytest.raises(AdmissionError, match="MISSING_CARRIER"):
        admit(tmp_path,tmp_path/"absent.json","512100.SH",pd.DatetimeIndex([]))


@pytest.mark.parametrize("key,value", [("corporate_actions_complete", False), ("bar_label", "unknown"), ("price_basis", "qfq"), ("frequency", "5m"), ("research_use_authorized", False), ("timezone", "UTC")])
def test_unresolved_source_semantics_fail_closed(tmp_path,key,value):
    p,m,t=manifest_fixture(tmp_path); m[key]=value; p.write_text(json.dumps(m))
    with pytest.raises(AdmissionError): admit(tmp_path,p,"512100.SH",t)


def test_admission_pass_means_data_only(tmp_path):
    p,m,t=manifest_fixture(tmp_path)
    tape, actions, receipt=admit(tmp_path,p,"512100.SH",t)
    assert receipt["status"]=="PASS_DATA_ADMISSION_ONLY"
    assert len(tape)==5 and actions==[]
    assert "alpha" not in receipt


def test_missing_year_cannot_pass_minute_coverage(tmp_path):
    p,m,t=manifest_fixture(tmp_path)
    m["files"]=[save_csv(tmp_path,"prices.csv",canonical().iloc[1:])]; p.write_text(json.dumps(m))
    with pytest.raises(AdmissionError,match="MINUTE_COVERAGE"): admit(tmp_path,p,"512100.SH",t)


def test_exact_clock_anchor_count_and_all_horizons():
    times,_=prices_frame(); a=pair_clock(pairs_frame(),times,"512100.SH")
    assert len(a)==16 and set(a.horizon)=={0,*HORIZONS}
    assert a.loc[(a.leg=="event") & (a.horizon==30),"index_row"].item()==30


def test_missing_etf_minute_never_shifts_clock_or_keeps_shorter_horizon():
    t,f=prices_frame(); f=f.drop(t[40])
    audit, aligned, _=common_pairs(pairs_frame(),t,f,[])
    assert not audit.eligible.item() and np.isnan(aligned[40])
    assert "event_missing" in audit.reason.item()


def test_zero_volume_not_free_fill():
    t,f=prices_frame(); f.loc[t[100],"volume"]=0
    audit,_,_=common_pairs(pairs_frame(),t,f,[])
    assert not audit.eligible.item()


def test_corporate_action_crossing_excluded_not_all_ex_date_intraday():
    t1=pd.date_range("2023-01-03 14:01",periods=60,freq="min",tz="Asia/Shanghai")
    t2=pd.date_range("2023-01-04 09:31",periods=600,freq="min",tz="Asia/Shanghai")
    t=t1.append(t2); f=pd.DataFrame({"close":10.,"volume":1.},index=t)
    audit,_,_=common_pairs(pairs_frame(),t,f,["2023-01-04"])
    assert "event_corporate_action" in audit.reason.item()
    assert "control_corporate_action" not in audit.reason.item()


def test_scaled_synthetic_carrier_exactly_preserves_returns():
    p=pairs_frame(); ix=100*np.exp(np.arange(600)*0.0001); carrier=ix*0.03
    o=measure(p,ix,carrier)
    assert len(o)==7 and tuple(o.horizon)==HORIZONS
    assert np.allclose(o.event_tracking_residual,0,atol=1e-14)
    assert np.allclose(o.incremental_tracking_residual,0,atol=1e-14)
    assert (o.etf_close_MAE==0).all() and (o.etf_close_MFE>=0).all()


def test_short_synthetic_direction_symmetry():
    p=pairs_frame(); ix=100*np.exp(np.arange(600)*0.0001)
    long=measure(p,ix,ix)
    p["parent_direction"]=-1; p["side"]="SHORT"; short=measure(p,ix,ix)
    assert np.allclose(long.etf_event,-short.etf_event)
    assert (short.etf_close_MFE==0).all()
    assert (short.etf_close_MAE<=0).all()


def test_raw_dividend_not_silently_adjusted():
    p=pairs_frame(); ix=np.full(600,100.); etf=np.full(600,10.); etf[30:241]=9.
    o=measure(p,ix,etf)
    assert np.isclose(o.loc[o.horizon==30,"etf_event"].item(),-0.1)
    # Admission/common-pair action ledger, NOT a guessed factor, removes such crossings.


def test_summary_does_not_select_horizon():
    ix=100*np.exp(np.arange(600)*0.0001); s=summarize(measure(pairs_frame(),ix,ix))
    assert tuple(map(int,s))==HORIZONS
    assert all("LONG" in x["sides"] and "SHORT" in x["sides"] for x in s.values())


def test_probe_does_not_admit_recent_data_as_history():
    x=timestamp_summary(["2026-09-11 10:00:00,10,10,10,10"])
    assert x["requested_window_rows"]==0 and x["out_of_window_rows"]==1


def test_no_tushare_credential_does_not_fake_download(monkeypatch):
    monkeypatch.delenv("TUSHARE_TOKEN",raising=False)
    assert tushare_probe()["status"]=="NOT_ATTEMPTED_AUTH_NOT_CONFIGURED"
