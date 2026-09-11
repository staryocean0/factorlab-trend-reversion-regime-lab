import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from scipy.stats import t as student_t
from research.r1a_endpoint_robustness.study import (
    SPECS, HORIZONS, GAMMAS, RobustnessError,
    block_memberships, shared_adjacency, graph_inference,
    greedy_nonoverlap, missing_sensitivity, blob_guard,
)


def test_cross_role_shared_blocks_are_the_same_dependency():
    bounds = np.array([[0,1,20,21], [20,21,40,41], [60,61,80,81]])
    members = block_memberships(bounds,5,0)
    a, _ = shared_adjacency(members)
    assert a[0,1] and a[1,0]  # first control overlaps second event
    assert not a[0,2] and np.diag(a).all()


def test_shared_multiple_blocks_count_once():
    a, _ = shared_adjacency([{1,2}, {1,2}, {3}])
    assert a.dtype == bool and int(a.sum()) == 5
    u = np.array([1.,2.,3.])
    assert u @ (a @ u) == (1+2)**2+3**2


def test_crossing_block_boundary_keeps_both_blocks():
    members = block_memberships(np.array([[4,5,19,20]]),5,0)
    assert members == [{0,1,3,4}]
    shifted = block_memberships(np.array([[4,5,19,20]]),5,2)
    assert shifted == [{1,4}]


@pytest.mark.parametrize('bounds', [np.array([[2,1,3,4]]),np.array([[-1,1,3,4]]),np.array([[0.5,1,3,4]])])
def test_invalid_exposure_order_or_clock_rejected(bounds):
    with pytest.raises(RobustnessError): block_memberships(bounds,5,0)


def test_graph_meat_matches_bruteforce_pairwise_sum():
    rng=np.random.default_rng(42)
    members=[{int(i%40),int((i*7+13)%40)} for i in range(100)]
    x=rng.normal(size=100); u=x-x.mean()
    expected=sum(u[i]*u[j] for i in range(100) for j in range(100) if members[i]&members[j])
    result=graph_inference(x,members)
    assert result['graph_meat_bp2'] == pytest.approx(expected)


def test_repeated_block_scores_not_treated_as_independent_rows():
    effects=np.linspace(-3,3,60)
    x=np.repeat(effects,3); members=[{i//3} for i in range(180)]
    out=graph_inference(x,members)
    expected=(180/179)*(60/59)*sum((3*effects)**2)/(180**2)
    assert out['graph_variance_bp2'] == pytest.approx(expected)
    assert out['used_se_bp'] > 1.7*out['iid_se_bp']


def test_multiple_comparison_intervals_widen_not_shrink():
    x=np.linspace(-10,14,100); out=graph_inference(x,[{i} for i in range(100)])
    assert out['inference_status'].startswith('APPROXIMATE')
    assert out['family56_lo_bp'] < out['family14_lo_bp'] < out['point_lo_bp']
    assert out['family56_hi_bp'] > out['family14_hi_bp'] > out['point_hi_bp']
    expected=x.mean()-student_t.ppf(1-.05/28,out['df_heuristic'])*out['used_se_bp']
    assert out['family14_lo_bp'] == pytest.approx(expected)
    assert out['p_bonferroni56_approx'] >= out['p_bonferroni14_approx']


def test_nonpositive_graph_variance_not_silently_repaired_into_pass():
    x=np.r_[1.,-2.,1.,np.zeros(33)]
    members=[{0},{0,1},{1}]+[{i+2} for i in range(33)]
    out=graph_inference(x,members)
    assert out['graph_variance_bp2'] < 0
    assert out['inference_status'].startswith('UNQUANTIFIED')
    assert out['family14_lo_bp'] is None and out['used_se_bp'] is None


def test_too_few_calendar_units_blocks_inference():
    out=graph_inference(np.arange(60,dtype=float),[{i//3} for i in range(60)])
    assert out['occupied_blocks'] == 20
    assert out['inference_status'].startswith('UNQUANTIFIED')


def test_direction_reversal_mirrors_intervals():
    x=np.linspace(-5,8,100); m=[{i} for i in range(100)]
    a=graph_inference(x,m); b=graph_inference(-x,m)
    assert a['family14_lo_bp'] == pytest.approx(-b['family14_hi_bp'])
    assert a['p_bonferroni14_approx'] == pytest.approx(b['p_bonferroni14_approx'])


def test_greedy_interval_rule_checks_event_control_cross_roles():
    p=pd.DataFrame({'pair_id':['a','b','c','d'],'event_entry_idx':[0,10,20,100],
                    'control_entry_idx':[100,200,110,300]})
    selected=greedy_nonoverlap(p,15)
    assert selected == {'a'}  # b event, c control, d event overlap a


def test_greedy_does_not_read_outcomes_or_eligibility():
    p=pd.DataFrame({'pair_id':['a','b','c'],'event_entry_idx':[0,20,40],'control_entry_idx':[100,120,140]})
    before=greedy_nonoverlap(p,5)
    p['eligible']=[False,True,True]; p['return']=[-1e9,1e9,0.]
    assert greedy_nonoverlap(p,5) == before == {'a','b','c'}
    assert greedy_nonoverlap(p.iloc[::-1],5) == before


def test_missing_outcome_tipping_algebra_and_no_imputation():
    out=missing_sensitivity(np.array([2.,4.,6.,8.]),np.array([True,True,False,False]),np.array([3.,5.]),[-12,0,12])
    assert out['missing_etf_mean_to_zero_bp'] == -4
    assert out['observed_mean_tracking_residual_bp'] == 1
    assert out['gamma_to_zero_bp'] == -12
    assert out['scenarios'][0]['scenario_all_pair_mean_bp_NOT_ESTIMATE'] == 0
    assert out['scenarios'][1]['scenario_all_pair_mean_bp_NOT_ESTIMATE'] == 6
    assert out['missing_returns_imputed'] is False
    assert out['unconditional_mean_identified'] is False


def test_full_coverage_has_no_missing_tipping_point():
    out=missing_sensitivity(np.array([1.,3.]),np.array([True,True]),np.array([2.,4.]))
    assert out['n_missing'] == 0 and out['gamma_to_zero_bp'] is None
    assert {r['scenario_all_pair_mean_bp_NOT_ESTIMATE'] for r in out['scenarios']} == {3.}


def test_bad_missingness_alignment_rejected():
    with pytest.raises(RobustnessError):
        missing_sensitivity(np.array([1.,2.]),np.array([True,False]),np.array([3.,4.]))


def test_pinned_blob_detects_changes(tmp_path):
    import hashlib
    p=tmp_path/'x'; p.write_bytes(b'test\n')
    blob_guard(p,hashlib.sha1(b'blob 5\0test\n').hexdigest())
    p.write_bytes(b'changed')
    with pytest.raises(RobustnessError): blob_guard(p,hashlib.sha1(b'blob 5\0test\n').hexdigest())


def test_frozen_method_is_complete_and_no_horizon_winner():
    root=Path(__file__).resolve().parents[1]
    f=json.loads((root/'docs/governance/R1A_ENDPOINT_ROBUSTNESS_FREEZE@1.0.json').read_text())
    assert f['horizons'] == list(HORIZONS)
    assert f['dependence']['all_prespecified_specs'] == [list(x) for x in SPECS]
    assert f['missing_outcome_sensitivity']['gamma_grid_bp'] == list(GAMMAS)
    assert f['production_authority'] is False and f['holding_period_selected'] is False
    assert f['fresh_oos'] is False and f['BLACKBOX_query_count'] == 3
