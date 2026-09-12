import copy
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from research.etf_source_repair.audit import effective_actions, crossing, window_audit, H
from research.r1a_carrier_transport.endpoint_diagnostic import endpoint_availability


def synthetic_inputs():
    times=pd.DatetimeIndex([])
    for day in ('2022-09-01','2022-09-02','2022-09-05','2022-09-06'):
        d=pd.date_range(day+' 09:31',periods=120,freq='min',tz='Asia/Shanghai').append(pd.date_range(day+' 13:01',periods=120,freq='min',tz='Asia/Shanghai'))
        times=d if len(times)==0 else times.append(d)
    tape=pd.DataFrame({'close':10.0,'volume':100.0},index=times)
    pairs=pd.DataFrame([{'pair_id':'synthetic','symbol':'000852.SH','event_entry_idx':239,'control_entry_idx':480,'event_day':'2022-09-01','control_day':'2022-09-05','side':'LONG','parent_direction':1}])
    action={'effective_date':'2022-09-02','first_resumed_trading_date':'2022-09-05'}
    return times,tape,pairs,action


def test_cancelled_proposal_not_effective():
    overlay={'carriers':{'X':{'known_effective_actions':[{'status':'CONFIRMED_ACTION','effective_date':'2022-09-02'}],'cancelled_proposals':[{'proposed_effective_date':'2022-08-03','status':'CANCELLED_NOT_APPLIED'}]}}}
    assert effective_actions(overlay,'X')==['2022-09-02']


@pytest.mark.parametrize('bad',['PROPOSED','CANCELLED_NOT_APPLIED','UNKNOWN'])
def test_unconfirmed_event_never_applied(bad):
    o={'carriers':{'X':{'known_effective_actions':[{'status':bad,'effective_date':'2022-09-02'}]}}}
    with pytest.raises(ValueError): effective_actions(o,'X')


@pytest.mark.parametrize('date',['2020-01-01','2026-01-01','2022-13-01'])
def test_action_window_and_calendar_validation(date):
    o={'carriers':{'X':{'known_effective_actions':[{'status':'CONFIRMED_ACTION','effective_date':date}]}}}
    with pytest.raises(ValueError): effective_actions(o,'X')


def test_duplicate_effective_dates_rejected():
    a={'status':'CONFIRMED_ACTION','effective_date':'2022-09-02'}
    with pytest.raises(ValueError): effective_actions({'carriers':{'X':{'known_effective_actions':[a,a]}}},'X')


def test_entry_on_ex_date_is_not_crossing():
    assert crossing(['2022-09-01','2022-09-02'],['2022-09-02','2022-09-05'],'2022-09-02').tolist()==[True,False]


def test_suspended_day_not_filled_and_old_exclusion_survives():
    t,f,p,a=synthetic_inputs(); f=f.loc[f.index.strftime('%Y-%m-%d')!='2022-09-02']
    old,px=endpoint_availability(p,t,f,[]); new,_=endpoint_availability(p,t,f,['2022-09-02'])
    w=window_audit(old,new,[a])
    assert len(w)==7 and not w.old_eligible.any() and not w.new_eligible.any()
    assert w.new_action_crossing.all() and w.reason_changed.all()
    assert not w.unit_bridge_crossing.any() and np.isnan(px[240:480]).all()
    assert not w.membership_changed.any()


def test_real_included_action_crossing_would_be_detected():
    t,f,p,a=synthetic_inputs()
    old,_=endpoint_availability(p,t,f,[]); new,_=endpoint_availability(p,t,f,['2022-09-02'])
    w=window_audit(old,new,[a])
    assert w.old_eligible.all() and not w.new_eligible.any() and w.membership_changed.all()


def test_action_in_control_leg_is_not_missed():
    t,f,p,a=synthetic_inputs(); p.event_entry_idx=480; p.control_entry_idx=239
    old,_=endpoint_availability(p,t,f,[]); new,_=endpoint_availability(p,t,f,['2022-09-02'])
    w=window_audit(old,new,[a]); assert w.new_action_crossing.all() and w.membership_changed.all()


def test_same_day_after_action_is_retained():
    t,f,p,a=synthetic_inputs(); p.event_entry_idx=480
    old,_=endpoint_availability(p,t,f,[]); new,_=endpoint_availability(p,t,f,['2022-09-02'])
    w=window_audit(old,new,[a]); assert w.new_eligible.all() and not w.new_action_crossing.any()


def test_duplicate_pair_horizon_rejected():
    t,f,p,a=synthetic_inputs(); old,_=endpoint_availability(p,t,f,[])
    with pytest.raises(ValueError): window_audit(pd.concat([old,old]),pd.concat([old,old]),[a])


def test_added_action_cannot_create_a_new_eligible_outcome():
    t,f,p,a=synthetic_inputs(); old,_=endpoint_availability(p,t,f,['2022-09-02']); new,_=endpoint_availability(p,t,f,[])
    with pytest.raises(ValueError): window_audit(old,new,[a])


def test_no_action_yields_exact_same_membership():
    t,f,p,a=synthetic_inputs(); old,_=endpoint_availability(p,t,f,[])
    w=window_audit(old,old,[]); assert not w.membership_changed.any() and not w.reason_changed.any()


def test_source_overlay_never_certifies_complete_history():
    root=Path(__file__).resolve().parents[1]
    o=json.loads((root/'docs/governance/ETF_ACTION_SOURCE_OVERLAY_V2_20260912.json').read_text())
    assert o['complete_corporate_action_calendar_certified'] is False
    assert o['microstructure_source_admitted'] is False
    assert effective_actions(o,'512100.SH')==['2022-09-02','2025-01-15']
    assert effective_actions(o,'588000.SH')==[]
    a=o['carriers']['512100.SH']['known_effective_actions'][0]
    assert a['new_shares_per_old_share']==0.36555
    assert o['carriers']['512100.SH']['cancelled_proposals'][0]['effective_factor_applied']==1.0


def test_auditor_does_not_fit_or_generate_strategy_signals():
    import ast
    root=Path(__file__).resolve().parents[1]
    tree=ast.parse((root/'research/etf_source_repair/audit.py').read_text())
    denied={'fit','fit_ridge','build_r1_events_and_controls','analyse','measure','measure_endpoints','target'}
    calls={n.func.attr if isinstance(n.func,ast.Attribute) else n.func.id for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,(ast.Attribute,ast.Name))}
    assert not calls.intersection(denied)
    assert H==(1,5,15,30,60,120,240)
