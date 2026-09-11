import numpy as np
import pandas as pd
import pytest
from research.r1a_carrier_transport.endpoint_diagnostic import (
    HORIZONS, YEARS, EndpointError, endpoint_availability, coverage_gate,
    measure_endpoints, analyse, report,
)


def fixture_data():
    times = []
    pairs = []
    for year in YEARS:
        offset = len(times)
        for day in (4, 5, 6):
            times.extend(pd.date_range(f"{year}-01-{day:02d} 09:31", periods=120, freq="min", tz="Asia/Shanghai"))
            times.extend(pd.date_range(f"{year}-01-{day:02d} 13:01", periods=120, freq="min", tz="Asia/Shanghai"))
        for j, side in enumerate(("LONG", "SHORT")):
            pairs.append({"pair_id": f"p{year}{j}", "symbol": "000852.SH", "event_day": f"{year}-01-04",
                          "control_day": f"{year}-01-05", "side": side, "parent_direction": 1 if j == 0 else -1,
                          "event_entry_idx": offset+10+j, "control_entry_idx": offset+300+j})
    times = pd.DatetimeIndex(times)
    index_px = 100*np.exp(np.arange(len(times))*.00001)
    tape = pd.DataFrame({"close": index_px*.02, "volume": 100.0}, index=times)
    return pd.DataFrame(pairs), times, index_px, tape


def test_complete_synthetic_integration_all_horizons_and_common_sample():
    p,t,ix,tape=fixture_data()
    result,audit,ledger,common=analyse(p,t,ix,tape,[])
    assert len(audit)==len(ledger)==len(common)==70
    assert result['common_endpoint_sensitivity']['gate']['outcomes_measured']
    assert set(result['horizons'])==set(map(str,HORIZONS))
    assert np.allclose(ledger.event_tracking_residual,0,atol=1e-14)
    assert np.allclose(ledger.incremental_tracking_residual,0,atol=1e-14)
    assert not any('MFE' in x or 'MAE' in x for x in ledger)
    for h in HORIZONS:
        assert result['horizons'][str(h)]['ETF_outcomes_read']
        assert set(result['horizons'][str(h)]['summary']['years'])==set(YEARS)


def test_interior_missing_or_zero_does_not_change_terminal_outcomes():
    p,t,ix,tape=fixture_data()
    _,audit,base,_=analyse(p,t,ix,tape,[])
    # Not an endpoint for either event nor either control at ANY frozen horizon.
    tape=tape.drop(t[50])
    tape.loc[t[51],'volume']=0
    _,audit2,modified,_=analyse(p,t,ix,tape,[])
    pd.testing.assert_frame_equal(audit,audit2)
    pd.testing.assert_frame_equal(base,modified)


@pytest.mark.parametrize('offset',[10,40,300,330])
def test_each_of_four_endpoints_is_required(offset):
    p,t,ix,tape=fixture_data(); p=p.iloc[:1]
    tape.loc[t[offset],'volume']=0
    a,px=endpoint_availability(p,t,tape,[])
    row=a.loc[a.horizon==30].iloc[0]
    assert not row.eligible and 'recorded_zero_volume' in row.reason


def test_missing_endpoint_is_not_filled_or_shifted():
    p,t,ix,tape=fixture_data(); p=p.iloc[:1]
    tape=tape.drop(t[40])
    a,px=endpoint_availability(p,t,tape,[])
    assert not a.loc[a.horizon==30,'eligible'].item()
    assert a.loc[a.horizon==15,'eligible'].item()
    assert np.isnan(px[40])
    assert a.loc[a.horizon==30,'event_exit_timestamp'].item()==t[40].isoformat()


def test_horizon_specific_cohorts_do_not_claim_common_sample():
    p,t,ix,tape=fixture_data()
    tape.loc[t[40],'volume']=0  # one of two 2021 events fails at h30: 50%<80%
    r,a,l,common=analyse(p,t,ix,tape,[])
    assert not r['horizons']['30']['ETF_outcomes_read']
    assert r['horizons']['15']['ETF_outcomes_read']
    assert 30 not in set(l.horizon)
    assert not r['common_endpoint_sensitivity']['gate']['pass']
    assert common.empty


def test_record_gate_failure_releases_no_ETF_returns():
    p,t,ix,tape=fixture_data()
    r,a,l,common=analyse(p,t,ix,tape,[],record_gate=False)
    assert l.empty and common.empty
    assert all(x['status']=='INSUFFICIENT_SOURCE_RECORD_COVERAGE' for x in r['horizons'].values())
    assert all('summary' not in x for x in r['horizons'].values())
    assert all('composition' in x for x in r['horizons'].values())


def test_gate_cannot_drop_a_missing_year():
    p,t,ix,tape=fixture_data()
    a,_=endpoint_availability(p,t,tape,[])
    one=a.loc[(a.horizon==30)&~a.event_day.str.startswith('2021')]
    assert not coverage_gate(one)['pass']


def test_gate_accepts_exact_80_percent_not_below():
    rows=[{'pair_id':f'{y}{k}','event_day':f'{y}-01-04','eligible':k<4} for y in YEARS for k in range(5)]
    a=pd.DataFrame(rows)
    assert coverage_gate(a)['pass']
    a.loc[0,'eligible']=False
    assert not coverage_gate(a)['pass']


def test_clock_crosses_lunch_without_using_wall_minutes():
    p,t,ix,tape=fixture_data(); p=p.iloc[:1].copy()
    p['event_entry_idx']=119
    a,_=endpoint_availability(p,t,tape,[])
    assert a.loc[a.horizon==1,'event_entry_timestamp'].item().endswith('11:30:00+08:00')
    assert a.loc[a.horizon==1,'event_exit_timestamp'].item().endswith('13:01:00+08:00')


def test_actions_exclude_only_crossings_for_the_relevant_horizon():
    p,t,ix,tape=fixture_data(); p=p.iloc[:1]
    a,_=endpoint_availability(p,t,tape,['2021-01-05'])
    assert a.loc[a.horizon==30,'eligible'].item()
    assert not a.loc[a.horizon==240,'eligible'].item()
    assert a.loc[a.horizon==240,'event_action_crossing'].item()
    assert not a.loc[a.horizon==240,'control_action_crossing'].item()


def test_prices_cannot_select_the_availability_sample():
    p,t,ix,tape=fixture_data(); a,_=endpoint_availability(p,t,tape,[])
    tape['close']=np.linspace(10,20,len(tape))
    b,_=endpoint_availability(p,t,tape,[])
    pd.testing.assert_frame_equal(a,b)


def test_synthetic_direction_and_paired_algebra():
    p,t,ix,tape=fixture_data(); p=p.iloc[:1].copy(); ep=tape.close.to_numpy()
    a=measure_endpoints(p,ix,ep,30)
    p['parent_direction']=-1; p['side']='SHORT'
    b=measure_endpoints(p,ix,ep,30)
    assert np.allclose(a.etf_event,-b.etf_event)
    assert np.allclose(a.etf_incremental,a.etf_event-a.etf_control)
    assert np.allclose(a.incremental_tracking_residual,a.etf_incremental-a.index_incremental)


def test_unsafe_identity_and_out_of_range_fail():
    p,t,ix,tape=fixture_data(); p=p.iloc[:1].copy()
    p['event_entry_idx']=len(t)-10
    with pytest.raises(EndpointError): endpoint_availability(p,t,tape,[])
    p['event_entry_idx']=10; p['side']='SHORT'
    with pytest.raises(EndpointError): endpoint_availability(p,t,tape,[])


def test_report_smoke_and_no_horizon_selection():
    p,t,ix,tape=fixture_data(); r,*_=analyse(p,t,ix,tape,[])
    text=report({'decision':'SYNTHETIC_TEST','code_commit':'test','carriers':{'512100.SH':r}})
    assert '240' in text and 'No MFE/MAE' in text
    assert 'PARTIAL_CARRIER_TRANSPORT' in text
    assert 'Retrospective' not in text or 'retrospective' in text
