from pathlib import Path
import hashlib
import ast
import numpy as np
import pandas as pd
import pytest
from research.etf_index_measurability.audit import (
    etf_clock,index_clock,consecutive,validity,observations,summarize,
    grid_departures,synthetic_equivalence,checked_path,assert_blob,TICK,
)


def fixture(clock=None):
    t = pd.DatetimeIndex(clock or ['2023-01-03 09:31','2023-01-03 09:32','2023-01-03 09:33']).tz_localize('Asia/Shanghai')
    ix = pd.DataFrame({'close':[100.]*len(t)},index=t)
    e = pd.DataFrame({'open':1.,'high':1.002,'low':.998,'close':1.,'volume':100.},index=t)
    return ix,e


def test_timezone_is_explicit():
    with pytest.raises(ValueError): etf_clock(pd.Series(['2023-01-03 09:31:00']))
    a=etf_clock(pd.Series(['2023-01-03 01:31:00+00:00']))
    b=etf_clock(pd.Series(['2023-01-03 09:31:00+08:00']))
    assert a.equals(b)


def test_inherited_index_encoding_not_silently_reinterpreted():
    f=pd.DataFrame({'timestamp':['2023-01-03T09:31:00Z'],'trading_day':['2023-01-03']})
    assert index_clock(f)[0].hour == 9
    f['trading_day']='2023-01-04'
    with pytest.raises(ValueError): index_clock(f)


@pytest.mark.parametrize('values',[
 ['2023-01-03 09:31:00+08:00']*2,
 ['2026-01-05 09:31:00+08:00'],
 ['2023-01-03 09:31:01+08:00'],
 ['2023-01-03 09:31:00.000000001+08:00'],
])
def test_bad_clock_rejected(values):
    with pytest.raises(ValueError): etf_clock(pd.Series(values))


def test_no_lunch_overnight_missing_minute_bridge():
    t=pd.DatetimeIndex(['2023-01-03 09:30','2023-01-03 09:31','2023-01-03 09:32',
       '2023-01-03 09:34','2023-01-03 11:30','2023-01-03 13:01',
       '2023-01-03 13:02','2023-01-04 09:31']).tz_localize('Asia/Shanghai')
    assert consecutive(t).tolist() == [False,False,True,False,False,False,True,False]


@pytest.mark.parametrize('col,value',[('close',0.),('open',np.inf),('volume',-1),('high',.8),('low',2.)])
def test_invalid_ohlcv(col,value):
    _,e=fixture(); e.iloc[1,e.columns.get_loc(col)]=value
    assert not validity(e)[0][1]


def test_missing_row_not_forward_filled():
    ix,e=fixture(); e=e.drop(e.index[1]); o=observations(ix,e,[])
    assert o.status.tolist() == ['POSITIVE_VOLUME','MISSING','POSITIVE_VOLUME']
    assert (o.comparison_status == 'ELIGIBLE').sum() == 0
    assert o.gap_abs_bp.isna().all()


def test_zero_volume_blocks_both_comparisons():
    ix,e=fixture(); e.iloc[1,e.columns.get_loc('volume')]=0
    o=observations(ix,e,[])
    assert (o.status == 'ZERO_VOLUME').sum()==1
    assert (o.comparison_status == 'ELIGIBLE').sum()==0
    assert o.zero_nonflat_bar.sum()==1


def test_positive_repeat_not_declared_stale():
    ix,e=fixture(); o=observations(ix,e,[])
    assert o.close_unchanged.dropna().tolist()==[1.,1.]
    assert 'stale' not in o.columns


def test_relative_change_not_level_price_difference():
    ix,e=fixture(); ix['close']=[100.,101.,102.]; e['close']=[1.,1.01,1.02]; e['high']=1.03
    o=observations(ix,e,[])
    assert np.allclose(o.gap_abs_bp.dropna(),0,atol=1e-10)
    assert np.isclose(o.tick_bp.iloc[1],10.)


def test_tick_and_trade_range_are_not_spread():
    ix,e=fixture(); e['close']=[1.,1.001,1.001]
    o=observations(ix,e,[])
    assert np.isclose(o.gap_abs_bp.iloc[1],1e4*np.log(1.001))
    assert 'spread' not in o.columns
    assert o.gap_reference_ticks.iloc[1]<1


def test_action_day_excluded_and_counted():
    ix,e=fixture(); o=observations(ix,e,['2023-01-03'])
    assert o.action_day.sum()==3
    assert (o.comparison_status=='DECLARED_ACTION_DAY').sum()==2
    assert o.gap_abs_bp.isna().all()


def test_invalid_index_not_measured():
    ix,e=fixture(); ix.iloc[1,0]=np.nan
    o=observations(ix,e,[])
    assert (o.comparison_status=='INVALID_INDEX_ENDPOINT').sum()==2


def test_summary_denominators_and_full_quantiles():
    ix,e=fixture(); e.iloc[1,e.columns.get_loc('volume')]=0
    o=observations(ix,e,[]); s=summarize(o,'512100.SH','000852.SH','ALL')
    assert s['index_records']==3 and s['zero_volume_records']==1
    assert s['record_coverage']==1 and np.isclose(s['positive_volume_coverage'],2/3)
    assert s['eligible_comparisons']==0 and s['gap_abs_bp_p95'] is None


def test_grid_departures_never_round_inputs():
    p=np.array([[1.,1.001,1.0005]])
    original=p.copy(); result=grid_departures(p)
    assert result.tolist()==[[False,False,True]]
    assert np.array_equal(p,original)


def test_source_bytes_and_path_guards(tmp_path):
    p=tmp_path/'test.csv'; raw=b'close\n1\n'; p.write_bytes(raw)
    spec={'path':'test.csv','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
    assert checked_path(tmp_path,spec)==p
    assert_blob(p,hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest())
    spec['sha256']='0'*64
    with pytest.raises(ValueError): checked_path(tmp_path,spec)
    spec['path']='../other.csv'
    with pytest.raises(ValueError): checked_path(tmp_path,spec)


def test_observational_equivalence_is_constructive():
    x=synthetic_equivalence()
    assert x['same_observed_ohlcv'] and x['synthetic_only']
    assert x['world_A_fair_close'] != x['world_B_fair_close']
    trades=np.array([[.999,1.001,.999],[1.001,.999,1.001],[.999,1.001,.999]])
    fair_A=np.ones_like(trades); trade_noise_A=trades-fair_A
    fair_B=trades.copy(); trade_noise_B=np.zeros_like(trades)
    def bars(prints):
        return np.column_stack([prints[:,0],prints.max(1),prints.min(1),prints[:,-1],np.full(3,300.)])
    assert np.allclose(bars(fair_A+trade_noise_A),bars(fair_B+trade_noise_B))
    assert np.allclose(bars(fair_A+trade_noise_A),x['observed_ohlcv'])


def test_no_fitting_strategy_or_prior_event_module_imports():
    p=Path(__file__).resolve().parents[1]/'research/etf_index_measurability/audit.py'
    tree=ast.parse(p.read_text())
    imported=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.ImportFrom): imported.append(node.module or '')
        if isinstance(node,ast.Import): imported.extend(n.name for n in node.names)
    assert not any(s.startswith(('research.r1','sklearn','statsmodels')) for s in imported)
    assert not any(isinstance(n,ast.Attribute) and n.attr in {'fit','fit_predict','polyfit','corr','autocorr'} for n in ast.walk(tree))
