"""Synthetic tests only; no market returns or external data are required."""
import inspect
import numpy as np
import pandas as pd
import pytest
from research.r1a_control_design.core import (
    FEATURES, STAGES, SPAN, allocate, check_features, prefix_scale,
    free_intervals, overlap_pairs, incidence, geometry, coverage_balance,
)
from research.r1a_control_design.study import allowed_tables, verify_event_identity


def table(indices, values=None, directions=None, year='2020'):
    values=[0.0]*len(indices) if values is None else values
    directions=[1]*len(indices) if directions is None else directions
    return pd.DataFrame([{'symbol':'000852.SH','entry_idx':i,'day':year+'-06-01',
      'calendar_year':year,'parent_direction':d,'clock_bucket':20,
      **dict(zip(FEATURES,[float(x),0.0,0.0,0.0]))}
      for i,x,d in zip(indices,values,directions)],columns=['symbol','entry_idx','day','calendar_year','parent_direction','clock_bucket',*FEATURES])


def primary(frame):
    return frame.loc[frame.stage==STAGES[2]].reset_index(drop=True)


@pytest.mark.parametrize('column',['return','close','PnL','severity','outcome','future_volatility'])
def test_allocator_refuses_any_extra_column(column):
    e=table([1000]);c=table([10]);c[column]=0
    with pytest.raises(ValueError,match='only accepts'):
        allocate(e,c)


def test_allocator_interface_has_no_price_or_outcome_argument():
    assert list(inspect.signature(allocate).parameters)==['events','controls']


def test_control_whole_path_must_finish_before_confirmation():
    a,n=allocate(table([500]),table([259,260]))
    assert primary(a).control_entry_idx.item()==259
    assert n.maximum_control_source_idx.item()==259
    assert n.information_cutoff_idx.item()==499


def test_only_unmatured_controls_remain_unmatched():
    a,_=allocate(table([500]),table([260]))
    assert len(a)==3 and not a.matched.any()
    assert set(a.reason)=={'NO_MATURE_EXACT_STRATUM'}


def test_future_normalization_and_future_events_cannot_change_prefix():
    e=table([1000,1100],[1.,1.]);c=table([10,300,600],[0.,1.,2.])
    a,n=allocate(e,c)
    full=pd.concat([c,table([1500,2000],[1e12,-1e12])],ignore_index=True)
    ef=pd.concat([e,table([3000],[2.])],ignore_index=True)
    b,m=allocate(ef,full)
    pd.testing.assert_frame_equal(a,b.loc[b.event_entry_idx<=1100].reset_index(drop=True))
    pd.testing.assert_frame_equal(n,m.loc[m.event_entry_idx<=1100].reset_index(drop=True))


def test_future_year_does_not_supply_a_warmup_or_change_scale():
    a,_=allocate(table([1000]),table([10],year='2019'))
    assert not a.matched.any()


def test_empty_pool_preserves_every_event():
    a,_=allocate(table([1000,1100]),table([]))
    assert len(a)==6 and not a.matched.any()
    c,b=coverage_balance(a)
    assert (c.coverage==0).all()
    assert not b.balance_pass.any()


def test_component_caliper_is_inclusive_and_not_relaxed():
    a,_=allocate(table([1000],[.5]),table([10]))
    assert primary(a).matched.item()
    b,_=allocate(table([1000],[.50001]),table([10]))
    assert b.loc[b.stage==STAGES[0],'matched'].item()
    assert not primary(b).matched.item()
    assert primary(b).reason.item()=='NO_CALIPER_SUPPORT'


def test_exclusive_scheme_does_not_reuse_identical_or_overlapping_intervals():
    a,_=allocate(table([1000,1100,1200]),table([10,20,300,600]))
    p=primary(a)
    assert p.control_entry_idx.tolist()==[10,300,600]
    assert a.loc[a.stage==STAGES[1],'control_entry_idx'].tolist()==[10,10,10]
    assert overlap_pairs(p.control_entry_idx.to_numpy(),SPAN)==0


def test_capacity_loss_is_not_hidden_as_a_missing_event():
    a,_=allocate(table([1000,1001]),table([10,20]))
    p=primary(a)
    assert len(p)==2 and p.matched.tolist()==[True,False]
    assert p.reason.iloc[1]=='INTERVAL_CAPACITY_BLOCKED'
    assert p.caliper_candidates.iloc[1]==2
    assert p.unreserved_caliper_candidates.iloc[1]==0


def test_interval_capacity_is_shared_across_directions():
    a,_=allocate(table([1000,1001],directions=[1,-1]),table([1,20,500],directions=[1,-1,-1]))
    assert primary(a).control_entry_idx.tolist()==[1,500]


def test_touching_price_endpoints_are_blocked():
    assert free_intervals(np.array([100,340,341,500]),[100]).tolist()==[False,False,True,True]
    assert free_intervals(np.array([100,101]),[341]).tolist()==[True,False]


def test_ties_choose_earliest_original_control_index():
    a,_=allocate(table([1000]),table([600,10,300]))
    assert primary(a).control_entry_idx.item()==10


def test_degenerate_prefix_scaling_uses_declared_fallback():
    cen,scale=prefix_scale(np.array([[1.,2.,3.,4.],[1.,2.,3.,4.]]))
    assert np.array_equal(scale,np.ones(4))
    assert np.array_equal(cen,[1,2,3,4])


@pytest.mark.parametrize('mutation',['duplicate','nan','bad_direction','fractional_clock'])
def test_invalid_feature_identities_fail_closed(mutation):
    e=table([1000]);c=table([10])
    if mutation=='duplicate':c=pd.concat([c,c])
    if mutation=='nan':c.loc[0,FEATURES[0]]=np.nan
    if mutation=='bad_direction':c.loc[0,'parent_direction']=0
    if mutation=='fractional_clock':c['entry_idx']=10.5
    with pytest.raises(ValueError):allocate(e,c)


def test_disjoint_incidence_energy_has_no_reuse_inflation():
    days=np.arange(2000)//240
    g=geometry(np.array([1000,1500]),np.array([10,400]),np.array([1,-1]),days,30)
    assert g['control_unit_energy']==60
    assert g['control_unit_energy_ratio_NOT_variance_effect']==1
    assert g['control_increment_minutes_used_more_than_once']==0


def test_reuse_raises_unit_energy_without_claiming_real_variance():
    days=np.arange(2000)//240
    g=geometry(np.array([1000,1500]),np.array([10,10]),np.array([1,1]),days,30)
    assert g['control_unit_energy_ratio_NOT_variance_effect']==2
    assert g['maximum_exact_reuse']==2
    assert 'variance' not in set(g)-{'control_unit_energy_ratio_NOT_variance_effect'}


def test_incidence_excludes_entry_increment_and_includes_exit():
    x=incidence(np.array([10]),np.array([-1]),5,100)
    assert x[10]==0 and np.all(x[11:16]==-1) and x[16]==0


def test_variance_and_coverage_denominators_do_not_hide_unmatched_events():
    a,_=allocate(table([1000,1100],[0.,3.]),table([10]))
    c,b=coverage_balance(a)
    p=c.loc[(c.stage==STAGES[2])&(c.group=='POOLED')].iloc[0]
    assert p.original_events==2 and p.matched_events==1 and p.coverage==.5
    q=b.loc[(b.stage==STAGES[2])&(b.group=='POOLED')&(b.feature==FEATURES[0])].iloc[0]
    assert q.retention_shift_SMD==-1


def test_original_event_identity_verification_rejects_new_population():
    e=table([1000])
    old=pd.DataFrame({'event_entry_idx':[999],'event_day':['2020-06-01'],'parent_direction':[1],
                     'clock_bucket':[20],**{'event_'+f:[0.] for f in FEATURES}})
    with pytest.raises(ValueError,match='universe'):
        verify_event_identity(e,old)
