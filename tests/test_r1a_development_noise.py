import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from research.r1a_development_noise import study as s


def pair_frame():
    return pd.DataFrame({'event_entry_idx':[0,10,20], 'control_entry_idx':[50,50,80],
                         'parent_direction':[1,1,-1]})


def test_exact_covariance_decomposition():
    e=np.array([1.,-2.,4.,8.]); c=np.array([3.,-1.,2.,5.])
    x=s.moments(e,c)
    assert np.isclose(x['difference_var_bp2'],np.var(e-c))
    assert np.isclose(x['event_share_of_difference']+x['control_share_of_difference']+x['covariance_share_of_difference'],1.)


def test_perfect_common_noise_cancels_without_infinite_ratio():
    x=s.moments(np.arange(20.),np.arange(20.))
    assert x['difference_var_bp2']==0
    assert x['cancellation_relative_to_marginal_sum']==1
    assert x['event_share_of_difference'] is None


def test_negative_covariance_is_retained():
    x=s.moments(np.arange(20.),-np.arange(20.))
    assert x['event_control_correlation']==-1
    assert x['cancellation_relative_to_marginal_sum']==-1
    assert x['covariance_share_of_difference']>0


def test_between_and_within_are_not_fitted_improvement():
    frame=pd.DataFrame({'event_bp':[1.,2.,10.,12.], 'control_bp':[2.,3.,8.,9.],
                        'calendar_year':['2019']*4,'parent_direction':[1]*4,'clock_bucket':[20,20,21,21]})
    rows=s.partition_moments(frame)
    a,b,c=rows
    for col in ['event_var_bp2','control_var_bp2','event_control_cov_bp2','difference_var_bp2']:
        assert np.isclose(a[col],b[col]+c[col])
    assert all(x['ex_post_not_causally_available'] for x in rows)


def test_singleton_strata_counted_not_dropped():
    f=pd.DataFrame({'event_bp':[1.,2.,3.], 'control_bp':[4.,5.,7.],
                    'calendar_year':['2020']*3,'parent_direction':[1]*3,'clock_bucket':[1,2,3]})
    a,b,c=s.partition_moments(f)
    assert a['singleton_strata']==3 and b['difference_var_bp2']==0
    assert np.isclose(a['difference_var_bp2'],c['difference_var_bp2'])


def test_clock_telescopes_simple_not_log_and_keeps_no_exposure_days():
    p=100*np.exp(np.arange(140)*.0003)
    days=np.repeat(np.arange(7),20); dates=[f'2020-01-{i+1:02d}' for i in range(7)]
    f=pair_frame(); h=5
    info,daily,lags=s.clock_accounting(f,p,days,dates,h,True)
    e=f.event_entry_idx.to_numpy(); c=f.control_entry_idx.to_numpy(); d=f.parent_direction.to_numpy()
    expected=np.mean(d*(p[e+h]/p[e]-p[c+h]/p[c])*1e4)
    assert np.isclose(daily.difference_contribution_bp.mean(),expected,atol=1e-9)
    assert len(daily)==7
    assert (daily.loc[daily.day=='2020-01-07',['event_contribution_bp','control_contribution_bp']]==0).all().all()
    assert info['maximum_control_reuse']==2
    assert info['control_exact_reuse_excess_energy']>0
    for lag in lags:
        assert np.isclose(lag['difference_lag_product_bp2'],lag['event_lag_product_bp2']+lag['control_lag_product_bp2']-lag['event_control_lag_product_bp2']-lag['control_event_lag_product_bp2'])
        assert not lag['mean_variance_estimator']


def test_identical_clock_legs_cancel_exactly():
    f=pair_frame(); f['control_entry_idx']=f.event_entry_idx
    p=100+np.sin(np.arange(140))
    info,daily,_=s.clock_accounting(f,p,np.repeat(np.arange(7),20),list(map(str,range(7))),5,True)
    assert np.allclose(daily.difference_contribution_bp,0)
    assert np.isclose(info['primitive_covariance_cancellation_ratio_ASSUMPTION'],1)
    assert np.isclose(info['minute_absolute_exposure_cancellation'],1)


def test_separate_times_are_not_automatically_shared_shocks():
    p=np.linspace(100,120,140); f=pair_frame()
    info,_,_=s.clock_accounting(f,p,np.repeat(np.arange(7),20),list(map(str,range(7))),5,True)
    assert info['within_pair_overlap_fraction']==0
    assert info['primitive_covariance_cancellation_ratio_ASSUMPTION']==0
    assert info['minute_absolute_exposure_cancellation']==0


def test_independent_control_model_uses_unequal_marginal_scales():
    rows=s.scale_scenarios(9.,1.)
    r=next(x for x in rows if x['K']=='infinity' and x['control_correlation_ASSUMED']==0)
    assert np.isclose(r['variance_ratio_to_independent_one_control'],.9)
    r=next(x for x in s.scale_scenarios(1.,1.) if x['K']=='infinity' and x['control_correlation_ASSUMED']==0)
    assert r['variance_ratio_to_independent_one_control']==.5


@pytest.mark.parametrize('e,c', [([],[]),([1.,np.nan],[2.,3.]),([1.],[1.,2.])])
def test_invalid_moments_fail(e,c):
    with pytest.raises(ValueError): s.moments(e,c)


def test_outside_clock_and_invalid_direction_fail():
    with pytest.raises(ValueError): s.weights(np.ones(10),np.array([8]),np.array([1]),5)
    with pytest.raises(ValueError): s.weights(np.ones(10),np.array([0]),np.array([0]),5)


def test_future_file_is_not_opened(tmp_path,monkeypatch):
    opened=[]
    monkeypatch.setattr(s.pq,'read_table',lambda *a,**kw:opened.append(a))
    m={'files':[{'symbol':'000852.SH','frequency':'1m','first_day':'2021-01-04','last_day':'2021-12-31','path':'future.parquet'}]}
    with pytest.raises(ValueError,match='no original'): s.load_development(tmp_path,'000852.SH',m)
    assert opened==[]


def test_mixed_role_file_rejected_before_read(tmp_path,monkeypatch):
    opened=[]
    monkeypatch.setattr(s.pq,'read_table',lambda *a,**kw:opened.append(a))
    m={'files':[{'symbol':'000852.SH','frequency':'1m','first_day':'2020-01-01','last_day':'2021-01-05','path':'mixed.parquet'}]}
    with pytest.raises(ValueError,match='mixed-role'): s.load_development(tmp_path,'000852.SH',m)
    assert opened==[]


def test_freeze_preserves_development_and_no_confirmation():
    root=Path(__file__).resolve().parents[1]
    x=json.loads((root/s.FREEZE).read_text())
    assert x['horizons']==list(s.HORIZONS)
    assert all(v['end']=='2020-12-31' for v in x['scope'].values())
    assert not x['new_confirmatory_outcomes_authorized'] and not x['production_authority']
    assert x['BLACKBOX_query_count']==3
